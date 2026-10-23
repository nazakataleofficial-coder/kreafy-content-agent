import json
from pathlib import Path
import shutil
import tempfile
import unittest

from studio.content import TOPICS
from studio.identity import (EXPRESSIONS, expression_for_topic,
                             expression_reference, load_expression_bank)

ROOT = Path(__file__).resolve().parents[1]


class ExpressionBankTests(unittest.TestCase):
    def test_all_22_assets_decode_and_use_full_photo_with_three_approved_references(self):
        bank = load_expression_bank(ROOT)
        self.assertEqual(len(bank['references']), 3)
        self.assertEqual(len(bank['assets']), 22)
        for name in EXPRESSIONS:
            photo, image, policy = expression_reference(ROOT, name, bank)
            self.assertEqual(list(image.size), bank['assets'][name]['size'])
            self.assertEqual(policy['expression'], name)
            self.assertTrue(policy['asset_ai_generated'])
            self.assertTrue(photo.is_file())

    def test_all_topics_select_intentional_expressions_and_unknown_topics_stop(self):
        chosen = [expression_for_topic(t) for t in TOPICS]
        self.assertEqual(len(set(chosen)), 12)
        self.assertTrue(set(chosen) <= EXPRESSIONS)
        with self.assertRaisesRegex(ValueError, 'explicit valid expression'):
            expression_for_topic({'id': 'unreviewed-new-topic'})
        self.assertEqual(expression_for_topic({'id': 'new-topic', 'expression': 'warm'}), 'warm')

    def test_changed_or_missing_portrait_stops_without_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'assets/approved_identity', root / 'assets/approved_identity')
            shutil.copytree(ROOT / 'assets/real_photos', root / 'assets/real_photos')
            target = root / 'assets/real_photos/curious.png'
            target.write_bytes(b'old or replaced portrait')
            with self.assertRaisesRegex(ValueError, 'no legacy fallback'):
                load_expression_bank(root)
            target.unlink()
            with self.assertRaisesRegex(ValueError, 'no legacy fallback'):
                load_expression_bank(root)

    def test_changed_side_reference_invalidates_bank(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'assets/approved_identity', root / 'assets/approved_identity')
            (root / 'assets/approved_identity/left-approved.png').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'reference missing or changed'):
                load_expression_bank(root)


if __name__ == '__main__':
    unittest.main()
