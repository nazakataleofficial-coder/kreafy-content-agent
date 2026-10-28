import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from studio.cleanup import cleanup
from studio.core import ACCOUNTS, PLATFORMS, approve, file_hash
from studio.publications import content_key


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'studio-output'
        self.folder = self.root / 'topic'
        self.folder.mkdir(parents=True)
        self.image = self.folder / 'portrait-123.png'
        self.image.write_bytes(b'fixture render')
        self.original = Path(self.tmp.name) / 'source.pdf'
        self.original.write_bytes(b'keep original')
        self.clock = datetime(2026, 10, 28, tzinfo=timezone.utc)
        self.old = (self.clock - timedelta(days=4)).isoformat()
        self.manifest = {'platforms': {}, 'temporary_render_cleanup': {
            'version': 1, 'files': [{'name': self.image.name, 'sha256': file_hash(self.image)}], 'completed_at': None}}
        self.db = Path(self.tmp.name) / 'delivery.sqlite3'
        urls = {'facebook': 'https://www.facebook.com/photo/?fbid=123',
                'linkedin': 'https://www.linkedin.com/feed/update/urn:li:activity:123/',
                'instagram': 'https://www.instagram.com/nazakataleofficial/p/abc/',
                'twitter': 'https://x.com/Kreafyonline/status/123'}
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TABLE delivery (key TEXT PRIMARY KEY, state TEXT, receipt TEXT)')
            for p in PLATFORMS:
                post = {'account_url': ACCOUNTS[p], 'caption': 'Example', 'sources': ['https://example.com'],
                        'image': str(self.image), 'image_sha256': file_hash(self.image)}
                approve(post)
                self.manifest['platforms'][p] = post
                receipt = {'platform': p, 'state': 'published', 'account_url': ACCOUNTS[p],
                           'public_post_url': urls[p], 'published_at': self.old, 'verified_at': self.old,
                           'verification_method': 'operator_live_account_caption_image'}
                db.execute('INSERT INTO delivery VALUES (?,?,?)', (content_key(post), 'published', json.dumps(receipt)))
        self.save()

    def save(self):
        (self.folder / 'manifest.json').write_text(json.dumps(self.manifest))

    def change_receipt(self, **changes):
        key = content_key(self.manifest['platforms']['facebook'])
        with sqlite3.connect(self.db) as db:
            receipt = json.loads(db.execute('SELECT receipt FROM delivery WHERE key=?', (key,)).fetchone()[0])
            receipt.update(changes)
            db.execute('UPDATE delivery SET receipt=? WHERE key=?', (json.dumps(receipt), key))

    def test_dry_run_preserves_everything(self):
        r = cleanup(self.root, self.db, at=self.clock)
        self.assertEqual(len(r['eligible']), 1)
        self.assertTrue(self.image.exists())

    def test_cleanup_retains_originals_records_and_is_idempotent(self):
        extra = self.folder / 'unregistered.png'
        extra.write_bytes(b'keep')
        r = cleanup(self.root, self.db, True, self.clock)
        self.assertEqual(r['removed'], [str(self.image)])
        self.assertTrue(self.original.exists())
        self.assertTrue(extra.exists())
        self.assertTrue(self.db.exists())
        self.assertTrue((self.folder / 'manifest.json').exists())
        self.assertEqual(cleanup(self.root, self.db, True, self.clock)['removed'], [])

    def test_waits_after_latest_verification(self):
        self.change_receipt(verified_at=(self.clock - timedelta(days=2)).isoformat())
        self.assertEqual(cleanup(self.root, self.db, True, self.clock)['removed'], [])

    def test_exact_72_hour_boundary(self):
        boundary = self.clock - timedelta(days=1)
        self.assertEqual(cleanup(self.root, self.db, True, boundary - timedelta(seconds=1))['removed'], [])
        self.assertEqual(len(cleanup(self.root, self.db, True, boundary)['removed']), 1)

    def test_missing_or_invalid_receipts_block(self):
        for change in [{'state': 'queued'}, {'published_at': None}, {'verified_at': 'bad'},
                       {'account_url': 'https://example.com'}, {'public_post_url': ''},
                       {'verified_at': (self.clock + timedelta(days=1)).isoformat()}]:
            with self.subTest(change=change):
                self.change_receipt(**change)
                self.assertEqual(cleanup(self.root, self.db, True, self.clock)['removed'], [])

    def test_altered_approval_blocks(self):
        self.manifest['platforms']['facebook']['caption'] = 'Changed'
        self.save()
        self.assertEqual(cleanup(self.root, self.db, True, self.clock)['removed'], [])

    def test_changed_file_blocks(self):
        self.image.write_bytes(b'changed')
        self.assertEqual(cleanup(self.root, self.db, True, self.clock)['removed'], [])

    def test_legacy_pack_skipped(self):
        del self.manifest['temporary_render_cleanup']
        self.save()
        self.assertEqual(cleanup(self.root, self.db, True, self.clock)['removed'], [])

    def test_symlink_not_followed(self):
        self.image.unlink()
        self.image.symlink_to(self.original)
        self.assertEqual(cleanup(self.root, self.db, True, self.clock)['removed'], [])
        self.assertTrue(self.original.exists())

    def test_wrong_root_rejected(self):
        with self.assertRaises(ValueError):
            cleanup(self.root.parent, self.db, True, self.clock)

    def test_missing_journal_skipped(self):
        self.assertEqual(cleanup(self.root, self.db.with_name('absent'), True, self.clock)['removed'], [])


if __name__ == '__main__':
    unittest.main()
