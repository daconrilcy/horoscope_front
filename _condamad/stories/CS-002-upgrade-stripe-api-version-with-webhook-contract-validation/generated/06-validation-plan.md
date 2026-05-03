# Validation Plan

## Environment assumptions

- Python commands run from PowerShell after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.
- No new dependency is allowed.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Stripe client tests | `pytest -q app/tests/unit/test_stripe_client.py` | `backend/` | yes | all tests pass |
| Checkout service contract | `pytest -q app/tests/unit/test_stripe_checkout_service.py` | `backend/` | yes | all tests pass |
| Customer portal service contract | `pytest -q app/tests/unit/test_stripe_customer_portal_service.py` | `backend/` | yes | all tests pass |
| Webhook service contract | `pytest -q app/tests/unit/test_stripe_webhook_service.py` | `backend/` | yes | all tests pass |
| Checkout API contract | `pytest -q app/tests/integration/test_stripe_checkout_api.py` | `backend/` | yes | all tests pass |
| Customer portal API contract | `pytest -q app/tests/integration/test_stripe_customer_portal_api.py` | `backend/` | yes | all tests pass |
| Webhook API contract | `pytest -q app/tests/integration/test_stripe_webhook_api.py` | `backend/` | yes | all tests pass |

## Runtime checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Loaded default settings | `python -c "from app.core.config import Settings; assert Settings().stripe_api_version == '2026-04-22.dahlia'"` | `backend/` | yes | assertion passes |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| API boundary guard | `rg -n "from app\.api|import app\.api" app/services app/domain app/infra app/core` | `backend/` | yes | no service/infra/core/domain imports from `app.api` |
| Legacy Stripe path scan | `rg -n "app\.integrations\.stripe_client|app/integrations/stripe_client.py" app tests ../docs ../.env.example` | `backend/` | yes | no active legacy path hits |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Old default scan | `rg -n "2024-12-18\.acacia" app tests ../.env.example ../docs ../_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation` | `backend/` | yes | only historical baseline/story references remain |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff lint | `ruff check app/infra/stripe/client.py app/core/config.py app/services/billing app/tests/unit/test_stripe_client.py` | `backend/` | yes | no lint errors |
| Ruff format check | `ruff format --check app/infra/stripe/client.py app/core/config.py app/services/billing app/tests/unit/test_stripe_client.py` | `backend/` | yes | files are formatted |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend tests | `pytest -q` | `backend/` | conditional | all tests pass; document if skipped for time/environment |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace or conflict marker errors |
| Worktree status | `git status --short` | repo root | yes | expected dirty files only |
