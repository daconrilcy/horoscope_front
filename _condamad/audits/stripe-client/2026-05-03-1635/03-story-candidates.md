# Story Candidates - stripe-client

No new story candidates.

## Rationale

- F-001 is a resolved prior data-integrity risk with passing regression coverage.
- F-002 is a resolved prior runtime-contract drift with passing client/config tests.
- F-003 is a resolved prior duplicate-responsibility risk with registry parity coverage.
- F-004 is a resolved prior boundary violation with active no-legacy and constructor uniqueness guards.
- F-005 is a positive no-legacy/security observation and does not require implementation work.

## Future guardrail candidates

No regression-guardrail update was written during this audit. The existing guards already cover the relevant boundaries:

- `RG-004` - centralized API error envelope.
- `RG-005` - API must not own service/business logic.
- `RG-006` - services/domain/infra/core must not import `app.api`.
- `RG-023` - root scripts remain owned.
- `RG-024` - Stripe local listener remains opt-in through the local dev stack.

If a future story changes the Stripe supported-event registry, it should consider adding a dedicated guardrail that names `backend/app/services/billing/stripe_webhook_events.py` as the canonical owner.
