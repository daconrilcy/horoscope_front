# Validation Plan - CS-007

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Working directory for Python validation: `backend`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Context loader behavior | `pytest -q app/tests/unit/test_context_loader.py` | `backend` | yes | all tests pass |
| Daily prediction service and guards | `pytest -q app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | yes | all tests pass |

## Integration tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Persistence regression | `pytest -q app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py` | `backend` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden infra imports in pure prediction | `rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\\.infra" app/prediction -g "*.py"` | `backend` | yes | zero hit |
| Removed old import paths | `rg -n "app\\.prediction\\.context_loader|app\\.prediction\\.persistence_service" app tests` | `backend` | yes | no active legacy consumer hits except test guards/evidence |
| No root backend prediction dir | `python -c "import os; assert not os.path.exists('prediction')"` | `backend` | yes | exit 0 |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff lint | `ruff check app tests` | `backend` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| DB harness guardrail RG-011 | `pytest -q app/tests/unit/test_backend_db_test_harness.py` | `backend` | yes | all tests pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repository root | yes | only story-scoped files changed |
| Whitespace/conflict check | `git diff --check` | repository root | yes | no whitespace/conflict errors |
| Final status | `git status --short` | repository root | yes | expected files only |

## Commands that may be skipped only with justification

- Full `pytest -q` may be skipped only if targeted and integration checks pass and runtime constraints are documented.
