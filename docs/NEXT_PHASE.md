# Implementation phase after native publication

## Locked decisions

- No new poster generation in this phase. Keep the 22 expression assets and three approved identity references unchanged.
- Approved visual direction is headline over the photo with a consistent face/office. The existing v4 renderer still has a separate text panel: its output is not a newly approved visual template. Do not silently treat scheduled draft artifacts as approved posts.
- Facebook/Instagram copy in Roman Urdu, LinkedIn/X in English; useful diagnosis rather than earnings promises. Each platform needs its own final approval for new content.
- Offline preparation uses the finite checked-in bank; ChatGPT Plus is not an unattended image-generation API. No paid model API, hosting purchase, additional integration or permission expansion.
- Native Facebook posting remains separate. Existing Buffer identities were observed in the browser, but API delivery has not been validated. No automated publisher has been enabled.

## Delivered now

1. Original URLs for the four AI-video monetization posts, correct account identities and known timestamp limitations are committed to `data/publications.json`.
2. `python -m studio status` reads that evidence and, when present, the local persistent delivery journal. It makes no network calls and does not imply fresh analytics.
The existing draft-only Actions artifact also includes `publication-status.json`. It is a saved-evidence report, not live analytics or an approval.

3. `record-publication` reconciles an approved manifest after a human/operator checks the live account, caption and exact image. It can resolve an earlier queued/unknown delivery, preserves the old receipt, and refuses a conflicting published URL.
4. The same account/caption/image fingerprint blocks another queue attempt, including after a date or approval change, before any Buffer network request. Keep one backed-up persistent journal. A different journal loses that protection.

Historical browser posts did not use studio manifests. Their uploaded image bytes were not independently hashed. Their URLs are verified evidence, but cannot safely be invented into exact-content delivery fingerprints. Manually check these four original URLs before considering similar content again.

## Native publication reconciliation

After separately approved publishing, inspect the actual live post, correct account, caption and exact image. Use the corresponding unchanged approved manifest:

```sh
python -m studio record-publication /path/to/manifest.json \
  --platform instagram \
  --url https://www.instagram.com/nazakataleofficial/p/ACTUAL_POST_ID/ \
  --observed-at 2026-10-24T02:00:00+05:00 \
  --account-verified
```

The example date/URL are placeholders, not a real new publication. Add `--published-at` only when the platform exposes the actual server timestamp. A submit-button click is not a publication timestamp. The command records evidence only; it does not publish or grant approval. For Facebook/LinkedIn, post URL syntax alone cannot verify authorship: explicit live-account verification is required.

## Next work in priority order

| Priority | Work | Completion condition |
|---|---|---|
| 1 | Audit existing Buffer errors without retrying | Distinguish failed, queued and uncertain entries; identify claim/media issues. Latest inspection loaded 20 error cards, not an exhaustive audit of every entry. No deletion/retry authorized by this plan. |
| 2 | Connect evidence to qualified leads | Record relevant enquiries, requested service, consultation, paid project and revenue only when observed. No invented zeroes or attributed revenue. |
| 3 | Review the existing 12-topic plan | Choose one audience problem and one useful deliverable per topic; check current sources. Do not recycle the bank as fresh research. |
| 4 | Fix the renderer to the approved overlay direction | Separate implementation review with existing assets; protect face/head, preserve aspect ratio, and obtain actual platform preview approval. No new poster requested now. |
| 5 | Validate an existing delivery route | Only an exact approved platform preview and existing authorized connection; verify resulting live URL before calling it published. No new permissions or integrations. |

## Weekly review

Use the existing `studio-output/scorecard.csv` for reach/views where available, reactions, comments, shares, qualified enquiries, consultations, paid work and revenue. Unknown stays blank. Compare posts at similar ages; record the observation time and original URL. Low comment volume alone is not a failure criterion. Prioritize relevant enquiries and bookings, and test one topic/hook/CTA change at a time. No automatic DMs, comments, follows or reposts.

The 90-day direction remains diagnosis-led educational content, visible practical deliverables and a clear relevant service next step. This file records implementation priorities; it does not claim the earlier research packs were freshly reverified or that any topic guarantees engagement.
