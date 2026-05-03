# No Legacy / DRY Guardrails

## Canonical ownership

- HTTP status mapping for `/v1/billing/stripe-webhook`: `backend/app/api/v1/routers/public/billing.py`
- Stripe webhook business processing: `backend/app/services/billing/stripe_webhook_service.py`
- Stripe webhook idempotency state: `backend/app/services/billing/stripe_webhook_idempotency_service.py`
- Centralized error envelope: `app.api.errors` via `_raise_error` / `ApplicationError`

## Forbidden legacy behavior

- `failed_internal` returned as HTTP 200 for signed processing failure.
- `JSONResponse` local construction in `backend/app/api/v1/routers/public/billing.py`.
- `from app.api` or `import app.api` inside `backend/app/services`, `backend/app/domain`, `backend/app/infra`, or `backend/app/core`.
- Duplicate webhook route, second idempotency table, compatibility wrapper, alias, shim, or silent fallback.

## Applied regression guardrails

- `RG-004`: centralized API errors preserved.
- `RG-005`: route remains HTTP adapter; business/idempotency logic remains in services.
- `RG-006`: non-API layers do not import `app.api`.
- `RG-024`: local Stripe listener remains opt-in; docs update does not alter `scripts/start-dev-stack.ps1`.

## Negative evidence

| Pattern | Evidence | Classification | Status |
|---|---|---|---|
| `failed_internal.*HTTP 200\|HTTP 200.*failed_internal\|JSONResponse` | Targeted `rg` over route, billing services, webhook tests, and docs returned zero hits. | active legacy removed | PASS |
| `from app\.api\|import app\.api` in non-API layers | Targeted `rg` over `backend/app/services`, `domain`, `infra`, `core` returned zero hits. | boundary preserved | PASS |
| `app.integrations.stripe_client` | `pytest -q app/tests/unit/test_stripe_client.py::test_legacy_integrations_stripe_client_module_is_absent` passes. | legacy module absent | PASS |

## DRY review

- No second webhook route was added.
- No second idempotency mechanism was added.
- Existing `StripeWebhookIdempotencyService` failed-row reclaim behavior is reused.
- Existing centralized error handling is reused; no local JSON error builder was introduced.
