# Stripe Network Policy After

## Effective policy

- Source config:
  - `STRIPE_TIMEOUT_SECONDS`, default `10`, minimum `1`.
  - `STRIPE_MAX_NETWORK_RETRIES`, default `2`, minimum `0`.
- SDK owner:
  - `backend/app/infra/stripe/client.py` applies both values to `stripe.StripeClient`.
- Cache key:
  - `api_key`, `stripe_api_version`, `stripe_timeout_seconds`, `stripe_max_network_retries`.

## Runtime and guard evidence

- `pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` passed: 90 tests.
- `pytest -q` passed: 3575 passed, 12 skipped.
- `ruff check .` passed.
- Ownership scan:
  - `app/infra/stripe/client.py` owns `StripeClient`, `timeout`, and `max_network_retries`.
  - Additional `timeout` hits are existing LLM/natal API error-code references, not Stripe network policy.
- Boundary scan:
  - No hits for `from app.api|import app.api|HTTPException|JSONResponse|fastapi` in billing services, infra Stripe or startup.

## Decisions

- Startup portal validation remains fail-open in `warn` mode and fail-closed in `strict` mode.
- Webhook upgrade hydration remains fail-closed/retryable on transient Stripe failure.
