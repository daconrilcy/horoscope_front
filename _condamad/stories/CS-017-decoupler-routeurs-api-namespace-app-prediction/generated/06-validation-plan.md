# Validation Plan

## Environment assumptions

- PowerShell on Windows.
- All Python commands run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Guard API/import architecture | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | yes | all tests pass |
| Public daily API contract | `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend/` | yes | all tests pass |
| Daily horoscope narration compatibility | `pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py` | `backend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| API zero import legacy prediction | `rg -n "app\.prediction" app/api -g "*.py"` | `backend/` | yes | zero hits |
| OpenAPI runtime contract | compare `_condamad/.../openapi-before.json` and `_condamad/.../openapi-after.json` | repo root | yes | no diff |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format check | `ruff format --check .` | `backend/` | yes | all files already formatted |
| Lint/static check | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend test suite | `pytest -q` | `backend/` | yes | all tests pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Final worktree status | `git status --short` | repo root | yes | expected dirty files only |
