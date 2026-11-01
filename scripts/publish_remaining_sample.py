"""One authorized sample, three existing Buffer accounts; never retries delivery."""
import json
import os
from pathlib import Path
import time

from studio.core import atomic_json
from studio.publications import content_key
import sqlite3
from studio.delivery import preflight_post, queue_post, refresh_post

if os.environ.get('GITHUB_RUN_ATTEMPT') != '1':
    raise SystemExit('Only the first attempt is authorized; inspect receipts instead of rerunning')
manifest = json.loads(Path('approved-sample/krf001-v2/manifest.json').read_text())
journal = 'sample-receipts/delivery.sqlite3'
Path('sample-receipts').mkdir(exist_ok=True)
if Path(journal).exists():
    raise SystemExit('Journal already exists; inspect instead of resending')
token = os.environ.get('BUFFER_ACCESS_TOKEN', '')
platforms = ('instagram', 'twitter')
# LinkedIn was already sent by the first run. Seed ONLY its known receipt, never resend.
with sqlite3.connect(journal) as db:
    db.execute('CREATE TABLE delivery (key TEXT PRIMARY KEY,state TEXT NOT NULL,receipt TEXT NOT NULL)')
    receipt = {'state':'submitted','platform':'linkedin','account_url':manifest['platforms']['linkedin']['account_url'],'channel_id':os.environ.get('BUFFER_LINKEDIN_ID',''),'provider_post_id':'6ae769288755094b82933b74','delivery_mode':'shareNow','public_post_url':None,'published_at':None,'queued_at':'2026-11-01T16:30:43.035796+00:00'}
    db.execute('INSERT INTO delivery VALUES (?,?,?)',(content_key(manifest['platforms']['linkedin']),'submitted',json.dumps(receipt)))
receipt = refresh_post(manifest['platforms']['linkedin'],'linkedin',journal,token)
atomic_json('sample-receipts/linkedin.json',receipt)
print(json.dumps(receipt),flush=True)
if receipt.get('state') != 'provider_sent':
    raise SystemExit('Existing LinkedIn post needs review; no new send allowed')
# All read-only checks must pass before the first mutation.
for platform in platforms:
    preflight_post(manifest['platforms'][platform], platform,
                   os.environ.get(f'BUFFER_{platform.upper()}_ID', ''), '', token)
    print(json.dumps({'platform': platform, 'preflight': 'passed', 'sent': False}), flush=True)
for platform in platforms:
    post = manifest['platforms'][platform]
    receipt = queue_post(post, platform, journal,
                         os.environ.get(f'BUFFER_{platform.upper()}_ID', ''), '', token)
    atomic_json(f'sample-receipts/{platform}.json', receipt)
    print(json.dumps(receipt), flush=True)
    for check in range(7):
        receipt = refresh_post(post, platform, journal, token)
        atomic_json(f'sample-receipts/{platform}.json', receipt)
        print(json.dumps(receipt), flush=True)
        if receipt.get('provider_status') == 'sent':
            break
        if receipt.get('provider_status') not in ('sending', 'scheduled'):
            raise SystemExit('Unexpected provider state; stopped without a resend')
        if check < 6:
            time.sleep(10)
    if receipt.get('provider_status') != 'sent':
        raise SystemExit('Publication still pending; inspect known provider ID, never resend')
