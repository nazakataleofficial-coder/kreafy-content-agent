# Buffer carousel and PDF delivery

This extends the existing publisher. It does not activate scheduled publishing, a Drive trigger, or a new integration. The draft-only Actions workflow stays unchanged.

## Supported delivery

- Instagram: ordered PNG images (application cap: 10).
- LinkedIn: ordered PNG images (cap: 20), or one PDF with a title and PNG thumbnail.
- X: up to four PNG images, with the existing conservative caption limit.
- Facebook personal/professional profile: native Facebook only; no silent Page substitution.

The existing single-image manifests continue to work. Their duplicate-prevention keys are unchanged. Use either the legacy image fields or the new `assets` array, never both.

An image asset has `type: image`, `path`, `sha256`, and `url`. A PDF asset has `type: document`, those same fields, `title`, and `thumbnail: {path, sha256, url}`. Paths are relative to the process working directory or absolute. Asset order is slide order. PNG/PDF bytes and the thumbnail are checked against their approved hashes; no resizing or face generation occurs here. Local file checks verify signatures and size, not a complete PDF parser; malformed documents can still be rejected by Buffer.

Every public URL must point at this repository's immutable 40-character commit SHA. Private Drive share pages are not media URLs. Only final, user-approved export assets should be hosted publicly; source/private folders remain private. This implementation does not change Drive permissions or upload files automatically.

Example platform entry (placeholder hashes and URLs are intentionally not executable):

```json
{
  "account_url": "https://www.linkedin.com/in/nazakat-ale/",
  "caption": "Authentication verifies identity. Authorization decides permitted access.",
  "sources": ["https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html"],
  "delivery_mode": "shareNow",
  "assets": [{
    "type": "document",
    "path": "approved-sample/linkedin.pdf",
    "sha256": "ACTUAL_FILE_SHA256",
    "url": "IMMUTABLE_PUBLIC_PDF_URL",
    "title": "Authentication vs Authorization",
    "thumbnail": {
      "path": "approved-sample/slide-01.png",
      "sha256": "ACTUAL_THUMBNAIL_SHA256",
      "url": "IMMUTABLE_PUBLIC_PNG_URL"
    }
  }]
}
```

## Operator sequence

1. Finalize the existing sample assets, platform captions, exact target and delivery mode. Inspect the slides/PDF before recording the user's approval. Use a separate manifest entry for every platform. Changing any approved field invalidates approval.
2. `python -m studio validate MANIFEST --platform instagram`
3. After actual user approval: `python -m studio approve MANIFEST --platform instagram`
4. With the existing authorized environment: `python -m studio preflight MANIFEST --platform instagram`. This is read-only: checks account identity/connection, every public asset, and the channel's Buffer history for possible duplicates. No post is created.
5. Run `python -m studio queue MANIFEST --platform instagram --journal /persistent/private/delivery.sqlite3` with `KREAFY_PUBLISH_ENABLED=true` only for the authorized send. The manifest selects `addToQueue` (default), `shareNow`, or `customScheduled` with a future timezone-aware `due_at`. The command name stays compatible with old callers.
6. `python -m studio refresh MANIFEST --platform instagram --journal /persistent/private/delivery.sqlite3` reads the known provider post. It never retries publishing.
7. Verify native account appearance and use the existing `record-publication` command for final visual verification. API evidence does not pretend to be a native preview or visual check.

Required existing environment: `BUFFER_ACCESS_TOKEN` and the relevant `BUFFER_INSTAGRAM_ID`, `BUFFER_LINKEDIN_ID`, or `BUFFER_TWITTER_ID`. `BUFFER_ORGANIZATION_ID` is optional: the publisher resolves a unique matching organization through read-only API calls when it is absent. No token is printed or placed in a manifest.

## Receipt meanings

| State | Meaning |
|---|---|
| queued / submitted | Buffer returned a post ID; this is not proof of publication |
| unknown / attempting | Delivery may have succeeded; no automatic resend |
| failed | Buffer reports an error; no automatic retry |
| provider_sent | Buffer reports sent, a timestamp and public URL, and the returned account/caption/media URLs match; native appearance is not yet verified |
| needs_review | Provider evidence is incomplete or content was changed/transformed |
| published | Explicit native account/caption/media verification was recorded |

The refresh command stores provider URL/time separately from the operator-verified URL/time. Unknown metrics remain null. Original submit receipts are preserved, and concurrent receipt changes are not overwritten. If Buffer rewrites asset URLs or captions, refresh conservatively requests review.

Keep one backed-up, durable SQLite journal. A different or lost journal weakens duplicate protection. The secondary Buffer scan checks all returned history up to 1,000 posts, including errors/drafts, and stops if pagination is incomplete. It conservatively flags matching captions or matching ordered public asset URLs. It cannot detect all native posts outside Buffer or edits that change both captions and URLs. This is not a cross-system exactly-once guarantee.

The temporary-render cleanup continues to retain carousel/PDF packs. Provider-only evidence never authorizes deletion. Existing source images and original PDFs are not deleted.

## 90-day system decision

Keep Drive as the content bank, a calendar as the plan, and Buffer as the delivery route for the three existing accounts. A future refiller should add only approved near-term entries within available queue slots and reconcile receipts. Three months of stored content does not mean three months fit in Buffer's free queue at once.

Google Apps Script is a possible alternative cloud runner, but it is not installed or connected by this change. Building a second publisher now would duplicate the existing Python validation/journal logic. The existing GitHub workflow still prepares drafts only; it does not yet refill queues or provide durable cross-run delivery storage. Decide and test that storage/runtime before enabling unattended scheduling.

The supplied conversation reports a Facebook Professional Dashboard and Planner. Those reports do not establish the account's current scheduling availability, supported media types or scheduling horizon. A native scheduling test remains required. No 90-day Facebook scheduling promise is made.

## Sources and verification boundary

Official documentation checked 2026-11-01:

- https://developers.buffer.com/reference — CreatePostInput, AssetInput, DocumentAssetInput, PostInput, PostsInput and post statuses.
- https://buffer.com/pricing — three free channels, ten scheduled posts per channel, API quotas.
- https://support.buffer.com/articles/using-facebook-with-buffer-jY1AM9fz2G — profiles unsupported.
- https://developers.google.com/apps-script/guides/triggers/installable — time-driven triggers can run at slightly randomized times.
- https://developers.google.com/apps-script/guides/services/quotas — quotas and execution limits apply.

Local tests cover ordered carousels, PDF payloads, mode/approval binding, malformed assets, duplicate pagination, legacy journal compatibility, failed/unknown delivery and read-only provider reconciliation. Transport responses in these tests are fixtures. A successful live carousel/PDF mutation and native publication verification are still required before calling this production-verified.
