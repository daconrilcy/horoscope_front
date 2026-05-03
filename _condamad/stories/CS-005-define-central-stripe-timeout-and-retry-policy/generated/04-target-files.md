# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/infra/stripe/client.py`
- `backend/app/core/config.py`
- `.env.example`
- `backend/app/services/billing/stripe_checkout_service.py`
- `backend/app/services/billing/stripe_customer_portal_service.py`
- `backend/app/services/billing/stripe_billing_profile_service.py`
- `backend/app/startup/stripe_portal_validation.py`
- `backend/app/tests/unit/test_stripe_client.py`
- `backend/app/tests/unit/test_stripe_checkout_service.py`
- `backend/app/tests/unit/test_stripe_customer_portal_service.py`
- `backend/app/tests/unit/test_stripe_portal_startup_validation.py`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`

## Required searches

```powershell
rg -n "timeout|max_network_retries|StripeClient\(" app/infra/stripe app/services/billing app/api/v1/routers app/startup -g "*.py"
rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe app/startup -g "*.py"
```

## Likely modified files

- `backend/app/core/config.py`
- `backend/app/infra/stripe/client.py`
- `.env.example`
- `backend/app/services/billing/stripe_billing_profile_service.py`
- `backend/app/tests/unit/test_stripe_client.py`
- `backend/app/tests/unit/test_stripe_checkout_service.py`
- `backend/app/tests/unit/test_stripe_customer_portal_service.py`
- `backend/app/tests/unit/test_stripe_portal_startup_validation.py`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`

## Forbidden unless justified

- `frontend/src/**`
- `backend/pyproject.toml`
- `requirements.txt`
- Nouveau wrapper Stripe hors `backend/app/infra/stripe/client.py`
