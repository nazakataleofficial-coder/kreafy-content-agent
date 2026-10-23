import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from studio import core
from studio.content import TOPICS, captions
from studio.delivery import queue_post, verify_channel
from studio.prepare import prepare
from studio.render import render

ROOT = Path(__file__).resolve().parents[1]


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.image = self.root / 'image.png'
        Image.new('RGB', (32, 32), 'red').save(self.image)
        self.post = {'account_url': core.ACCOUNTS['twitter'], 'caption': 'One useful test before another tool.',
                     'image': str(self.image), 'image_sha256': core.file_hash(self.image),
                     'public_image_url': 'https://example.invalid/approved.png', 'planned_date_pkt': '2026-10-26',
                     'sources': ['https://support.google.com/youtube/answer/9314415']}
        self.journal = self.root / 'private' / 'receipts.sqlite3'
        self.calls = []

    def tearDown(self):
        self.temp.cleanup()

    def transport(self, query, variables, token):
        self.calls.append(query)
        if query.startswith('query'):
            return {'channels': [{'id': 'channel', 'service': 'twitter',
                    'externalLink': core.ACCOUNTS['twitter'], 'isDisconnected': False,
                    'isLocked': False, 'isQueuePaused': False}]}
        return {'createPost': {'post': {'id': 'provider-1', 'dueAt': None}}}

    def deliver(self, transport=None):
        return queue_post(self.post, 'twitter', self.journal, 'channel', 'org', 'not-a-real-token',
                          transport=transport or self.transport, image_check=lambda post: None)

    def test_no_permission_means_no_network(self):
        with patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': ''}):
            with self.assertRaisesRegex(ValueError, 'disabled'):
                self.deliver()
        self.assertEqual(self.calls, [])

    @patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': 'true'})
    def test_unapproved_means_no_network(self):
        with self.assertRaisesRegex(ValueError, 'not been approved'):
            self.deliver()
        self.assertEqual(self.calls, [])

    def test_approval_binds_every_publishing_field(self):
        core.approve(self.post)
        core.require_approval(self.post)
        for key, value in [('caption', 'New caption'), ('account_url', 'https://x.com/other'),
                           ('public_image_url', 'https://example.invalid/other.png'),
                           ('image_sha256', 'changed'), ('planned_date_pkt', '2026-10-27')]:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.post)
                changed[key] = value
                with self.assertRaises(ValueError):
                    core.require_approval(changed)

    def test_missing_or_changed_image_is_blocked(self):
        self.image.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'missing or changed'):
            core.validate_post(self.post, 'twitter')
        self.image.unlink()
        with self.assertRaises(ValueError):
            core.validate_post(self.post, 'twitter')

    def test_wrong_account_is_blocked(self):
        self.post['account_url'] = 'https://x.com/other'
        with self.assertRaises(ValueError):
            core.validate_post(self.post, 'twitter')

    def test_unicode_and_url_bounds(self):
        self.assertEqual(core.x_weight('x https://example.com/' + 'a'*100), 25)
        self.assertGreater(core.x_weight('\U0001f600'*150), 280)
        self.post['caption'] = 'x'*281
        with self.assertRaises(ValueError):
            core.validate_post(self.post, 'twitter')

    def test_sources_and_guarantees_are_reviewed(self):
        for value in ('Guaranteed revenue', '99.9% success', '**Fake bold**'):
            self.post['caption'] = value
            with self.assertRaises(ValueError):
                core.validate_post(self.post, 'twitter')
        self.post['caption'] = 'Useful advice'
        self.post['sources'] = []
        with self.assertRaises(ValueError):
            core.validate_post(self.post, 'twitter')

    @patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': 'true'})
    def test_receipt_is_queued_not_published_and_repeat_is_blocked(self):
        core.approve(self.post)
        receipt = self.deliver()
        self.assertEqual(receipt['state'], 'queued')
        self.assertIsNone(receipt['published_at'])
        self.assertIsNone(receipt['public_post_url'])
        # Moving the editorial date/reapproving must not bypass the journal.
        self.post['planned_date_pkt'] = '2026-11-01'
        core.approve(self.post)
        with self.assertRaisesRegex(ValueError, 'Already attempted'):
            self.deliver()
        self.assertEqual(sum(q.startswith('mutation') for q in self.calls), 1)

    @patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': 'true'})
    def test_timeout_is_durable_unknown_and_never_retried(self):
        def timeout(query, variables, token):
            if query.startswith('query'):
                return self.transport(query, variables, token)
            self.calls.append(query)
            raise TimeoutError('Potentially accepted by server')
        core.approve(self.post)
        with self.assertRaisesRegex(RuntimeError, 'uncertain'):
            self.deliver(timeout)
        with self.assertRaisesRegex(ValueError, 'Already attempted'):
            self.deliver(timeout)
        self.assertEqual(sum(q.startswith('mutation') for q in self.calls), 1)
        import sqlite3
        with sqlite3.connect(self.journal) as db:
            self.assertEqual(db.execute('SELECT state FROM delivery').fetchone()[0], 'unknown')

    @patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': 'true'})
    def test_missing_provider_id_is_not_success(self):
        def missing(query, variables, token):
            return self.transport(query, variables, token) if query.startswith('query') else {'createPost': {}}
        core.approve(self.post)
        with self.assertRaisesRegex(RuntimeError, 'uncertain'):
            self.deliver(missing)

    def test_channel_identity_and_connection_are_checked(self):
        for changed in ({'externalLink': 'https://x.com/unrelated'}, {'isLocked': True},
                        {'isDisconnected': True}, {'isQueuePaused': True}, {'service': 'linkedin'}):
            def transport(query, variables, token):
                result = self.transport(query, variables, token)
                result['channels'][0].update(changed)
                return result
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                verify_channel('twitter', 'channel', 'org', 'token', transport)

    @patch.dict(os.environ, {'KREAFY_PUBLISH_ENABLED': 'true'})
    def test_facebook_profile_has_no_silent_buffer_fallback(self):
        with self.assertRaisesRegex(ValueError, 'native posting'):
            queue_post(self.post, 'facebook', self.journal, 'channel', 'org', 'token')

    def test_legacy_model_calls_fail_before_import_or_network(self):
        from config.config import require_billable_api_opt_in
        with patch.dict(os.environ, {'KREAFY_ALLOW_BILLABLE_APIS': ''}):
            with self.assertRaises(RuntimeError):
                require_billable_api_opt_in()
        from generator.hottake_generator import generate_with_gemini, generate_with_claude
        with patch.dict(os.environ, {'KREAFY_ALLOW_BILLABLE_APIS': ''}):
            for generator in (generate_with_gemini, generate_with_claude):
                with self.assertRaisesRegex(RuntimeError, 'API calls disabled'):
                    generator('No calls allowed')

    def test_unpinned_public_asset_fails_before_fetch(self):
        from studio.delivery import verify_public_image
        with patch('studio.delivery.urlopen') as fetch:
            with self.assertRaisesRegex(ValueError, 'immutable'):
                verify_public_image(self.post)
            fetch.assert_not_called()


