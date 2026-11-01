import copy
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from studio.core import ACCOUNTS, approve, digest, file_hash, require_approval, validate_post
from studio.delivery import build_payload, check_remote_duplicates, preflight_post, queue_post, refresh_post, verify_public_image
from studio.publications import content_key


class BufferMediaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.journal = self.root / 'delivery.sqlite3'
        self.assets = []
        for i in range(5):
            path = self.root / f'slide-{i}.png'
            Image.new('RGB', (16, 20), (i * 20, 0, 0)).save(path)
            self.assets.append({'type': 'image', 'path': str(path), 'sha256': file_hash(path),
                'url': 'https://raw.githubusercontent.com/nazakataleofficial-coder/kreafy-content-agent/' + 'a'*40 + f'/slide-{i}.png'})
        self.post = {'account_url': ACCOUNTS['instagram'], 'caption': 'Identity and permissions are different.',
                     'sources': ['https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html'],
                     'assets': copy.deepcopy(self.assets)}
        self.calls = []
        self.platform = 'instagram'
        self.provider_status = 'sent'
        self.provider_override = {}
        self.pages = [{'edges': [], 'pageInfo': {'hasNextPage': False, 'endCursor': None}}]

    def tearDown(self):
        self.tmp.cleanup()

    def transport(self, query, variables, token):
        self.calls.append((query, variables))
        if query.startswith('query Account'):
            return {'account': {'organizations': [{'id': 'org'}]}}
        if query.startswith('query Channels'):
            return {'channels': [{'id': 'channel', 'service': self.platform,
                'externalLink': ACCOUNTS[self.platform], 'isLocked': False,
                'isDisconnected': False, 'isQueuePaused': False}]}
        if query.startswith('query DuplicateCheck'):
            return {'posts': self.pages.pop(0)}
        if query.startswith('query PublicationStatus'):
            item = {'id': 'post-1', 'channelId': 'channel', 'text': self.post['caption'],
                    'status': self.provider_status, 'sentAt': '2026-10-20T12:00:00Z',
                    'externalLink': 'https://www.instagram.com/p/SAMPLE/',
                    'channel': {'service': self.platform, 'externalLink': ACCOUNTS[self.platform]},
                    'assets': [{'source': a['url']} for a in self.post['assets']]}
            item.update(self.provider_override)
            return {'post': item}
        if query.startswith('mutation'):
            return {'createPost': {'post': {'id': 'post-1', 'dueAt': None}}}
        self.fail('Unexpected operation')

    def send(self):
        approve(self.post)
        with patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': 'true'}):
            return queue_post(self.post, self.platform, self.journal, 'channel', 'org', 'dummy',
                              transport=self.transport, image_check=lambda post: None)

    def refresh(self):
        return refresh_post(self.post, self.platform, self.journal, 'dummy', transport=self.transport)

    def test_five_images_preserve_order_and_required_api_field(self):
        self.send()
        payload = next(v['input'] for q, v in self.calls if q.startswith('mutation'))
        self.assertEqual([a['image']['url'] for a in payload['assets']], [a['url'] for a in self.assets])
        self.assertIs(payload['needsApproval'], False)
        self.assertEqual(payload['metadata']['instagram']['type'], 'post')

    def test_linkedin_document_has_title_url_and_thumbnail(self):
        self.platform = 'linkedin'
        self.post['account_url'] = ACCOUNTS['linkedin']
        path = self.root / 'slides.pdf'
        path.write_bytes(b'%PDF-1.4\n%fixture for transport test')
        self.post['assets'] = [{'type': 'document', 'path': str(path), 'sha256': file_hash(path),
            'url': self.assets[0]['url'].replace('.png', '.pdf'), 'title': 'Authentication vs Authorization',
            'thumbnail': self.assets[0]}]
        self.send()
        doc = next(v['input']['assets'][0]['document'] for q, v in self.calls if q.startswith('mutation'))
        self.assertEqual(doc['title'], 'Authentication vs Authorization')
        self.assertEqual(doc['thumbnailUrl'], self.assets[0]['url'])
        self.assertTrue(doc['url'].endswith('.pdf'))
        self.assertNotIn('image', next(v['input']['assets'][0] for q, v in self.calls if q.startswith('mutation')))

    def test_invalid_media_is_rejected_without_network(self):
        for assets, platform in [([], 'instagram'), (self.assets, 'twitter'),
                                 ([{'type': 'video'}], 'instagram'),
                                 ([{'type': 'document'}], 'instagram')]:
            with self.subTest(platform=platform, assets=assets):
                bad = dict(self.post, assets=assets, account_url=ACCOUNTS[platform])
                with self.assertRaises(ValueError):
                    validate_post(bad, platform)
        self.assertFalse(self.calls)

    def test_changed_slide_and_thumbnail_require_approval(self):
        approve(self.post)
        self.post['assets'][3]['sha256'] = 'f'*64
        with self.assertRaises(ValueError):
            require_approval(self.post)
        with self.assertRaises(ValueError):
            validate_post(self.post, 'instagram')

    def test_reordering_changes_content_key_but_moving_files_or_dates_does_not(self):
        original = content_key(self.post)
        moved = copy.deepcopy(self.post)
        moved['assets'][0]['path'] = 'another-path.png'
        moved['due_at'] = '2099-01-01T00:00:00Z'
        self.assertEqual(content_key(moved), original)
        moved['assets'].reverse()
        self.assertNotEqual(content_key(moved), original)

    def test_legacy_single_image_keeps_its_journal_key(self):
        legacy = {'account_url': ACCOUNTS['twitter'], 'caption': 'Test', 'image_sha256': self.assets[0]['sha256']}
        modern = {'account_url': legacy['account_url'], 'caption': 'Test', 'assets': [self.assets[0]]}
        expected = digest({'account': legacy['account_url'], 'caption': 'Test', 'image': legacy['image_sha256']})
        self.assertEqual(content_key(legacy), expected)
        self.assertEqual(content_key(modern), expected)

    def test_mixed_legacy_and_new_schema_is_rejected(self):
        self.post['image'] = self.assets[0]['path']
        with self.assertRaisesRegex(ValueError, 'not both'):
            validate_post(self.post, 'instagram')

    def test_delivery_mode_is_approved_and_immediate_is_not_reported_published(self):
        self.post['delivery_mode'] = 'shareNow'
        result = self.send()
        self.assertEqual(result['state'], 'submitted')
        self.assertIsNone(result['published_at'])
        self.post['delivery_mode'] = 'addToQueue'
        with self.assertRaises(ValueError):
            require_approval(self.post)

    def test_fixed_schedule_requires_future_time_with_timezone(self):
        self.post['delivery_mode'] = 'customScheduled'
        for when in ('2020-01-01T00:00:00Z', '2099-01-01T00:00:00', None):
            self.post['due_at'] = when
            with self.assertRaises(ValueError):
                build_payload(self.post, 'instagram', 'channel')
        self.post['due_at'] = '2099-01-01T12:00:00+05:00'
        self.assertEqual(build_payload(self.post, 'instagram', 'channel')['dueAt'], self.post['due_at'])

    def test_existing_organization_is_resolved_without_new_secret(self):
        approve(self.post)
        preflight_post(self.post, 'instagram', 'channel', '', 'dummy', self.transport, lambda p: None)
        self.assertTrue(all(q.startswith('query') for q, _ in self.calls))
        self.assertFalse(self.journal.exists())

    def test_duplicate_on_second_page_blocks_mutation(self):
        self.pages = [
            {'edges': [], 'pageInfo': {'hasNextPage': True, 'endCursor': 'cursor-1'}},
            {'edges': [{'node': {'channelId': 'channel', 'text': self.post['caption'], 'assets': []}}],
             'pageInfo': {'hasNextPage': False}}]
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.send()
        self.assertFalse(any(q.startswith('mutation') for q, _ in self.calls))

    def test_incomplete_duplicate_scan_fails_closed(self):
        self.pages = [{'edges': [], 'pageInfo': {}}]
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            self.send()
        self.assertFalse(any(q.startswith('mutation') for q, _ in self.calls))

    def test_public_asset_checks_every_slide(self):
        class Headers:
            def get_content_type(self):
                return 'image/png'
        class Response:
            headers = Headers()
            def __init__(self, url, blob): self.url, self.blob = url, blob
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def geturl(self): return self.url
            def read(self, limit): return self.blob[:limit]
        def fetch(request, timeout):
            index = [a['url'] for a in self.assets].index(request.full_url)
            blob = Path(self.assets[index]['path']).read_bytes()
            if index == 4: blob = b'changed fifth slide'
            return Response(request.full_url, blob)
        with patch('studio.delivery.urlopen', side_effect=fetch) as mocked:
            with self.assertRaisesRegex(ValueError, 'differs'):
                verify_public_image(self.post)
            self.assertEqual(mocked.call_count, 5)

    def test_sent_is_provider_evidence_and_does_not_enable_cleanup(self):
        self.send()
        result = self.refresh()
        self.assertEqual(result['state'], 'provider_sent')
        self.assertEqual(result['provider_post_url'], 'https://www.instagram.com/p/SAMPLE/')
        self.assertEqual(result['verification_method'], 'buffer_api_only')
        self.assertIsNone(result['public_post_url'])
        self.assertIsNone(result['published_at'])
        self.assertIsNone(result['metrics'])
        self.assertEqual(sum(q.startswith('mutation') for q, _ in self.calls), 1)

    def test_wrong_returned_account_does_not_change_receipt(self):
        original = self.send()
        self.provider_override['channelId'] = 'unrelated'
        with self.assertRaises(ValueError): self.refresh()
        with sqlite3.connect(self.journal) as db:
            self.assertEqual(json.loads(db.execute('SELECT receipt FROM delivery').fetchone()[0]), original)

    def test_sent_missing_evidence_or_changed_content_needs_review(self):
        self.send()
        for override in ({'externalLink': None}, {'sentAt': None}, {'text': 'Edited elsewhere'}, {'assets': []}):
            with self.subTest(override=override):
                self.provider_override = override
                self.assertEqual(self.refresh()['state'], 'needs_review')

    def test_failed_post_is_not_automatically_retried(self):
        self.send()
        self.provider_status = 'error'
        self.assertEqual(self.refresh()['state'], 'failed')
        with self.assertRaisesRegex(ValueError, 'Already attempted'):
            self.send()
        self.assertEqual(sum(q.startswith('mutation') for q, _ in self.calls), 1)

    def test_timeout_still_blocks_a_second_send(self):
        approve(self.post)
        def timeout(query, variables, token):
            if query.startswith('mutation'): raise TimeoutError()
            return self.transport(query, variables, token)
        with patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': 'true'}):
            with self.assertRaisesRegex(RuntimeError, 'uncertain'):
                queue_post(self.post, 'instagram', self.journal, 'channel', 'org', 'dummy', timeout, lambda p: None)
            with self.assertRaisesRegex(ValueError, 'Already attempted'):
                self.send()
        with self.assertRaisesRegex(ValueError, 'No known Buffer'):
            self.refresh()


if __name__ == '__main__':
    unittest.main()
