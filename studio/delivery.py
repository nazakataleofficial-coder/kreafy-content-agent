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

from studio.core import ACCOUNTS, now, require_approval, validate_post
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
    url = post.get('public_image_url') or ''
    # Fail closed: only repository images pinned to a full commit SHA are accepted.
    pattern = r'https://raw\.githubusercontent\.com/nazakataleofficial-coder/kreafy-content-agent/[0-9a-f]{40}/[^?#]+\.png'
    if not re.fullmatch(pattern, url):
        raise ValueError('Image URL must be a public PNG pinned to an immutable repository commit')
    request = Request(url, headers={'User-Agent': 'KreafyContentStudio/1.0'})
    with urlopen(request, timeout=30) as response:
        if response.geturl() != url or response.headers.get_content_type() != 'image/png':
            raise ValueError('Unexpected image response or redirect')
        blob = response.read(10 * 1024 * 1024 + 1)
    import hashlib
    if len(blob) > 10 * 1024 * 1024 or hashlib.sha256(blob).hexdigest() != post['image_sha256']:
        raise ValueError('Public image differs from the approved image')


def queue_post(post, platform, journal, channel_id, organization_id, token,
               transport=graphql, image_check=verify_public_image):
    if os.environ.get('KREAFY_PUBLISH_ENABLED') != 'true':
        raise ValueError('Publishing is disabled; prepare and approve previews first')
    if platform == 'facebook':
        raise ValueError('This Facebook professional profile requires native posting; no Buffer fallback')
    validate_post(post, platform)
    require_approval(post)
    if not all((channel_id, organization_id, token)):
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
        verify_channel(platform, channel_id, organization_id, token, transport)
        image_check(post)
        try:
            with db:
                db.execute('INSERT INTO delivery VALUES (?, ?, ?)', (key, 'attempting', json.dumps({'attempted_at': now(), 'platform': platform})))
        except sqlite3.IntegrityError as exc:
            raise ValueError('Already attempted: inspect the durable receipt; never automatically repost') from exc
        payload = {'channelId': channel_id, 'text': post['caption'],
                   'schedulingType': 'automatic', 'mode': 'addToQueue',
                   'assets': [{'image': {'url': post['public_image_url']}}]}
        if platform == 'instagram':
            payload['metadata'] = {'instagram': {'type': 'post', 'shouldShareToFeed': True}}
        try:
            result = transport(CREATE, {'input': payload}, token).get('createPost', {})
            provider_post = result.get('post') or {}
            if result.get('message') or not provider_post.get('id'):
                raise RuntimeError('No confirmed Buffer post ID')
            receipt = {'state': 'queued', 'platform': platform, 'account_url': post['account_url'],
                       'provider_post_id': provider_post['id'], 'due_at': provider_post.get('dueAt'),
                       'queued_at': now(), 'published_at': None, 'public_post_url': None,
                       'note': 'Queued is not published. Final account appearance and URL remain unverified.'}
            state = 'queued'
        except Exception:
            receipt = {'state': 'unknown', 'platform': platform, 'observed_at': now(),
                       'note': 'Request may have succeeded. Inspect Buffer and the account before any further action.'}
            with db:
                db.execute('UPDATE delivery SET state=?,receipt=? WHERE key=?', ('unknown', json.dumps(receipt), key))
            raise RuntimeError('Delivery result uncertain; journal retained and automatic retry blocked') from None
        with db:
            db.execute('UPDATE delivery SET state=?,receipt=? WHERE key=?', (state, json.dumps(receipt), key))
        return receipt