class ConnectionReportTests(unittest.TestCase):
    def test_missing_token_never_calls_provider(self):
        from studio.connections import inspect_connections
        with patch('studio.connections.graphql') as transport:
            with self.assertRaises(ValueError):
                inspect_connections('', {}, transport)
            transport.assert_not_called()

    def test_report_verifies_all_three_exact_accounts_without_mutation(self):
        from studio.connections import inspect_connections
        calls = []
        def transport(query, variables, token):
            calls.append(query)
            if query.startswith('query Account'):
                return {'account': {'organizations': [{'id': 'org'}]}}
            return {'channels': [{'id': p, 'service': p, 'externalLink': core.ACCOUNTS[p],
                'isDisconnected': False, 'isLocked': False, 'isQueuePaused': False}
                for p in ('linkedin', 'instagram', 'twitter')]}
        report = inspect_connections('dummy', {p: p for p in ('linkedin', 'instagram', 'twitter')}, transport)
        self.assertTrue(all(report[p]['ready'] for p in ('linkedin', 'instagram', 'twitter')))
        self.assertFalse(report['facebook']['ready'])
        self.assertTrue(all(q.startswith('query') for q in calls))
        self.assertNotIn('dummy', json.dumps(report))

    def test_missing_channel_secret_is_reported_as_not_ready(self):
        from studio.connections import inspect_connections
        def transport(query, variables, token):
            return {'account': {'organizations': [{'id': 'org'}]}}
        report = inspect_connections('dummy', {}, transport)
        self.assertTrue(all(not item['ready'] for item in report.values()))


