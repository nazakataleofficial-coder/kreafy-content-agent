## Current status — 24 October 2026 PKT

Four native browser posts were verified live on the intended accounts. Original URLs, exact available timestamps, click-time limitations and initial metrics are in [the publication ledger](../data/publications.json). This is not a successful test of the Buffer API adapter. No automatic publishing is enabled.

The offline `status` and `record-publication` commands now support progress inspection and exact-manifest reconciliation with the durable delivery journal. Historical posts lack a manifest fingerprint; their ledger entries do not provide automatic duplicate prevention. The [next phase](NEXT_PHASE.md) supersedes earlier next-step recommendations below. No new poster was generated in this implementation.

---

## Expression bank upgrade — 2026-10-24 PKT

All 22 named portraits in `assets/real_photos` were replaced using the user-approved front, left and right facial references. Full prompts and asset/reference checksums are in `assets/approved_identity/expression-bank.json`; see [gallery and topic mapping](EXPRESSION_BANK.md).

The draft studio selects 12 deliberate expressions for its 12 topics, fitting the full selected portrait without source cropping. Source assets are correctly marked AI-generated; composition performs no additional face generation. All bank/reference hashes are verified before output. No paid API, new integration or social publishing was activated. Individual generated assets were visually reviewed by the assistant; user publishing approval remains per platform.

Earlier notes below describe previous templates and default selection, superseded by this bank.

## Approved identity upgrade — 2026-10-23

The user-approved `image(5).png` is preserved byte-for-byte as
`assets/approved_identity/nazakat-ale-approved.png` (SHA-256
`68ff5338eb4250b855804a2ed6cbd1ab75451d8b3dae4b3a872b72bf7d341486`).
The free studio selects only this reference. The 22 historical images remain
unchanged and are not selected by this workflow. Missing or changed approved
bytes stop preparation without a fallback.

Template v3 keeps the approved photographic region large, removes the previous
checklists/subtitle and uses a short bold headline plus small brand footer.
The original poster's old text is excluded at y=1000; the hair, face, beard and
hand remain in the photo. No face generation, facial retouching or pose variation
is performed. New AI variations require separate visual likeness review.

Validation: 22 local tests pass, all 12 topics / 48 drafts render, and both
portrait/wide exports were visually reviewed. New reference/layout changes create
new content identities; previous approvals cannot approve these new previews.
No new social posts were queued or published by this upgrade.

Earlier implementation notes below describe the previous template and its tests;
this approved identity configuration supersedes their default-photo selection.

# Free Studio — implementation and verification boundary

Prepared 2026-10-23 for Nazakat Ale / TheAleBuilds x Kreafy.

## Implemented

- Offline finite bilingual editorial bank: 12 original topics / 48 drafts.
- Platform-specific account allowlist, length validation and no silent truncation.
  X uses a conservative Unicode upper bound, not a full twitter-text implementation.
- Photo-preserving composition: full existing source asset, no new synthetic face,
  portrait/wide exports, auto-wrapped text, visible three-step educational checklist.
- Hash-named assets and approval fingerprint including caption, target, date,
  source references, local image hash and public image URL.
- No network or billing during draft generation. Legacy model API use opt-in only.
- Read-only HTML review output with no remote scripts/fonts or publishing controls.
- Optional read-only Google Drive image import; not connected or integration tested.
- Guarded Buffer adapter with live channel identity/connection check, pinned image
  verification, required provider ID and separate queued/unknown receipt states.
- Durable SQLite reservation before mutation; timeout, missing ID, crash and any
  prior attempt block automatic re-delivery. No retry loop.
- Free draft-only scheduled workflow proposed in place of the older direct queue.
  No token secrets, media publishing, Telegram alerts or paid model step.
- Unknown KPI fields blank. Re-running preparation preserves existing scorecard data.

## Tested locally

The repository test suite covers all 48 captions, no-permission/no-approval network
blocking, stale approval detection, source/image validation, Unicode length bounds,
wrong-account/paused/disconnected channel rejection, duplicate prevention,
uncertain-delivery persistence, missing provider IDs, Facebook profile restrictions,
legacy model billing guards, public asset pinning, complete image corners in both
ratios, repeat preparation, preserved approvals/KPIs and source photo integrity.

The full seed campaign was rendered and sampled visually as portrait/wide contact
sheets. This is asset/layout QA, not native Facebook/Instagram/LinkedIn/X preview QA.

## Not verified / not activated

- No new social post, schedule, follow, like, message or account setting was changed.
- No Buffer token, channel authorization, live mutation or publication test was used.
- No Google Drive access or sharing was created. No Drive files were downloaded.
- No Cloudflare site/Worker/DB, OAuth app or other integration was deployed.
- No production worker with shared journal or live publication-status reconciliation.
- No engagement, lead, booking, revenue or CTR improvement has been measured.
- No claim that every photo in `assets/real_photos` has the exact same identity.
- Source links are contextual references; new policy claims require current review.

## Free constraints

ChatGPT Plus does not include ordinary model API billing. Existing repo secrets do
not prove a Gemini model call is free. The scheduled free preparation route uses
neither model provider. It is a finite curated bank, not endless fresh AI research.

Buffer Free: three channels, ten queued posts per channel, replenishing slots.
The user's Facebook professional profile is not a supported Buffer destination.
A custom Cloudflare/GitHub/Drive dashboard cannot bypass social-network access,
OAuth permissions or API pricing. X direct API is not treated as a zero-cost route.
Cloudflare Workers can coordinate lightweight work within quotas; heavy video or
image-model rendering is not promised on its free tier.

## Recommended next integration phase

Keep the current public website and account connections unchanged until scope and
permissions are explicitly approved. Check existing Buffer channel identities with
read-only access, host only approved assets immutably, then obtain approval for one
specific native preview on each platform before a real delivery test. Cloudflare
backend and Drive folder automation should only follow identified authorized
resources; no account token belongs in a browser bundle or public repository.
