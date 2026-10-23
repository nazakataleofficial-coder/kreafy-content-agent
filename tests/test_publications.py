import copy
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from studio.core import ACCOUNTS, approve, file_hash
from studio.delivery import queue_post
from studio.publications import content_key, publication_status, record_publication, validate_url


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        image = self.root / 'test.png'
        Image.new('RGB', (10, 10), 'blue').save(image)
        self.post = {'account_url': ACCOUNTS['twitter'], 'caption': 'Inspect the problem first.',
                     'image': str(image), 'image_sha256': file_hash(image),
                     'sources': ['https://example.org/source'], 'planned_date_pkt': '2026-10-26'}
        approve(self.post)
        self.journal = self.root / 'receipts.sqlite3'
        self.url = 'https://x.com/Kreafyonline/status/123456'

    def tearDown(self):
        self.tmp.cleanup()

    def record(self, **kwargs):
        values = dict(post=self.post, platform='twitter', journal=self.journal,
                      url=self.url, observed_at='2026-10-24T02:00:00+05:00', account_verified=True)
        values.update(kwargs)
        return record_publication(**values)

    def test_verified_native_publication_blocks_queue_before_network_even_after_date_change(self):
        receipt = self.record()
        self.assertIsNone(receipt['published_at'])
        self.assertIsNone(receipt['metrics'])
        changed = copy.deepcopy(self.post)
        changed['planned_date_pkt'] = '2026-11-03'
        approve(changed)
        with patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': 'true'}):
            with self.assertRaisesRegex(ValueError, 'Already attempted'):
                queue_post(changed, 'twitter', self.journal, 'channel', 'org', 'test',
                           transport=lambda *a: self.fail('No network permitted'),
                           image_check=lambda *a: self.fail('No image fetch permitted'))

    def test_explicit_live_verification_and_exact_approval_required(self):
        with self.assertRaisesRegex(ValueError, 'Verify the live'):
            self.record(account_verified=False)
        self.post['caption'] = 'Changed after approval'
        with self.assertRaisesRegex(ValueError, 'not been approved'):
            self.record()
        self.assertFalse(self.journal.exists())

    def test_reject_wrong_account_host_and_timestamp(self):
        for url in ['https://x.com/other/status/123', 'https://x.com.evil.org/Kreafyonline/status/123',
                    'https://user@x.com/Kreafyonline/status/123']:
            with self.assertRaises(ValueError):
                self.record(url=url)
        for stamp in ['today', '2026-10-24T02:00:00']:
            with self.assertRaises(ValueError):
                self.record(observed_at=stamp)
        with self.assertRaises(ValueError):
            self.record(published_at='2026-10-25T02:00:00+05:00')
        self.assertFalse(self.journal.exists())

    def test_reconcile_unknown_preserve_receipt_and_refuse_conflict(self):
        self.journal.parent.mkdir(exist_ok=True)
        with sqlite3.connect(self.journal) as db:
            db.execute('CREATE TABLE delivery (key TEXT PRIMARY KEY, state TEXT NOT NULL, receipt TEXT NOT NULL)')
            db.execute('INSERT INTO delivery VALUES (?, ?, ?)', (content_key(self.post), 'unknown', json.dumps({'state': 'unknown'})))
        receipt = self.record()
        self.assertEqual(receipt['previous_delivery']['state'], 'unknown')
        self.assertEqual(self.record(), receipt)
        with self.assertRaisesRegex(ValueError, 'Conflicting URL'):
            self.record(url='https://x.com/Kreafyonline/status/999')
        self.assertEqual(self.record(), receipt)

    def test_committed_history_has_four_original_urls_and_unknowns_stay_unknown(self):
        before = self.journal.exists()
        report = publication_status(journal=self.journal)
        self.assertEqual(len(report['publications']), 4)
        for item in report['publications']:
            validate_url(item['platform'], item['public_post_url'])
            self.assertEqual(item['account_url'], ACCOUNTS[item['platform']])
            self.assertIsNone(item['metrics']['qualified_enquiries'])
            self.assertIsNone(item['content_fingerprint'])
        self.assertEqual(self.journal.exists(), before)
        self.record()
        self.assertEqual(publication_status(journal=self.journal)['local_delivery_receipts'][0]['state'], 'published')


if __name__ == '__main__':
    unittest.main()
