# Baseline admin refresh ownership

## Runtime route

- Command: `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; path='/v1/admin/users/{user_id}/refresh-subscription'; route=app.openapi()['paths'].get(path); print(path in app.openapi()['paths']); print(sorted(route.keys()) if route else [])"`
- Result: `True`, method list `['post']`.

## Direct Stripe ownership before implementation

- Command: `rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" backend/app/api/v1/routers`
- Hits:
  - `backend/app/api/v1/routers/admin/users.py:414`: `stripe_client = get_stripe_client()`
  - `backend/app/api/v1/routers/admin/users.py:420`: `subscription = stripe_client.subscriptions.retrieve(...)`

## Test patch boundary before implementation

- Command: `rg -n "app\.api\.v1\.routers\.admin\.users\.get_stripe_client|refresh-subscription|subscription_refresh_forced" backend/app/tests/integration/test_admin_stripe_actions_api.py`
- Hits:
  - integration test patches `app.api.v1.routers.admin.users.get_stripe_client`
  - integration test covers `/v1/admin/users/{user_id}/refresh-subscription`
  - integration test asserts `subscription_refresh_forced` audit presence.
