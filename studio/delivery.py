"""Guarded single-platform Buffer queueing. Never enabled by the draft workflow.

Only a durable journal prevents retries across processes. Keep its SQLite file on
persistent storage, back it up, and never start multiple independent journals.
"""
import json
import os
import re
import sqlite3
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from studio.core import ACCOUNTS, media_assets, now, require_approval, validate_post
from studio.publications import content_key

API = 'https://api.buffer.com'
CREATE = '''mutation CreatePost($input: CreatePostInput!) {
 createPost(input: $input) {
  ... on PostActionSuccess { post { id text dueAt } }
  ... on MutationError { message }
 }
}'''


def graphql(query, variables, token):
    request = Request(API, data=json.dumps({'query': query, 'variables': variables}).encode(),
                      headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, method='POST')
    # No retries. A mutation timeout is an unknown result, not evidence of failure.
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('errors') or not isinstance(result.get('data'), dict):
        raise RuntimeError('Buffer request returned an error; inspect provider before retrying')
    return result['data']


def canonical_account(url):
    parsed = urlparse(url or '')
    host = parsed.netloc.lower().removeprefix('www.')
    if host == 'twitter.com':
        host = 'x.com'
    return host, parsed.path.rstrip('/').lower(), parsed.query


def verify_channel(platform, channel_id, organization_id, token, transport=graphql):
    query = '''query Channels($input: ChannelsInput!) {
      channels(input: $input) {
        id service externalLink isDisconnected isLocked isQueuePaused
      }
    }'''
    channels = transport(query, {'input': {'organizationId': organization_id}}, token).get('channels', [])
    channel = next((c for c in channels if c.get('id') == channel_id), None)
    if not channel or channel.get('service') != platform:
        raise ValueError('Buffer channel is missing or belongs to a different platform')
    if canonical_account(channel.get('externalLink')) != canonical_account(ACCOUNTS[platform]):
        raise ValueError('Buffer account URL cannot be verified against the approved target')
    if any(channel.get(k, True) for k in ('isDisconnected', 'isLocked', 'isQueuePaused')):
        raise ValueError('Channel is disconnected, locked, paused, or status is unavailable')


def verify_public_image(post):
    """Verify every ordered asset and PDF thumbnail, retaining the legacy entrypoint."""
    assets = media_assets(post)
    for asset in assets:
        files = [asset]
        if asset['type'] == 'document':
            files.append(dict(asset['thumbnail'], type='image'))
        for item in files:
            url = item.get('url') or ''
            extension, mime, limit = ('pdf', 'application/pdf', 100) if item['type'] == 'document' else ('png', 'image/png', 10)
            pattern = rf'https://raw\.githubusercontent\.com/nazakataleofficial-coder/kreafy-content-agent/[0-9a-f]{{40}}/[A-Za-z0-9_./-]+\.{extension}'
            if not re.fullmatch(pattern, url) or '..' in urlparse(url).path.split('/'):
                raise ValueError('Asset URL must be pinned to an immutable repository commit')
            request = Request(url, headers={'User-Agent': 'KreafyContentStudio/1.0'})
            with urlopen(request, timeout=30) as response:
                if response.geturl() != url or response.headers.get_content_type() not in (mime, 'application/octet-stream'):
                    raise ValueError('Unexpected asset response or redirect')
                blob = response.read(limit * 1024 * 1024 + 1)
            import hashlib
            if len(blob) > limit * 1024 * 1024 or hashlib.sha256(blob).hexdigest() != item['sha256']:
                raise ValueError('Public asset differs from the approved file')


def build_payload(post, platform, channel_id):
    mode = post.get('delivery_mode', 'addToQueue')
    if mode not in ('addToQueue', 'shareNow', 'customScheduled'):
        raise ValueError('Unsupported delivery mode')
    payload = {'channelId': channel_id, 'text': post['caption'], 'needsApproval': False,
               'schedulingType': 'automatic', 'mode': mode, 'assets': []}
    if mode == 'customScheduled':
        from studio.publications import timestamp
        if timestamp(post.get('due_at')) <= timestamp(now()):
            raise ValueError('Scheduled publication requires a future timezone-aware due_at')
        payload['dueAt'] = post['due_at']
    elif post.get('due_at') is not None:
        raise ValueError('due_at is only valid for customScheduled delivery')
    for asset in media_assets(post):
        if asset['type'] == 'document':
            payload['assets'].append({'document': {'url': asset['url'], 'title': asset['title'],
                                                  'thumbnailUrl': asset['thumbnail']['url']}})
        else:
            payload['assets'].append({'image': {'url': asset['url']}})
    if platform == 'instagram':
        payload['metadata'] = {'instagram': {'type': 'post', 'shouldShareToFeed': True}}
    return payload


