# Validation Plan

## Environment Assumptions

- Working directory for backend commands: `backend/`.
- Python commands run only after `.\.venv\Scripts\Activate.ps1` from repo root.
- Test framework: pytest.
- Static checks: Ruff.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Request ID standard | `pytest -q app/tests/unit/test_request_id.py` | `backend/` | yes | all tests pass |
| Service propagation | `pytest -q app/tests/unit/test_daily_prediction_service.py` | `backend/` | yes | all tests pass |
| Projection contract | `pytest -q app/tests/unit/test_public_projection.py` | `backend/` | yes | all tests pass |
| Guardrails | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | yes | all tests pass |
| API integration | `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend/` | yes | all tests pass if present |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Projection UUID prohibition | `rg -n "uuid\\.uuid4\\(|request_id = str\\(|trace_id = str\\(" app/prediction/public_projection.py` | `backend/` | yes | no output |
| LLM legacy provider guard | `rg -n "LLMNarrator\\(|chat\\.completions\\.create|openai\\.AsyncOpenAI" app tests` | `backend/` | yes | only classified historical or guard hits |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff lint | `ruff check app tests` | `backend/` | yes | no lint errors |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace or conflict errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Final status | `git status --short` | repo root | yes | expected files only |

## Commands That May Be Skipped Only With Justification

- Broader `pytest -q` if targeted checks and quality gate pass but runtime cost or environment blocks the full suite.
