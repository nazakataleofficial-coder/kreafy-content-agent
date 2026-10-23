"""Private offline evidence log; never accesses inboxes or sends messages."""
import json
import re
import sqlite3
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

from studio.core import PLATFORMS, now
from studio.publications import timestamp, validate_url

SERVICES = ('website', 'app', 'youtube', 'animation-2d', 'animation-3d',
            'video-editing', 'ai-automation', 'social-growth')
STAGES = ('enquiry', 'qualified', 'booked', 'won', 'lost')
ALLOWED = {None: {'enquiry'}, 'enquiry': {'qualified', 'lost'},
           'qualified': {'booked', 'won', 'lost'}, 'booked': {'won', 'lost'},
           'won': set(), 'lost': set()}


def record_lead(journal, platform, service, stage, observed_at, evidence,
                lead_id=None, post_url=None, attribution='unknown', amount_pkr=None):
    if platform not in PLATFORMS or service not in SERVICES or stage not in STAGES:
        raise ValueError('Unsupported platform, service or stage')
    if evidence not in ('operator_observed', 'user_reported'):
        raise ValueError('An actual observation or user report is required')
    observed = timestamp(observed_at)
    if attribution not in ('unknown', 'direct', 'self_reported'):
        raise ValueError('Invalid attribution')
    if bool(post_url) != (attribution != 'unknown'):
        raise ValueError('A post URL needs direct or self-reported attribution; never guess attribution')
    if post_url:
        validate_url(platform, post_url)
    if lead_id is None:
        if stage != 'enquiry':
            raise ValueError('Start with an enquiry before progressing a lead')
        lead_id = uuid.uuid4().hex
    if not re.fullmatch(r'[0-9a-f]{32}', lead_id):
        raise ValueError('Use an opaque hexadecimal lead ID, never a name or contact')
    amount = None
    if amount_pkr is not None:
        try:
            amount = Decimal(str(amount_pkr))
            if (not amount.is_finite() or amount <= 0 or
                    amount != amount.quantize(Decimal('0.01')) or stage != 'won'):
                raise ValueError
        except (InvalidOperation, ValueError):
            raise ValueError('Record positive actual received PKR, at most two decimals, only at won') from None
    event = dict(lead_id=lead_id, platform=platform, service=service, stage=stage,
                 observed_at=observed_at, recorded_at=now(), evidence=evidence,
                 post_url=post_url, attribution=attribution,
                 amount_pkr=str(amount) if amount is not None else None)
    Path(journal).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(journal, timeout=30) as db:
        db.execute('CREATE TABLE IF NOT EXISTS lead_events (seq INTEGER PRIMARY KEY, lead_id TEXT NOT NULL, event TEXT NOT NULL)')
        with db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT event FROM lead_events WHERE lead_id=? ORDER BY seq DESC LIMIT 1', (lead_id,)).fetchone()
            previous = json.loads(old[0]) if old else None
            if previous:
                if previous['platform'] != platform or previous['service'] != service:
                    raise ValueError('Existing lead identity differs; do not silently reassign it')
                if observed < timestamp(previous['observed_at']):
                    raise ValueError('Observation predates the last lead event')
            if stage not in ALLOWED[previous['stage'] if previous else None]:
                raise ValueError('Duplicate or invalid lead stage transition')
            db.execute('INSERT INTO lead_events (lead_id,event) VALUES (?,?)', (lead_id, json.dumps(event)))
    return event


def lead_scorecard(journal):
    rows = []
    if Path(journal).is_file():
        with sqlite3.connect(Path(journal).resolve().as_uri() + '?mode=ro', uri=True) as db:
            if db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lead_events'").fetchone():
                rows = [json.loads(r[0]) for r in db.execute('SELECT event FROM lead_events ORDER BY seq')]
    score = dict(scope='Recorded evidence only; not a complete business total or live analytics.',
                 recorded_leads=len({r['lead_id'] for r in rows}),
                 relevant_enquiries=None, qualified_enquiries=None, consultation_bookings=None,
                 won_projects=None, recorded_received_pkr=None, received_amounts_known=0,
                 attribution_note='No attribution or revenue inferred from views, likes or comments.')
    if rows:
        for key, stage in [('relevant_enquiries', 'enquiry'), ('qualified_enquiries', 'qualified'),
                           ('consultation_bookings', 'booked'), ('won_projects', 'won')]:
            score[key] = len({r['lead_id'] for r in rows if r['stage'] == stage})
        amounts = [Decimal(r['amount_pkr']) for r in rows if r['stage'] == 'won' and r['amount_pkr'] is not None]
        score['received_amounts_known'] = len(amounts)
        score['recorded_received_pkr'] = str(sum(amounts, Decimal('0'))) if amounts else None
    return score