class CampaignTests(unittest.TestCase):
    def test_approved_photo_extraction_preserves_pixels_and_excludes_old_text(self):
        from studio.identity import approved_reference
        photo, extracted, policy = approved_reference(ROOT)
        self.assertEqual(extracted.size, (1122, 1000))
        with Image.open(photo) as original:
            self.assertEqual(extracted.tobytes(), original.convert('RGB').crop((0, 0, 1122, 1000)).tobytes())
        self.assertFalse(policy['legacy_rotation'])
        self.assertFalse(policy['face_regeneration'])

    def test_missing_or_changed_reference_never_uses_legacy_faces(self):
        from studio.identity import approved_reference
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'assets/approved_identity', root / 'assets/approved_identity')
            legacy = root / 'assets/real_photos'
            legacy.mkdir()
            Image.new('RGB', (30, 30), 'red').save(legacy / 'confident.png')
            approved = root / 'assets/approved_identity/nazakat-ale-approved.png'
            approved.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'fallback is forbidden'):
                approved_reference(root)
            approved.unlink()
            with self.assertRaisesRegex(ValueError, 'fallback is forbidden'):
                approved_reference(root)

    def test_all_48_platform_captions_fit_and_have_original_sources(self):
        self.assertEqual(len(TOPICS), 12)
        self.assertEqual(len({t['id'] for t in TOPICS}), 12)
        for topic in TOPICS:
            for platform, caption in captions(topic).items():
                core.validate_post({'caption': caption, 'account_url': core.ACCOUNTS[platform],
                                    'sources': topic['sources']}, platform, check_assets=False)

    def test_render_keeps_all_four_corners_without_crop(self):
        with tempfile.TemporaryDirectory() as tmp:
            photo = Path(tmp) / 'source.png'
            image = Image.new('RGB', (200, 400), 'white')
            from PIL import ImageDraw
            draw = ImageDraw.Draw(image)
            colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00']
            for box, color in zip([(0,0,50,50), (150,0,199,50), (0,350,50,399), (150,350,199,399)], colors):
                draw.rectangle(box, fill=color)
            image.save(photo)
            for variant in ('portrait', 'wide'):
                out = Path(tmp) / f'{variant}.png'
                result = render(photo, 'TEST THE PROBLEM', 'One useful next step.', out, variant, ['Check input', 'Test once', 'Review output'])
                self.assertFalse(result['source_cropped'])
                rendered = Image.open(out)
                expected = (1080,1350) if variant == 'portrait' else (1200,675)
                self.assertEqual(rendered.size, expected)
                available = set(rendered.get_flattened_data())
                for rgb in [(255,0,0),(0,255,0),(0,0,255),(255,255,0)]:
                    self.assertIn(rgb, available)

    def test_full_campaign_repeat_preserves_approvals_and_kpi_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = prepare(ROOT, tmp, '2026-10-26')
            self.assertEqual(len(paths), 12)
            first = json.loads(paths[0].read_text())
            self.assertEqual(set(first['platforms']), set(core.PLATFORMS))
            core.approve(first['platforms']['linkedin'])
            core.atomic_json(paths[0], first)
            scorecard = Path(tmp) / 'scorecard.csv'
            original_scorecard = scorecard.read_text()
            self.assertNotIn(',0,', original_scorecard)  # unknown metrics are empty
            scorecard.write_text(original_scorecard + '\nMANUAL RECORD PRESERVED\n')
            photo_before = core.file_hash(ROOT / 'assets/approved_identity/nazakat-ale-approved.png')
            prepare(ROOT, tmp, '2026-10-26')
            second = json.loads(paths[0].read_text())
            core.require_approval(second['platforms']['linkedin'])
            self.assertIn('MANUAL RECORD PRESERVED', scorecard.read_text())
            self.assertEqual(photo_before, core.file_hash(ROOT / 'assets/approved_identity/nazakat-ale-approved.png'))
            self.assertEqual(second['source_photo_sha256'], photo_before)
            self.assertEqual(second['render']['crop_box'], [0, 0, 1122, 1000])
            self.assertFalse(second['render']['face_regenerated'])
            page = (Path(tmp) / 'index.html').read_text()
            self.assertNotIn('<script', page)
            self.assertEqual(page.count('<article '), 48)


if __name__ == '__main__':
    unittest.main()
