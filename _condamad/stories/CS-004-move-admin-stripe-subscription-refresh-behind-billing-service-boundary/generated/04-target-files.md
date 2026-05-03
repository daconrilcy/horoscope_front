# Target Files

## Must inspect before implementation

- `../00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/api/v1/routers/admin/users.py`
- `backend/app/services/billing/stripe_billing_profile_service.py`
- `backend/app/services/billing/stripe_checkout_service.py`
- `backend/app/services/billing/stripe_customer_portal_service.py`
- `backend/app/infra/stripe/client.py`
- `backend/app/tests/integration/test_admin_stripe_actions_api.py`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `backend/app/tests/unit/test_api_router_architecture.py`

## Required searches

- `rg -n "refresh_subscription|refresh-subscription|get_stripe_client|stripe_client|subscription_refresh_forced|admin.forced_refresh" backend/app`
- `rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" backend/app/api/v1/routers`
- `rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" backend/app/services/billing backend/app/infra/stripe -g "*.py"`

## Likely modified files

- `backend/app/api/v1/routers/admin/users.py`
- `backend/app/services/billing/stripe_billing_profile_service.py`
- `backend/app/tests/integration/test_admin_stripe_actions_api.py`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `backend/app/tests/unit/test_api_router_architecture.py`

## Likely deleted files

- None expected.

## Forbidden unless directly justified

- `frontend/src/**`
- `backend/pyproject.toml`
- Other admin endpoints: `reveal-stripe-id`, `assign-plan`, `commercial-gesture`
- New root-level service directories under `backend/`
