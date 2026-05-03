# Implementation Plan

## Initial repository findings

- `settings.stripe_api_version` currently defaults to `2024-12-18.acacia`.
- `.env.example` currently documents `STRIPE_API_VERSION=2024-12-18.acacia`.
- `backend/app/infra/stripe/client.py` already passes `settings.stripe_api_version` to `stripe.StripeClient`.
- `backend/app/tests/unit/test_stripe_client.py` mocks the old version and guards the legacy integration module absence.

## Proposed changes

- Update the runtime default to `2026-04-22.dahlia`.
- Update `.env.example`.
- Strengthen Stripe client unit tests to assert the SDK receives the configured version.
- Persist baseline and after evidence including SDK version and rollback guidance.
- Update webhook local testing docs with endpoint version expectations.

## Files to modify

- `backend/app/core/config.py`
- `.env.example`
- `backend/app/tests/unit/test_stripe_client.py`
- `docs/billing-webhook-local-testing.md`
- Capsule evidence/traceability files.

## Files to delete

- None expected.

## Tests to add or update

- `backend/app/tests/unit/test_stripe_client.py`

## Risk assessment

- Main risk is Stripe SDK/API version compatibility. Existing mocked service tests prove local contract shape, not live Stripe account behavior.

## Rollback strategy

- Restore `STRIPE_API_VERSION=2024-12-18.acacia` in the runtime environment if Dashboard alignment cannot be completed, then rerun the same Stripe contract tests before deploying.
