# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/core/config.py`
- `.env.example`
- `backend/app/infra/stripe/client.py`
- `backend/app/services/billing/stripe_checkout_service.py`
- `backend/app/services/billing/stripe_customer_portal_service.py`
- `backend/app/services/billing/stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_client.py`
- `backend/app/tests/unit/test_stripe_checkout_service.py`
- `backend/app/tests/unit/test_stripe_customer_portal_service.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `backend/app/tests/integration/test_stripe_checkout_api.py`
- `backend/app/tests/integration/test_stripe_customer_portal_api.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `docs/billing-webhook-local-testing.md`

## Required searches before editing

```powershell
rg -n "STRIPE_API_VERSION|stripe_api_version|stripe_version" backend .env.example docs _condamad
rg -n "app\.integrations\.stripe_client|backend/app/integrations/stripe_client.py|2024-12-18\.acacia" backend docs .env.example _condamad
rg -n "from app\.api|import app\.api" backend/app/services backend/app/domain backend/app/infra backend/app/core
```

## Likely modified files

- `backend/app/core/config.py`
- `.env.example`
- `backend/app/tests/unit/test_stripe_client.py`
- `docs/billing-webhook-local-testing.md`
- `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/evidence/*.md`
- Capsule generated evidence files.

## Forbidden or high-risk files

- `backend/app/integrations/stripe_client.py`
- `frontend/src/api/billing.ts`
- `backend/app/infra/stripe/__init__.py`
