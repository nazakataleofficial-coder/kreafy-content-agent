# Private lead tracking

The new offline commands record observed business outcomes without reading inboxes, connecting another service, sending messages or publishing. No actual leads or payments have been seeded.

```sh
python -m studio lead-scorecard
```

With no observations, business metrics are null (unknown), not invented zeroes. The recorded-lead count describes only this local log. Once observations exist, stage counts describe recorded evidence only, not complete business totals or current live analytics.

`record-lead` stores opaque IDs, service, platform, observed time, evidence type, stage and optional post attribution. It does not accept names, emails, phone numbers or message text. The default database is `studio-private/leads.sqlite3`, already excluded from Git. Keep it private and backed up; do not upload it as a public Actions artifact.

## Evidence definitions

- `enquiry`: someone actually asks about a relevant Kreafy service; a generic comment is insufficient.
- `qualified`: service need and a plausible buying discussion are confirmed. A like/follow alone is insufficient.
- `booked`: a consultation date/time is agreed; do not create calendar invitations automatically.
- `won`: paid work is confirmed. Record actual received PKR only when known, not quoted project value, promised income or inferred revenue.
- `lost`: enquiry did not proceed. Closed leads cannot be counted as won again in the same log.

An enquiry must be recorded first; qualification precedes bookings/wins. Bookings are optional before a win. Repeated stages, chronology reversals and silent platform/service reassignment are rejected. Each won amount is counted once. Unknown amounts remain null, and the scorecard states how many won entries have a known amount. This is a basic outcome log, not an accounting/payment system; later instalments and corrections need a separately designed workflow.

## Operator workflow

Only after an actual observation or explicit user report:

```sh
python -m studio record-lead --platform instagram --service video-editing \
  --stage enquiry --observed-at ACTUAL_ISO_TIME_WITH_TIMEZONE \
  --evidence operator_observed
```

The command returns a random lead ID. Reuse it with `--lead-id` for later `qualified`, `booked`, `won` or `lost` observations. `--evidence user_reported` explicitly preserves a user-reported observation rather than pretending it was independently verified. Date placeholder above is intentionally invalid until replaced.

Attribution defaults to unknown. Only add `--post-url` with `--attribution direct` when the enquiry is directly tied to that original post, or `self_reported` when the person explicitly named it. Never assign a sale to the latest post merely because it was recent. The platform argument refers to the source platform for that attribution.

For a confirmed win, optional `--amount-pkr` accepts a positive received amount with at most two decimal places. No currency conversion or income estimate is performed. Reading `lead-scorecard` does not create or alter the database. No unattended sync or scraping is implemented.
