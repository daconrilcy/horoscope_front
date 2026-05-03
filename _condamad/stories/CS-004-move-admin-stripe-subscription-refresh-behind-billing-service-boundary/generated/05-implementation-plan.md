# Implementation Plan

## Current architecture finding

- `backend/app/api/v1/routers/admin/users.py` owns Stripe client retrieval and `subscriptions.retrieve` for the admin refresh route.
- `backend/app/services/billing/stripe_billing_profile_service.py` already owns Stripe profile sync via `update_from_event_payload` and is the narrowest canonical billing destination.
- Existing integration tests patch the route-owned Stripe import, which preserves the boundary violation.

## Selected approach

- Add `StripeBillingProfileService.force_admin_subscription_refresh` as the billing/admin use case.
- Add a service-local exception type carrying code/message, without FastAPI imports.
- Keep the route as HTTP adapter: auth, request-id, DB session, service call, error translation, commit, success response.
- Patch Stripe at `app.services.billing.stripe_billing_profile_service.get_stripe_client` in tests.
- Add an AST architecture guard that fails if API routers import/call the Stripe client directly.

## Files to modify

- `backend/app/api/v1/routers/admin/users.py`
- `backend/app/services/billing/stripe_billing_profile_service.py`
- `backend/app/tests/integration/test_admin_stripe_actions_api.py`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `backend/app/tests/unit/test_api_router_architecture.py`

## Tests to add or update

- Update admin integration success test patch boundary.
- Add admin integration tests for missing subscription and missing Stripe client.
- Add unit tests for service-owned refresh success and service error cases.
- Add API router architecture guard for direct Stripe SDK ownership.

## No Legacy stance

- No router-owned Stripe client import remains.
- No wrapper or alias keeps the old route-owned patch path alive.
- The old behavior is preserved only through the HTTP contract, not through duplicate orchestration.

## Rollback strategy

- Revert the five code/test files and remove generated evidence if validation exposes a behavior regression that cannot be fixed within story scope.
