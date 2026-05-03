# After admin refresh ownership

## Runtime route

- `python -c "from app.main import app; assert '/v1/admin/users/{user_id}/refresh-subscription' in app.openapi()['paths']"` passed from `backend/` after venv activation.
- `pytest -q app/tests/integration/test_admin_stripe_actions_api.py` passed: `6 passed`.

## Ownership after implementation

- `backend/app/api/v1/routers/admin/users.py` delegates refresh orchestration to `StripeBillingProfileService.force_admin_subscription_refresh`.
- `backend/app/services/billing/stripe_billing_profile_service.py` owns Stripe client retrieval, `subscriptions.retrieve`, `admin.forced_refresh` event construction, billing profile sync and audit recording.
- Integration tests patch `app.services.billing.stripe_billing_profile_service.get_stripe_client`, not the route module.

## Reintroduction guard

- `pytest -q app/tests/unit/test_api_router_architecture.py -k "stripe_sdk or service_modules_do_not_import_fastapi_or_wildcards"` passed: `2 passed, 53 deselected`.
- `rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" app/api/v1/routers` returned zero hits.
- `rg -n "app\.api\.v1\.routers\.admin\.users\.get_stripe_client" app/tests` returned zero hits.
- `rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe -g "*.py"` returned zero hits.

## Allowed differences

- `backend/app/tests/unit/test_api_router_architecture.py` now includes a Stripe SDK ownership guard.
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` line-number metadata for `admin/users.py` was updated because this story changed that file's line layout; no new SQL debt was added.
