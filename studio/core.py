"""Pure validation and approval primitives. No network calls or model billing."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PLATFORMS = ('facebook', 'linkedin', 'instagram', 'twitter')
ACCOUNTS = {
    'facebook': 'https://www.facebook.com/profile.php?id=61586245874786',
    'linkedin': 'https://www.linkedin.com/in/nazakat-ale/',
    'instagram': 'https://www.instagram.com/nazakataleofficial/',
    'twitter': 'https://x.com/Kreafyonline',
}
LIMITS = {'facebook': 63206, 'linkedin': 3000, 'instagram': 2200, 'twitter': 280}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def x_weight(text):
    """Conservative upper bound: URLs 23, each non-ASCII code point two.

    Emoji clusters can be overcounted (safe rejection). Never truncate a caption.
    This is intentionally not advertised as a complete twitter-text parser.
    """
    parts = re.split(r'(https?://[^\s]+)', text)
    return sum(23 if re.fullmatch(r'https?://[^\s]+', part) else
               sum(1 if ord(c) < 128 else 2 for c in part) for part in parts)


def validate_post(post, platform, check_assets=True):
    if platform not in PLATFORMS:
        raise ValueError('Unsupported platform')
    if post.get('account_url') != ACCOUNTS[platform]:
        raise ValueError('Unexpected target account')
    text = post.get('caption', '')
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Caption is empty')
    count = x_weight(text) if platform == 'twitter' else len(text.encode('utf-16-le')) // 2
    if count > LIMITS[platform]:
        raise ValueError(f'{platform}: caption exceeds conservative supported length')
    if '**' in text or re.search(r'\bguaranteed\b|\b99\.9%|\b100% success\b', text, re.I):
        raise ValueError('Formatting or unsupported guarantee requires review')
    sources = post.get('sources')
    if not isinstance(sources, list) or not sources or not all(
            isinstance(s, str) and s.startswith('https://') for s in sources):
        raise ValueError('Original source URLs are required')
    if check_assets:
        path = Path(post['image'])
        if not path.is_file() or file_hash(path) != post.get('image_sha256'):
            raise ValueError('Image missing or changed')
    return count


def approval_hash(post):
    # Every publishing-relevant value, including identity, caption, asset bytes,
    # planned date and exact public URL, is bound to the approval.
    return digest({k: v for k, v in post.items() if k != 'approval'})


def approve(post):
    post['approval'] = {'digest': approval_hash(post), 'approved_at': now()}


def require_approval(post):
    approval = post.get('approval', {})
    if not approval.get('approved_at') or approval.get('digest') != approval_hash(post):
        raise ValueError('This exact platform preview has not been approved or has changed')


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)
