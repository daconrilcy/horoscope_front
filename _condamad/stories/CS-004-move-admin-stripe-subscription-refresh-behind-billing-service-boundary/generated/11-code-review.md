# CONDAMAD Code Review

## Review target

- Story: `CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary`
- Source: `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/00-story.md`
- Review date: 2026-05-03
- Verdict: `CLEAN`

## Inputs reviewed

- Story contract and acceptance criteria.
- Generated capsule files `03-acceptance-traceability.md`, `06-validation-plan.md`, `07-no-legacy-dry-guardrails.md`, `10-final-evidence.md`.
- Evidence files `evidence/admin-refresh-baseline.md` and `evidence/admin-refresh-after.md`.
- Regression guardrails registry `_condamad/stories/regression-guardrails.md`.
- Diff for:
  - `backend/app/api/v1/routers/admin/users.py`
  - `backend/app/services/billing/stripe_billing_profile_service.py`
  - `backend/app/tests/integration/test_admin_stripe_actions_api.py`
  - `backend/app/tests/unit/test_api_router_architecture.py`
  - `backend/app/tests/unit/test_stripe_billing_profile_service.py`
  - `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
  - `_condamad/stories/story-status.md`

## Diff summary

- Admin refresh route now delegates to `StripeBillingProfileService.force_admin_subscription_refresh`.
- Billing service owns Stripe client retrieval, `subscriptions.retrieve`, synthetic `admin.forced_refresh` event construction, profile sync and audit recording.
- Integration tests patch the service boundary instead of the route module.
- Unit tests cover service success and expected application errors.
- Architecture test now guards against direct Stripe SDK ownership in API routers.
- SQL allowlist metadata was updated for shifted line numbers in `admin/users.py`.

## Findings

No actionable findings.

## Acceptance audit

- AC1: Passed. The route remains exposed through OpenAPI as `post` and returns the same success payload.
- AC2: Passed. The route no longer imports `get_stripe_client` or calls Stripe subscription retrieval directly; AST guard and scan cover the forbidden route ownership.
- AC3: Passed. The billing service owns the refresh orchestration and is covered by service unit tests.
- AC4: Passed. Missing subscription and missing Stripe client are translated by the route to the expected HTTP errors through `raise_api_error`; generic errors still map to 500.
- AC5: Passed. The billing/infra scan found no `app.api`, FastAPI, `HTTPException`, or `JSONResponse` dependency.

Applicable guardrails:

- `RG-004`: Preserved; service uses application exceptions and the route owns HTTP translation.
- `RG-005`: Preserved; Stripe orchestration moved out of the API route.
- `RG-006`: Preserved; non-API layers do not import `app.api`.

## Validation audit

Reviewer reran the required targeted checks in the venv. All required story validation evidence is present and consistent. Full backend `pytest -q` was not required by the story and remains a documented residual limitation only.

## DRY / No Legacy audit

- No compatibility wrapper, alias, re-export, fallback, or duplicate active implementation was introduced.
- Old test patch target `app.api.v1.routers.admin.users.get_stripe_client` has zero hits.
- Direct Stripe SDK access under `app/api/v1/routers` has zero active hits.

## Commands run by reviewer

From repository root unless noted:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check app/api/v1/routers/admin/users.py app/services/billing/stripe_billing_profile_service.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py
.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/api/v1/routers/admin/users.py app/services/billing/stripe_billing_profile_service.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py
git diff --check
git diff --stat
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py
.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; assert '/v1/admin/users/{user_id}/refresh-subscription' in app.openapi()['paths']; print(sorted(app.openapi()['paths']['/v1/admin/users/{user_id}/refresh-subscription'].keys()))"
cd backend; rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" app/api/v1/routers
cd backend; rg -n "app\.api\.v1\.routers\.admin\.users\.get_stripe_client" app/tests
cd backend; rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe -g "*.py"
```

Results:

- Ruff format check: `5 files already formatted`
- Ruff lint: `All checks passed!`
- `git diff --check`: passed with CRLF warnings only.
- Targeted pytest bundle: `73 passed`
- OpenAPI route check: `['post']`
- Forbidden scans: zero hits.

## Residual risks

- Full backend test suite was not rerun during review; targeted route, service, architecture, OpenAPI and no-legacy checks cover the story scope.

## Verdict

`CLEAN`
