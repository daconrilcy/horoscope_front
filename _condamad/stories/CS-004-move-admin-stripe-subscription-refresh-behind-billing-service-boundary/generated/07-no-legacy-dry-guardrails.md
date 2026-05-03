# No Legacy / DRY Guardrails

## Story-specific forbidden patterns

- `backend/app/api/v1/routers/**` importing `app.infra.stripe.client.get_stripe_client`.
- `backend/app/api/v1/routers/**` calling `stripe_client.subscriptions.retrieve`.
- Tests patching `app.api.v1.routers.admin.users.get_stripe_client` as a nominal path.
- Billing services importing `fastapi`, `HTTPException`, `JSONResponse`, or `app.api`.
- Compatibility wrappers, transitional aliases, re-export modules, silent fallback behavior, or duplicate active implementations.

## Canonical ownership

- Stripe SDK factory: `backend/app/infra/stripe/client.py`.
- Admin billing refresh use case: `backend/app/services/billing/stripe_billing_profile_service.py`.
- HTTP adaptation and admin authorization: `backend/app/api/v1/routers/admin/users.py`.

## Required negative evidence

- AST guard in `backend/app/tests/unit/test_api_router_architecture.py`.
- `rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" app/api/v1/routers` from `backend/`.
- `rg -n "app\.api\.v1\.routers\.admin\.users\.get_stripe_client" app/tests` from `backend/`.
- `rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe -g "*.py"` from `backend/`.

## Exceptions

- Existing Stripe SDK calls in billing services and startup validation are allowed by the story allowlist.
- FastAPI imports in tests are out of the service/infra dependency boundary.

## Review checklist

- One canonical path owns admin refresh orchestration.
- Route remains a thin HTTP adapter.
- No route-owned Stripe client path remains active.
- No service imports FastAPI or API modules.
- Tests fail if direct Stripe SDK calls return to API routers.
