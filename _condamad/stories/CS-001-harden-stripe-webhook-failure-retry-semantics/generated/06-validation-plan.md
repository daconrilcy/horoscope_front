# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Backend commands run after `.\.venv\Scripts\Activate.ps1`
- Backend working directory for Python commands: `backend`

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Baseline signed failure contract | `pytest -q app/tests/integration/test_stripe_webhook_api.py::test_webhook_business_failure_persists_failed_and_retry_is_accepted` | `backend` | yes-before-edit | Existing HTTP 200 baseline captured before runtime edit. |
| Webhook behavior and idempotency | `pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_idempotency_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend` | yes | Signed processing failure returns retryable non-2xx and redelivery succeeds. |
| Stripe legacy guard regression | `pytest -q app/tests/unit/test_stripe_client.py::test_legacy_integrations_stripe_client_module_is_absent` | `backend` | yes | Legacy `app.integrations.stripe_client` remains absent. |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| API error and non-API import boundary | `pytest -q app/tests/unit/test_api_error_architecture.py app/tests/unit/test_api_router_architecture.py::test_non_api_layers_do_not_import_api_package` | `backend` | yes | Centralized error and non-API import guards pass. |
| Exact SQL debt allowlist | `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist` | `backend` | yes | Touched route line numbers match the existing allowlist, with no new SQL debt. |
| Runtime OpenAPI contract | `python -c "from app.main import app; schema = app.openapi(); assert '/v1/billing/stripe-webhook' in schema['paths']; assert '500' in schema['paths']['/v1/billing/stripe-webhook']['post']['responses']"` | `backend` | yes | Webhook path and retryable 500 response are declared. |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Non-API layers must not import API | `rg -n "from app\.api\|import app\.api" backend\app\services backend\app\domain backend\app\infra backend\app\core` | repo root | yes | Zero hits. |
| No HTTP 200 failed-internal wording or local JSONResponse | `rg -n "failed_internal.*HTTP 200\|HTTP 200.*failed_internal\|JSONResponse" backend\app\api\v1\routers\public\billing.py backend\app\services\billing backend\app\tests\integration\test_stripe_webhook_api.py backend\app\tests\unit\test_stripe_webhook_service.py docs\billing-webhook-idempotency.md docs\billing-webhook-local-testing.md` | repo root | yes | Zero hits. |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted format check | `ruff format --check app/api/v1/routers/public/billing.py app/services/billing/stripe_webhook_service.py app/services/billing/stripe_webhook_idempotency_service.py app/tests/integration/test_stripe_webhook_api.py app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_idempotency_service.py app/tests/unit/test_stripe_client.py` | `backend` | yes | Files are formatted. |
| Full backend lint | `ruff check .` | `backend` | yes | No lint errors. |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend test suite | `pytest -q` | `backend` | yes | Full suite passes. |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | Only story-related tracked files plus pre-existing dirty files are visible. |
| Whitespace/conflict marker check | `git diff --check` | repo root | yes | No whitespace errors. |
| Worktree status | `git status --short` | repo root | yes | Expected story changes and pre-existing dirty story files only. |
