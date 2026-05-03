# Stripe API Version After Upgrade

## Target

- Runtime default after implementation: `2026-04-22.dahlia`
- Installed Stripe SDK version: `14.4.1`
- SDK decision: keep `stripe==14.4.1`; the local contract tests prove the SDK client receives `stripe_version=2026-04-22.dahlia` and billing/webhook payload assumptions remain stable.

## Webhook endpoint expectation

Stripe Dashboard webhook endpoints should be configured on API version `2026-04-22.dahlia`. The backend consumes the existing event fields `id`, `type`, `data.object`, `customer`, and `client_reference_id`; no public billing response schema change is expected.

## Rollback guidance

If the production Stripe Dashboard endpoint cannot be aligned immediately:

1. Set `STRIPE_API_VERSION=2024-12-18.acacia` explicitly in the affected runtime environment.
2. Restart the backend so the cached Stripe SDK client is rebuilt.
3. Rerun the checkout, customer portal, invoice preview, subscription upgrade, and webhook validation commands before deployment.
4. Remove the override after the Dashboard endpoint is upgraded to `2026-04-22.dahlia`.

## Validation result

- `pytest -q app/tests/unit/test_stripe_client.py`: PASS, 5 tests.
- `pytest -q` targeted Stripe unit and integration subset: PASS, 107 tests.
- `ruff check` targeted backend Stripe/config files: PASS.
- Runtime default check with `APP_DISABLE_BACKEND_DOTENV=1`: PASS.
- Full root `pytest -q`: PASS on user rerun after root pytest fixes, 3552 passed and 12 skipped.
