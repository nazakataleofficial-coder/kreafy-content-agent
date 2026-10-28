"""Remove only registered temporary renders after all four verified publications.

No Drive writes, repository/history deletion, or directory-recursive deletion.
Receipts, manifests and original assets are always retained. Dry-run by default.
"""
import argparse
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from studio.core import ACCOUNTS, PLATFORMS, atomic_json, file_hash, require_approval, validate_post
from studio.publications import content_key, timestamp, validate_url

RETENTION = timedelta(days=3)


def cleanup(root, journal, apply=False, at=None):
    root = Path(root).absolute()
    clock = at or datetime.now(timezone.utc)
    if clock.utcoffset() is None:
        raise ValueError('Cleanup time must include timezone')
    # Only the designated generated-output directory can be a deletion root.
    if root.name != 'studio-output' or root.is_symlink() or root.resolve() != root:
        raise ValueError('Use a real studio-output directory without symlink ancestors')
    result = {'mode': 'apply' if apply else 'dry-run', 'removed': [], 'eligible': [], 'skipped': []}
    if not root.is_dir() or not Path(journal).is_file():
        result['skipped'].append('Output directory or durable publication journal missing')
        return result
    with sqlite3.connect(Path(journal).resolve().as_uri() + '?mode=ro', uri=True) as db:
        try:
            receipts = {key: (state, json.loads(raw)) for key, state, raw in
                        db.execute('SELECT key,state,receipt FROM delivery')}
        except (sqlite3.Error, ValueError) as exc:
            raise ValueError('Cannot verify publication journal; nothing removed') from exc
    # A shallow scan deliberately excludes any original/imported subdirectories.
    for folder in sorted(root.iterdir()):
        manifest_path = folder / 'manifest.json'
        if not folder.is_dir() or folder.is_symlink() or not manifest_path.is_file():
            continue
        try:
            if manifest_path.is_symlink():
                raise ValueError('Symlink manifest')
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            policy = manifest.get('temporary_render_cleanup')
            if not policy or policy.get('version') != 1:
                raise ValueError('No explicit temporary-render inventory')
            if policy.get('completed_at'):
                continue
            posts = manifest['platforms']
            if set(posts) != set(PLATFORMS):
                raise ValueError('All four platform manifests required')
            eligible_at = []
            for platform in PLATFORMS:
                post = posts[platform]
                validate_post(post, platform, check_assets=False)
                require_approval(post)
                state, receipt = receipts.get(content_key(post), ('missing', {}))
                if (state != 'published' or receipt.get('state') != 'published' or
                        receipt.get('platform') != platform or
                        receipt.get('account_url') != ACCOUNTS[platform] or
                        receipt.get('verification_method') != 'operator_live_account_caption_image'):
                    raise ValueError('All four live publications must be verified')
                validate_url(platform, receipt.get('public_post_url', ''))
                published = timestamp(receipt.get('published_at'))
                verified = timestamp(receipt.get('verified_at'))
                if published > verified or verified > clock:
                    raise ValueError('Invalid publication/verification time')
                eligible_at.append(max(published, verified) + RETENTION)
            if clock < max(eligible_at):
                raise ValueError('Three-day retention has not elapsed')
            files = policy.get('files', [])
            expected = {Path(p['image']).name: p['image_sha256'] for p in posts.values()}
            if (not files or len(files) != len(expected) or
                    {f['name']: f['sha256'] for f in files} != expected):
                raise ValueError('Temporary inventory differs from approved images')
            targets = []
            for item in files:
                name = item['name']
                if Path(name).name != name or not name.endswith('.png') or not name.startswith(('portrait-', 'wide-')):
                    raise ValueError('Only generated portrait/wide PNGs can be removed')
                target = folder / name
                for post in posts.values():
                    if Path(post['image']).name == name and Path(post['image']).absolute() != target:
                        raise ValueError('Image lies outside this generated topic folder')
                if target.is_symlink() or target.resolve().parent != folder.resolve():
                    raise ValueError('Unsafe render path')
                if target.exists() and (not target.is_file() or target.stat().st_nlink != 1 or file_hash(target) != item['sha256']):
                    raise ValueError('Render changed or has linked copies')
                targets.append(target)
            # Validate the whole topic before deleting any byte. Missing files are
            # tolerated to recover a previously interrupted cleanup safely.
            result['eligible'].append(str(folder))
            if apply:
                for target in targets:
                    if target.exists():
                        target.unlink()
                        result['removed'].append(str(target))
                policy['completed_at'] = clock.isoformat()
                policy['reason'] = 'All four live publications verified; three-day retention elapsed'
                atomic_json(manifest_path, manifest)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            result['skipped'].append({'manifest': str(manifest_path), 'reason': str(exc)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='studio-output')
    parser.add_argument('--journal', default='studio-private/delivery.sqlite3')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    print(json.dumps(cleanup(args.root, args.journal, args.apply), indent=2))


if __name__ == '__main__':
    main()
