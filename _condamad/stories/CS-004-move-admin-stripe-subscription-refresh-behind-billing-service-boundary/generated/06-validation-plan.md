# Validation Plan

## Environment assumptions

- Repository root: `c:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Admin Stripe route contract | `pytest -q app/tests/integration/test_admin_stripe_actions_api.py` | `backend/` | yes | all tests pass |
| Billing service use case | `pytest -q app/tests/unit/test_stripe_billing_profile_service.py` | `backend/` | yes | all tests pass |
| API router architecture guard | `pytest -q app/tests/unit/test_api_router_architecture.py -k "stripe_sdk or service_modules_do_not_import_fastapi_or_wildcards"` | `backend/` | yes | selected guards pass |
| OpenAPI route presence | `python -c "from app.main import app; assert '/v1/admin/users/{user_id}/refresh-subscription' in app.openapi()['paths']"` | `backend/` | yes | assertion passes |

## Unit tests

See targeted checks.

## Integration tests

See targeted checks.

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| API router Stripe ownership guard | `pytest -q app/tests/unit/test_api_router_architecture.py -k stripe_sdk` | `backend/` | yes | guard passes |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Direct Stripe in API routers | `rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" app/api/v1/routers` | `backend/` | yes | zero active hits |
| Old route patch target | `rg -n "app\.api\.v1\.routers\.admin\.users\.get_stripe_client" app/tests` | `backend/` | yes | zero active hits |
| Service HTTP/API dependency scan | `rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe -g "*.py"` | `backend/` | yes | no forbidden service/infra dependency hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff format | `ruff format app/api/v1/routers/admin/users.py app/services/billing/stripe_billing_profile_service.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py` | `backend/` | yes | files formatted |
| Ruff lint | `ruff check app/api/v1/routers/admin/users.py app/services/billing/stripe_billing_profile_service.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend targeted regression bundle | `pytest -q app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py` | `backend/` | yes | all tests pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace/conflict-marker errors |
| Worktree status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

- Full backend `pytest -q` may be skipped if targeted and architecture suites pass and runtime constraints make the full suite too expensive for this story.
