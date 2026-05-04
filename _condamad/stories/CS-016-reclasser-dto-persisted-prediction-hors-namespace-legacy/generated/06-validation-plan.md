# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Working directory for Python checks: `backend`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Guard RG-036 | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | yes | all tests pass |
| Persistence and scoring | `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` | `backend` | yes | all tests pass |
| API daily compatibility | `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend` | yes | all tests pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Repository legacy imports | `rg -n "app\.prediction\.persisted|app\.prediction\.context" app/infra/db/repositories -g "*.py"` | `backend` | yes | no hits |
| Active legacy imports | `rg -n "from app\.prediction\.persisted|from app\.prediction\.context" app tests -g "*.py"` | `backend` | yes | no hits |
| Legacy package files | `rg --files app/prediction` | `backend` | yes | no files / path absent |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint scoped | `ruff check app/infra/db/repositories app/tests` | `backend` | yes | no lint errors |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace/conflict marker issues |
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped changes |
| Worktree status | `git status --short` | repo root | yes | expected files plus pre-existing unrelated dirty files |
