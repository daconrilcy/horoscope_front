# Validation Plan - CS-012

## Environment assumptions

- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend`.
- No frontend command is required because the story is backend architecture-only.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint changed guard | `ruff check app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | yes | no lint errors |
| Targeted architecture and LLM guards | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Prediction file inventory | `rg --files app/prediction` | `backend` | yes | reviewed against allowlist |
| Forbidden import scan | `rg -n "from app\\.api|import app\\.api|fastapi|AIEngineAdapter|from sqlalchemy|import sqlalchemy|LLMNarrator" app/prediction -g "*.py"` | `backend` | yes | zero hits |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy wording classification | `rg -n "legacy|compat|shim|fallback|deprecated|alias" app/prediction app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | yes | hits classified |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend lint subset | `ruff check app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Broader backend suite | `pytest -q` | `backend` | no | pass if feasible; otherwise document limitation |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repository root | yes | only story-relevant changes |
| Whitespace/conflict check | `git diff --check` | repository root | yes | no whitespace or conflict-marker errors |
| Final status | `git status --short` | repository root | yes | expected files only |