def check_remote_duplicates(post, channel_id, organization_id, token, transport=graphql):
    query = '''query DuplicateCheck($input: PostsInput!, $after: String) {
      posts(input: $input, first: 100, after: $after) {
        edges { node { id channelId text status assets { source } } }
        pageInfo { hasNextPage endCursor }
      }
    }'''
    urls = [a['url'] for a in media_assets(post)]
    after, seen = None, set()
    # Fail closed on a larger history; never silently skip unchecked pages.
    for _ in range(10):
        data = transport(query, {'input': {'organizationId': organization_id,
                          'filter': {'channelIds': [channel_id]}}, 'after': after}, token).get('posts')
        if not isinstance(data, dict) or not isinstance(data.get('edges'), list):
            raise ValueError('Buffer duplicate scan returned incomplete data')
        for edge in data['edges']:
            item = edge.get('node') or {}
            if item.get('channelId') != channel_id:
                raise ValueError('Buffer duplicate scan returned an unexpected channel')
            if item.get('text') == post['caption'] or [a.get('source') for a in item.get('assets', [])] == urls:
                raise ValueError('Possible duplicate in Buffer; inspect the existing post before sending')
        page = data.get('pageInfo') or {}
        if page.get('hasNextPage') is False:
            return
        after = page.get('endCursor')
        if page.get('hasNextPage') is not True or not after or after in seen:
            raise ValueError('Buffer duplicate scan pagination is incomplete')
        seen.add(after)
    raise ValueError('Buffer history exceeds 1000 posts; duplicate review required')


def resolve_organization(platform, channel_id, token, transport=graphql):
    organizations = transport('query Account { account { organizations { id } } }', {}, token).get('account', {}).get('organizations', [])
    if not organizations or len(organizations) > 5:
        raise ValueError('Cannot identify the existing Buffer organization')
    matches = []
    for org in organizations:
        try:
            verify_channel(platform, channel_id, org['id'], token, transport)
            matches.append(org['id'])
        except ValueError:
            continue
    if len(matches) != 1:
        raise ValueError('Expected exactly one ready organization for the approved account')
    return matches[0]


def preflight_post(post, platform, channel_id, organization_id, token,
                   transport=graphql, image_check=verify_public_image):
    if platform == 'facebook':
        raise ValueError('This Facebook professional profile requires native posting; no Buffer fallback')
    validate_post(post, platform)
    require_approval(post)
    payload = build_payload(post, platform, channel_id)
    if not all((channel_id, token)):
        raise ValueError('Existing authorized Buffer connection is not configured')
    organization_id = organization_id or resolve_organization(platform, channel_id, token, transport)
    verify_channel(platform, channel_id, organization_id, token, transport)
    image_check(post)
    check_remote_duplicates(post, channel_id, organization_id, token, transport)
    return payload


def queue_post(post, platform, journal, channel_id, organization_id, token,
               transport=graphql, image_check=verify_public_image):
    if os.environ.get('KREAFY_PUBLISH_ENABLED') != 'true':
        raise ValueError('Publishing is disabled; prepare and approve previews first')
    if platform == 'facebook':
        raise ValueError('This Facebook professional profile requires native posting; no Buffer fallback')
    validate_post(post, platform)
    require_approval(post)
    payload = build_payload(post, platform, channel_id)
    if not all((channel_id, token)):
        raise ValueError('Existing authorized Buffer connection is not configured')
    # Bind duplicate prevention to target and content, not approval timestamps or
    # filenames. Altering a planned date cannot make the same post publish again.
    key = content_key(post)
    from pathlib import Path
    Path(journal).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(journal, timeout=30) as db:
        db.execute('CREATE TABLE IF NOT EXISTS delivery (key TEXT PRIMARY KEY, state TEXT NOT NULL, receipt TEXT NOT NULL)')
        if db.execute('SELECT 1 FROM delivery WHERE key=?', (key,)).fetchone():
            raise ValueError('Already attempted: inspect the durable receipt; never automatically repost')
        payload = preflight_post(post, platform, channel_id, organization_id, token, transport, image_check)
        try:
            with db:
                db.execute('INSERT INTO delivery VALUES (?, ?, ?)', (key, 'attempting', json.dumps({
                    'attempted_at': now(), 'platform': platform, 'channel_id': channel_id,
                    'account_url': post['account_url'], 'delivery_mode': payload['mode']})))
        except sqlite3.IntegrityError as exc:
            raise ValueError('Already attempted: inspect the durable receipt; never automatically repost') from exc
        try:
            result = transport(CREATE, {'input': payload}, token).get('createPost', {})
            provider_post = result.get('post') or {}
            if result.get('message') or not provider_post.get('id'):
                raise RuntimeError('No confirmed Buffer post ID')
            state = 'submitted' if payload['mode'] == 'shareNow' else 'queued'
            receipt = {'state': state, 'platform': platform, 'account_url': post['account_url'],
                       'channel_id': channel_id, 'delivery_mode': payload['mode'],
                       'provider_post_id': provider_post['id'], 'due_at': provider_post.get('dueAt'),
                       'queued_at': now(), 'published_at': None, 'public_post_url': None,
                       'note': 'Accepted by Buffer, not yet verified live. Refresh provider status before reporting publication.'}
        except Exception:
            receipt = {'state': 'unknown', 'platform': platform, 'observed_at': now(),
                       'channel_id': channel_id, 'account_url': post['account_url'],
                       'note': 'Request may have succeeded. Inspect Buffer and the account before any further action.'}
            with db:
                db.execute('UPDATE delivery SET state=?,receipt=? WHERE key=?', ('unknown', json.dumps(receipt), key))
            raise RuntimeError('Delivery result uncertain; journal retained and automatic retry blocked') from None
        with db:
            db.execute('UPDATE delivery SET state=?,receipt=? WHERE key=?', (state, json.dumps(receipt), key))
        return receipt


