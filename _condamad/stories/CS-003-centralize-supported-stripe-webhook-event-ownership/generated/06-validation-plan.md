# Validation Plan

## Environment assumptions

- Commands run on Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Python working directory for backend checks: `backend`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint changed backend files | `ruff check app/services/billing/stripe_webhook_events.py app/services/billing/stripe_webhook_service.py app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` | `backend` | yes | no lint errors |
| Unit tests | `pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py` | `backend` | yes | all tests pass |
| Integration tests | `pytest -q app/tests/integration/test_stripe_webhook_api.py` | `backend` | yes | all tests pass |
| Combined targeted suite | `pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` | `backend` | yes | all tests pass |
| OpenAPI path unchanged | `python -c "from app.main import app; assert '/v1/billing/stripe-webhook' in app.openapi()['paths']"` | `backend` | yes | assertion passes |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Target event scan | `rg -n "subscription_schedule|checkout.session.async_payment_succeeded" app/services/billing ../docs ../scripts app/tests` | `backend` | yes | hits are canonical registry, docs, script/tests/evidence only |
| API import boundary | `rg -n "from app\.api|import app\.api" app/services app/domain app/infra app/core` | `backend` | yes | no service/domain/infra/core imports from API |
| Forbidden shell listener | `rg -n "stripe-listen-webhook\.sh" ../scripts ../docs app/tests` | `backend` | yes | no active support hits |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | only story files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace/conflict errors |
| Final status | `git status --short` | repo root | yes | expected files only |

## Rule for skipped commands

If a command cannot be run, record exact command, reason, risk, and compensating evidence in `10-final-evidence.md`.
