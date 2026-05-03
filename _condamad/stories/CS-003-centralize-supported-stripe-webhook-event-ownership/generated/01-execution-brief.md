# Execution Brief — CS-003-centralize-supported-stripe-webhook-event-ownership

## Primary objective

Implement a single canonical Stripe webhook supported-event registry under `backend/app/services/billing` and migrate runtime service, resolver, docs, script and parity tests to it.

## Boundaries

- Keep ownership outside `backend/app/api`.
- Preserve current supported behavior, including explicit classification of async checkout and subscription schedule events.
- Preserve ignored behavior for unsupported events such as `invoice.payment_succeeded`.
- Do not change API error contracts, Stripe API version, or frontend code.

## Done when

- AC1-AC5 are mapped to code and validation evidence.
- Baseline and after evidence artifacts exist.
- Targeted tests, lint, OpenAPI path check, and No Legacy scans are recorded.
- `_condamad/stories/story-status.md` is updated to `ready-to-review`.
