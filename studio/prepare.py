"""Render a finite four-week campaign and a local read-only review report."""
import csv
import html
import json
from datetime import date, timedelta
from pathlib import Path

from studio.content import TOPICS, captions
from studio.core import ACCOUNTS, PLATFORMS, atomic_json, digest, file_hash, validate_post
from studio.render import render
from studio.identity import load_expression_bank, expression_for_topic, expression_reference


def prepare(root, destination, start):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    # Check the full editorial bank before writing any files.
    for topic in TOPICS:
        for platform, caption in captions(topic).items():
            validate_post({'caption': caption, 'account_url': ACCOUNTS[platform],
                           'sources': topic['sources']}, platform, check_assets=False)
    days, cursor = [], date.fromisoformat(start)
    while len(days) < len(TOPICS):
        if cursor.weekday() in (0, 2, 4):
            days.append(cursor)
        cursor += timedelta(days=1)
    bank = load_expression_bank(root)
    for topic in TOPICS:
        expression_for_topic(topic)
    destination.mkdir(parents=True, exist_ok=True)
    cards, rows, manifest_paths = [], [], []
    for scheduled_day, topic in zip(days, TOPICS):
        expression = expression_for_topic(topic)
        photo, extracted_photo, policy = expression_reference(root, expression, bank)
        identity = digest({'topic': topic, 'captions': captions(topic),
                           'photo': file_hash(photo), 'identity_policy': policy, 'template_version': 4})[:16]
        folder = destination / f'{scheduled_day}-{topic["id"]}-{identity}'
        manifest_path = folder / 'manifest.json'
        manifest_paths.append(manifest_path)
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            for platform, post in manifest['platforms'].items():
                validate_post(post, platform)
        else:
            folder.mkdir(parents=True, exist_ok=True)
            images = {}
            for variant in ('portrait', 'wide'):
                temp = folder / f'{variant}.png'
                render(extracted_photo, topic['headline'], topic['takeaway'], temp, variant, topic['poster_steps'])
                hashed = folder / f'{variant}-{file_hash(temp)[:20]}.png'
                temp.rename(hashed)
                images[variant] = hashed
            manifest = {'schema_version': 1, 'topic_id': topic['id'],
                        'pillar': topic['pillar'], 'goal': topic['goal'],
                        'editorial_note': 'Original recommendations; not a verified engagement or earnings claim. Source links are references, not live monitoring.',
                        'source_photo_sha256': file_hash(photo),
                        'identity_policy': policy,
                        'source_photo_path': bank['assets'][expression]['path'],
                        'expression': expression,
                        'render': {'source_cropped': False, 'crop_box': None,
                                   'face_regenerated': False, 'template_version': 4,
                                   'source_asset_ai_generated': True},
                        'platforms': {}}
            for platform, caption in captions(topic).items():
                image = images['wide' if platform == 'twitter' else 'portrait']
                post = {'account_url': ACCOUNTS[platform], 'caption': caption,
                        'planned_date_pkt': scheduled_day.isoformat(),
                        'image': str(image), 'image_sha256': file_hash(image),
                        'public_image_url': None, 'sources': topic['sources'],
                        'status': 'draft', 'approval': None}
                post['validated_character_count'] = validate_post(post, platform)
                post['word_count'] = len(caption.split())
                manifest['platforms'][platform] = post
            atomic_json(manifest_path, manifest)
        for platform in PLATFORMS:
            post = manifest['platforms'][platform]
            relative = Path(post['image']).relative_to(destination).as_posix()
            cards.append(f'<article data-platform="{platform}"><h2>{html.escape(str(scheduled_day))} | {platform.title()}</h2>'
                         f'<p>{html.escape(topic["headline"])}</p>'
                         f'<a href="{html.escape(post["account_url"], quote=True)}" rel="noreferrer">Intended account</a>'
                         f'<img loading="lazy" src="{html.escape(relative, quote=True)}" alt="Generated expression portrait with a short educational headline">'
                         f'<p>{post["word_count"]} words | {post["validated_character_count"]} conservative characters | Draft</p>'
                         f'<pre>{html.escape(post["caption"])}</pre>'
                         '<details><summary>Reference URLs</summary>' + ''.join(
                             f'<p><a href="{html.escape(url, quote=True)}" rel="noreferrer">{html.escape(url)}</a></p>' for url in post['sources']) + '</details></article>')
            rows.append({'date_pkt': scheduled_day.isoformat(), 'platform': platform,
                         'topic_id': topic['id'], 'goal': topic['goal'], 'status': 'draft',
                         'post_url': '', 'published_at': '', 'reach': '', 'reactions': '',
                         'comments': '', 'shares': '', 'qualified_enquiries': '',
                         'consultations': '', 'paid_work': '', 'revenue_pkr': ''})
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' file:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Kreafy - unpublished campaign previews</title><style>
body{margin:0;background:#0f0f0f;color:#f7f5ef;font:16px/1.6 system-ui}header{padding:32px;max-width:1000px;margin:auto}h1,h2{color:#c8a96b}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,370px),1fr));gap:24px;padding:24px}article{background:#191919;border:1px solid #444;border-radius:12px;padding:22px;min-width:0}img{width:100%;max-height:500px;object-fit:contain;margin:18px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}a{color:#e4c98f}details{overflow-wrap:anywhere}</style>
<header><h1>TheAleBuilds x Kreafy</h1><p>12 original topics / 48 platform drafts. Nothing is published by this report.</p>
<p>Facebook + Instagram: Roman Urdu. LinkedIn + X: English. Topic-matched portraits from the 22-image bank are fitted without cropping. These are AI-generated assets made using the three user-approved face references; likeness is not guaranteed. Preparation does not regenerate faces. Final platform previews still require approval. Dates are a proposed PKT editorial calendar, not publishing reservations.</p>
<p>Source links require current-context review before approval. Metrics remain unknown until observed. This file has no login, approval, publishing, analytics or external script.</p></header><main>'''
    (destination / 'index.html').write_text(page + '\n'.join(cards) + '</main></html>', encoding='utf-8')
    scorecard = destination / 'scorecard.csv'
    if not scorecard.exists():
        with scorecard.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    atomic_json(destination / 'campaign.json', {'start': str(days[0]), 'end': str(days[-1]),
                'topics': len(TOPICS), 'drafts': len(rows), 'manifests': [str(p) for p in manifest_paths],
                'next_step': 'Review; publish only after separate platform approval. Never recycle this finite bank as new research.'})
    return manifest_paths
