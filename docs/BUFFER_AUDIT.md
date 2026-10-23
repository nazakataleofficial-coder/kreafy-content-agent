# Buffer queue audit — 24 October 2026 PKT

Source: authenticated existing Chrome session, [Buffer Publish](https://publish.buffer.com/schedule). All **95 queue cards** were loaded and inspected through normal read-only browser controls. The machine-readable snapshot includes each observed internal post ID, UI label, state and exact error in [data/buffer-audit.json](../data/buffer-audit.json).

| Channel | Errored | Scheduled | Total |
|---|---:|---:|---:|
| Instagram / nazakataleofficial | 87 | 4 | 91 |
| LinkedIn / Nazakat Ale | 1 | 0 | 1 |
| X / Kreafyonline | 3 | 0 | 3 |
| Total | 91 | 4 | 95 |

Queue badges include failures; they do not mean 95 posts will publish. Drafts showed 0. The existing organization showed a free plan and 3/3 connected channel slots. This does not validate API tokens or remove historical authorization failures. Facebook is not among these Buffer channels.

## Observed failures

| Displayed failure class | Entries |
|---|---:|
| Authorization lost: refresh channel requested | 70 |
| Instagram potential spam | 14 |
| Attached media/link: possible size or timeout | 2 |
| Media issue: remove and upload again requested | 2 |
| Generic sending trouble | 1 |
| X publishing error | 1 |
| Unknown error | 1 |

These are provider messages, not independently diagnosed root causes. Historical authorization errors do not establish the current authorization state. No refresh, reauthorization, retry, edit or deletion was performed. Spam flags do not prove which caption phrase caused rejection.

## Four scheduled entries requiring a decision

All are Instagram posts on `nazakataleofficial`. Times below are the displayed Asia/Karachi schedule, not actual publication timestamps. No evidence supporting the quoted results was inspected.

| Internal post ID | Scheduled PKT | Visible claim requiring evidence |
|---|---|---|
| `6ad9c68fc0efd57f50735c78` | Oct 24, 06:25 | 30% middleman fees; marketplace built in three weeks |
| `6ad9c690d26c2ef1687f24b7` | Oct 24, 22:39 | Faceless channel makes $8,000/month on complete autopilot |
| `6ad9c69268fbd2404aab2ded` | Oct 25, 09:01 | 3D visuals get 3x more clicks |
| `6ad9c693c0efd57f50735d3c` | Oct 25, 21:17 | Business saved 120 hours every month |

Recommendation: move precisely these four entries to Drafts while checking evidence and rewriting unsupported claims. The native menu exposes **Move to Drafts**. This is a proposed reversible queue change, **not executed or approved by this audit**. Do not pause other channels, delete posts or retry the 91 failures. Recheck each ID/state at action time; if already sent, do not assume moving it can undo publication.

## Copy and conversion findings

- Multiple excerpts use earnings, speed, percentage-lift or client-result claims without evidence available in this audit. Treat them as unverified claims, not real case studies. Do not reuse them as proof in future content.
- Repeated comment-keyword/DM promises appear in the queue. No working automatic response or deliverable was verified. A CTA must describe a real available next step; no automatic DMs are enabled.
- Contradictory positioning appears across excerpts: passive/autopilot promises alongside warnings that YouTube automation is not passive income. Use realistic process descriptions consistently.
- Buffer Home displayed 20 unanswered comments/mentions and weekly comments of 0. These are different UI scopes; neither establishes lead count. No inbox was opened and no messages/comments were sent.
- Relevant enquiries, bookings, paid work and received money remain **unknown**. Do not convert likes, comments or queue counts into business outcomes.

## Verification boundary

All card states and IDs were read. Some captions were collapsed, so this is not a full-caption/media audit. No queued entry was verified as a public social post. Internal Buffer IDs are not original public URLs. Sources are the authenticated queue and each channel's visible queue view; screenshots and private source data are not committed.
