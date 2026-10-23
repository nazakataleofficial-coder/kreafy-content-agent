# TheAleBuilds x Kreafy — Free Draft Studio

An original, finite content-preparation system for Nazakat Ale and Kreafy.
**Preparation is offline and uses no model API or additional subscription.**
No reach, engagement, monetization, revenue, face-generation or zero-maintenance
claim is made. This is a tested preparation upgrade, not a verified live publisher.

## Publication tracking and next phase

Four manually published native posts are recorded in [data/publications.json](data/publications.json), with original URLs and timestamp limitations. This verifies the browser workflow only, not the Buffer API adapter. Initial metrics are observations, not growth results. See the [current implementation plan](docs/NEXT_PHASE.md).

```sh
python -m studio status
```

Status is offline: it reads recorded evidence and optional local delivery receipts, without refreshing analytics. Historical posts have no manifest fingerprint and are not automatically deduplicated. Future native publications can be reconciled against an approved manifest using `record-publication`; see the plan. Nothing is sent by either command.

## Current workflow

The proposed replacement daily workflow prepares unpublished campaign previews on
Monday, Wednesday and Friday. It uses no secrets, does not change Google Drive
sharing, does not push generated media, does not send notifications and does not
queue or publish posts. GitHub Actions timing is best effort, not an exact timer.
The workflow is checked into the default branch; actual runs and artifacts must be checked in Actions.

- 12 original topics, each adapted to four platforms: 48 drafts.
- Facebook and Instagram: Roman Urdu. LinkedIn and X: English.
- Portrait 1080x1350 and wide 1200x675 PNG exports: large photo, short bold headline, small brand footer. Detailed diagnostic advice stays in captions.
- Identity references: the user-approved front poster plus approved left/right views in `assets/approved_identity/`. Each is checksum-bound in `expression-bank.json`.
- All 22 `assets/real_photos/*.png` portraits have been replaced with newly generated office portraits using those references: Pakistani shalwar kameez, consistent warm office, silver Dell laptop, navy mug/coaster, tan notebook and black pen. They are AI-generated, not photographs of real documented events. Small visual differences remain possible.
- Each campaign topic selects an intentional expression. The complete selected photo is fitted without cropping or regeneration during offline preparation. All 22 file hashes and the three reference hashes are checked first; missing/changed files stop generation without a legacy fallback.
- Source references were approved by the user; individual generated assets received assistant visual review. This does not approve any platform post or guarantee a biometric match. Final publishing still requires separate platform-preview approval.
- No image generation API is called by the automated workflow. The checked-in finite portrait bank is reused offline. Old versions remain in Git history.
- Local read-only HTML review report, planned PKT calendar and blank KPI scorecard.
- Exact-content, per-platform approvals; changed content invalidates approval.
- Optional Buffer queue adapter checks account identity and connection state,
  verifies immutable public image bytes and records a durable no-retry receipt.
- Optional Google Drive image importer uses read-only scope, private local output,
  file limits and checks. It does not create a connection or choose an asset for use.

## Prepare locally

Python 3.11+ and a readable TrueType font (DejaVu Sans on Linux or Arial on Windows):

```sh
python -m pip install -r requirements-free.txt
python -m unittest discover -s tests -v
python -m studio prepare --start 2026-10-26
```

Open `studio-output/index.html`. The first 12 Mon/Wed/Fri dates are editorial
suggestions, not reserved posting slots. Nothing is sent. Preparation can rerun
without overwriting existing approvals, changed caption drafts or KPI entries.
The bank is finite; it must not be recycled and called fresh audience research.

## Delivery boundaries

The earlier automatic `poster/buffer_poster.py` entry point is blocked. Its legacy
code is retained as a reference, not as an alternative unapproved posting path.
The legacy model generators require explicit `KREAFY_ALLOW_BILLABLE_APIS=true`;
the free workflow never sets it or provides API keys. No paid fallback runs there.

Queueing requires all of the following:

1. A separately approved platform preview, with image and target account verified.
2. An authorized, connected Buffer channel on the existing free plan.
3. The reviewed image hosted at a full-commit-SHA-pinned public repository URL.
4. `BUFFER_ACCESS_TOKEN`, `BUFFER_ORGANIZATION_ID`, platform channel ID and a
   persistent, backed-up SQLite journal. Never put credentials in files or chat.
5. A live integration test after specific posting approval. No such test was run
   as part of this upgrade.

A `public_image_url` is added to a manifest **before** approval. Changing it,
caption, date, account or asset hash invalidates that approval.

```sh
python -m studio validate /path/to/manifest.json --platform linkedin
# Only after the user approves that exact LinkedIn preview:
python -m studio approve /path/to/manifest.json --platform linkedin
# Only with authorized existing credentials and an explicit delivery enable:
# KREAFY_PUBLISH_ENABLED=true python -m studio queue /path/to/manifest.json --platform linkedin
```

`queue` adds to the channel's existing Buffer queue. It does NOT honor the proposed
calendar date as an exact publishing time, schedule a thread, or enable a boost.
A returned provider ID means **queued**, not published. A timeout or missing ID
becomes `unknown`; reruns are blocked even if the caption is reapproved or its date
changes. Final live account appearance, public URL and publication time remain
unknown until independently checked. There is no production scheduled delivery
workflow: a durable shared journal and full live checks must come first.

Facebook's intended target is a professional profile, which Buffer does not
support. The system exports its draft; it never substitutes a Page or another
account. Buffer Free covers only three connected channels. Direct network APIs
are not assumed to be free or approved.

## Optional Google Drive import

Only after separate authorization, with an existing service account given access
to an explicit folder and its JSON supplied through environment secrets:

```sh
python -m studio import-drive --folder AUTHORIZED_FOLDER_ID
```

The optional importer needs the existing Google packages in `requirements.txt`.
It reads only PNG/JPEG files directly inside the folder (no subfolder scan), caps
imports at 50 files and 10 MiB per file, uses hashed local filenames and verifies
image decoding. It never deletes source files, changes sharing, publishes media,
or automatically treats an imported photo as an approved identity reference.
A Drive sharing URL is not assumed to be a suitable public image-delivery URL.

## Research and verification

See [implementation status](docs/FREE_STUDIO_STATUS.md) and
[research references](docs/RESEARCH_REFERENCES.md). Source links in campaign drafts
support context; they are not automatically refreshed, fact-checked by a model,
or proof that a caption is highest-performing. Comments are not a prerequisite
for the proposed enquiry-led content plan.
