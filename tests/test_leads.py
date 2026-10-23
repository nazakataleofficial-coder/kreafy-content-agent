import tempfile
import unittest
from pathlib import Path

from studio.leads import lead_scorecard, record_lead


class LeadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'private/leads.sqlite3'

    def tearDown(self):
        self.tmp.cleanup()

    def record(self, stage='enquiry', **kwargs):
        return record_lead(self.db, 'twitter', 'video-editing', stage,
                           '2026-10-24T03:00:00+05:00', 'operator_observed', **kwargs)

    def test_unknown_business_results_remain_unknown_without_creating_a_database(self):
        score = lead_scorecard(self.db)
        self.assertIsNone(score['qualified_enquiries'])
        self.assertIsNone(score['recorded_received_pkr'])
        self.assertFalse(self.db.exists())

    def test_distinct_stage_counts_and_money_are_not_double_counted(self):
        lead = self.record()['lead_id']
        self.record('qualified', lead_id=lead)
        self.record('booked', lead_id=lead)
        self.record('won', lead_id=lead, amount_pkr='12000.50')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.record('won', lead_id=lead, amount_pkr='12000.50')
        score = lead_scorecard(self.db)
        self.assertEqual(score['recorded_leads'], 1)
        self.assertEqual(score['qualified_enquiries'], 1)
        self.assertEqual(score['consultation_bookings'], 1)
        self.assertEqual(score['won_projects'], 1)
        self.assertEqual(score['recorded_received_pkr'], '12000.50')

    def test_won_without_known_amount_does_not_invent_revenue(self):
        lead = self.record()['lead_id']
        self.record('qualified', lead_id=lead)
        self.record('won', lead_id=lead)
        self.assertIsNone(lead_scorecard(self.db)['recorded_received_pkr'])

    def test_unverified_attribution_and_invalid_money_or_contact_ids_are_rejected(self):
        for kwargs in [dict(post_url='https://x.com/Kreafyonline/status/123'),
                       dict(attribution='direct'), dict(lead_id='a-person@example.org'),
                       dict(amount_pkr='NaN'), dict(amount_pkr='10.123'), dict(amount_pkr='-1')]:
            with self.assertRaises(ValueError):
                self.record(**kwargs)
        self.assertFalse(self.db.exists())
        event = self.record(post_url='https://x.com/Kreafyonline/status/123', attribution='self_reported')
        self.assertEqual(event['attribution'], 'self_reported')

    def test_lead_cannot_skip_enquiry_or_change_service_or_go_back_in_time(self):
        with self.assertRaises(ValueError):
            self.record('won')
        lead = self.record()['lead_id']
        with self.assertRaises(ValueError):
            record_lead(self.db, 'twitter', 'website', 'qualified', '2026-10-24T03:01:00+05:00',
                        'operator_observed', lead_id=lead)
        with self.assertRaises(ValueError):
            record_lead(self.db, 'twitter', 'video-editing', 'qualified', '2026-10-24T02:01:00+05:00',
                        'operator_observed', lead_id=lead)
        self.assertEqual(lead_scorecard(self.db)['recorded_leads'], 1)


if __name__ == '__main__':
    unittest.main()
