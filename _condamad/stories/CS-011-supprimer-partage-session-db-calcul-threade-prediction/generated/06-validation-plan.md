# Validation Plan

## Environment assumptions

- Commands run from `backend/` after `.\.venv\Scripts\Activate.ps1`.
- Python commands must never run outside the activated venv.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Runner unit tests | `pytest -q app/tests/unit/test_prediction_compute_runner.py` | `backend/` | yes | all tests pass |
| Daily prediction regression | `pytest -q app/tests/unit/test_daily_prediction_service.py` | `backend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| DB direct import guard | `rg -n "SessionLocal|engine" app/tests/unit/test_prediction_compute_runner.py app/tests/unit/test_daily_prediction_service.py` | `backend/` | yes | no direct forbidden DB imports |
| Thread/session comment guard | `rg -n "non-thread-safe|thread-safe|session worker|contexte precharge" app/services/prediction/compute_runner.py` | `backend/` | yes | corrected behavior documented |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff lint targeted | `ruff check app/services/prediction/compute_runner.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_prediction_compute_runner.py` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Broader backend tests | `pytest -q` | `backend/` | conditional | pass or documented limitation |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Whitespace check | `git diff --check` | repo root | yes | no whitespace/conflict marker issues |
| Final status | `git status --short` | repo root | yes | expected dirty files only |
