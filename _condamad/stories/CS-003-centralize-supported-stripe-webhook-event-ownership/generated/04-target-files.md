# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/services/billing/stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `scripts/stripe-listen-webhook.ps1`
- `docs/billing-webhook-local-testing.md`
- `docs/stripe-webhook-dev.md`

## Required searches before editing

```powershell
rg -n "subscription_schedule|checkout\.session\.async_payment_succeeded|invoice\.payment_succeeded" backend/app/services/billing backend/app/tests docs scripts
rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/services/billing backend/app/tests docs scripts
rg -n "from app\.api|import app\.api" backend/app/services backend/app/domain backend/app/infra backend/app/core
```

## Likely modified files

- `backend/app/services/billing/stripe_webhook_events.py`
- `backend/app/services/billing/stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `scripts/stripe-listen-webhook.ps1`
- `docs/billing-webhook-local-testing.md`
- `docs/stripe-webhook-dev.md`
- `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/evidence/*.md`

## Forbidden or high-risk files

- `backend/app/api/**` unless an unchanged OpenAPI check exposes a real blocker.
- `frontend/**` because the registry is internal backend.
- Dependency manifests; no new dependency is authorized.