def refresh_post(post, platform, journal, token, transport=graphql):
    """Read Buffer status. Provider evidence never substitutes for native visual QA."""
    from pathlib import Path
    from studio.publications import timestamp, validate_url
    validate_post(post, platform, check_assets=False)
    require_approval(post)
    if not token or not Path(journal).is_file():
        raise ValueError('Existing token and durable delivery journal are required')
    key = content_key(post)
    with sqlite3.connect(journal, timeout=30) as db:
        row = db.execute('SELECT state,receipt FROM delivery WHERE key=?', (key,)).fetchone()
        if not row:
            raise ValueError('No previous delivery to refresh')
        saved = json.loads(row[1])
        if row[0] == 'published':
            return saved
        provider_id = saved.get('provider_post_id')
        if not provider_id or not saved.get('channel_id'):
            raise ValueError('No known Buffer post/channel ID; reconcile manually, never resend')
        query = '''query PublicationStatus($input: PostInput!) {
          post(input: $input) {
            id channelId text status sentAt externalLink
            channel { service externalLink }
            assets { source }
          }
        }'''
        item = transport(query, {'input': {'id': provider_id}}, token).get('post') or {}
        channel = item.get('channel') or {}
        if (item.get('id') != provider_id or item.get('channelId') != saved['channel_id'] or
                channel.get('service') != platform or
                canonical_account(channel.get('externalLink')) != canonical_account(ACCOUNTS[platform])):
            raise ValueError('Returned Buffer post does not match the approved account')
        status = item.get('status')
        if status not in ('draft', 'error', 'needs_approval', 'scheduled', 'sending', 'sent'):
            raise ValueError('Unknown Buffer post status; original receipt retained')
        observed = now()
        match = (item.get('text') == post['caption'] and
                 [a.get('source') for a in item.get('assets', [])] == [a.get('url') for a in media_assets(post)])
        url = item.get('externalLink')
        if url:
            parsed = urlparse(url)
            hosts = {'twitter': ('x.com', 'www.x.com', 'twitter.com', 'www.twitter.com'),
                     'instagram': ('instagram.com', 'www.instagram.com'),
                     'linkedin': ('linkedin.com', 'www.linkedin.com')}
            if parsed.scheme != 'https' or parsed.netloc not in hosts.get(platform, ()):
                raise ValueError('Buffer returned an unexpected public URL')
            canonical_host = {'twitter': 'x.com', 'instagram': 'www.instagram.com', 'linkedin': 'www.linkedin.com'}[platform]
            validate_url(platform, parsed._replace(netloc=canonical_host, query='', fragment='').geturl())
        sent_at = item.get('sentAt')
        if sent_at and timestamp(sent_at) > timestamp(observed):
            raise ValueError('Buffer publication timestamp is in the future')
        state = ('provider_sent' if status == 'sent' and match and url and sent_at else
                 'needs_review' if status == 'sent' or not match else
                 'failed' if status == 'error' else 'queued' if status == 'scheduled' else status)
        updated = dict(saved, state=state, provider_status=status, observed_at=observed,
                       provider_content_matches=match, provider_post_url=url,
                       provider_sent_at=sent_at, metrics=None,
                       verification_method='buffer_api_only',
                       note='Buffer evidence only. Native account appearance has not been visually verified.')
        # A concurrent operator may have reconciled this post while the GET ran.
        with db:
            cursor = db.execute('UPDATE delivery SET state=?,receipt=? WHERE key=? AND receipt=?',
                                (state, json.dumps(updated), key, row[1]))
            if cursor.rowcount != 1:
                raise ValueError('Receipt changed during refresh; re-read it before continuing')
        return updated
