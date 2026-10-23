"""Offline reconciliation of manually verified publications; never publishes."""
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from studio.core import ACCOUNTS, digest, require_approval, validate_post

DEFAULT_HISTORY = Path(__file__).resolve().parents[1] / 'data/publications.json'


def content_key(post):
    return digest({'account': post['account_url'], 'caption': post['caption'],
                   'image': post['image_sha256']})


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.utcoffset() is None:
            raise ValueError
        return parsed
    except (ValueError, AttributeError):
        raise ValueError('An ISO timestamp with timezone is required') from None


def validate_url(platform, url):
    parsed = urlsplit(url)
    patterns = {
        'twitter': ('x.com', r'/Kreafyonline/status/[0-9]+/?'),
        'instagram': ('www.instagram.com', r'/nazakataleofficial/p/[A-Za-z0-9_-]+/?'),
        'linkedin': ('www.linkedin.com', r'/feed/update/urn:li:activity:[0-9]+/?'),
        'facebook': ('www.facebook.com', r'/photo/'),
    }
    host, pattern = patterns[platform]
    if (parsed.scheme != 'https' or parsed.netloc != host or
            not re.fullmatch(pattern, parsed.path) or parsed.fragment):
        raise ValueError('Unexpected public post URL for this platform/account')
    if platform == 'facebook':
        from urllib.parse import parse_qs
        query = parse_qs(parsed.query)
        if not re.fullmatch(r'[0-9]+', query.get('fbid', [''])[0]):
            raise ValueError('Facebook photo ID is required')
    elif parsed.query:
        raise ValueError('Use the original post URL without tracking parameters')


def record_publication(post, platform, journal, url, observed_at,
                       published_at=None, account_verified=False):
    """Operator must visually verify account, caption AND exact image first.

    A URL alone cannot prove Facebook/LinkedIn authorship. The explicit operator
    attestation is mandatory. No login, metrics scraping or delivery is performed.
    Existing attempting/unknown/queued entries are reconciled only by this command.
    """
    validate_post(post, platform)
    require_approval(post)
    if account_verified is not True:
        raise ValueError('Verify the live account, caption and image before recording')
    validate_url(platform, url)
    observed = timestamp(observed_at)
    if published_at and timestamp(published_at) > observed:
        raise ValueError('Publication cannot be later than the observation')
    receipt = {'state': 'published', 'platform': platform,
               'account_url': ACCOUNTS[platform], 'public_post_url': url,
               'published_at': published_at, 'verified_at': observed_at,
               'verification_method': 'operator_live_account_caption_image',
               'metrics': None}
    Path(journal).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(journal, timeout=30) as db:
        db.execute('CREATE TABLE IF NOT EXISTS delivery (key TEXT PRIMARY KEY, state TEXT NOT NULL, receipt TEXT NOT NULL)')
        with db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT state, receipt FROM delivery WHERE key=?', (content_key(post),)).fetchone()
            if old and old[0] == 'published':
                saved = json.loads(old[1])
                if saved['public_post_url'] != url:
                    raise ValueError('Conflicting URL: original published receipt retained')
                return saved
            if old:
                receipt['previous_delivery'] = json.loads(old[1])
            db.execute('INSERT OR REPLACE INTO delivery VALUES (?, ?, ?)',
                       (content_key(post), 'published', json.dumps(receipt)))
    return receipt


def publication_status(history=DEFAULT_HISTORY, journal=None):
    """Return observations as stored; never imply fresh analytics verification."""
    report = json.loads(Path(history).read_text(encoding='utf-8'))
    report['local_delivery_receipts'] = []
    if journal and Path(journal).is_file():
        with sqlite3.connect(Path(journal).resolve().as_uri() + '?mode=ro', uri=True) as db:
            exists = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery'").fetchone()
            if exists:
                report['local_delivery_receipts'] = [json.loads(row[0]) for row in db.execute('SELECT receipt FROM delivery ORDER BY key')]
    report['notice'] = 'Stored observations only. Unknown metrics are null. Nothing sent or changed.'
    return report
