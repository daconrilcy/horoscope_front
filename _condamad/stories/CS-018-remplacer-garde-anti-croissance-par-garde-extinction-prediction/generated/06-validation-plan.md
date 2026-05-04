# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.
- Test framework: pytest.
- Lint/static tool: Ruff.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Guard test | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | yes | all guard tests pass |
| Service regression | `pytest -q app/tests/unit/test_daily_prediction_service.py` | `backend/` | yes | service tests pass |
| API regression | `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend/` | yes | integration tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy folder extinction | `rg --files app/prediction` | `backend/` | yes | no files found; command may return exit 1 |
| Legacy import extinction | `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` | `backend/` | yes | zero active Python hits |
| Allowlist not runtime | `rg -n "_PREDICTION_NAMESPACE_ALLOWLIST\|prediction-namespace-allowlist\|allowlist" app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | yes | zero hits in guard runtime |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Compatibility wording scan | `rg -n "legacy\|compat\|shim\|fallback\|deprecated\|alias" app tests -g "*.py"` | `backend/` | yes | hits classified or zero active story regressions |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff lint targeted | `ruff check app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | yes | no lint errors |
| Ruff format check targeted | `ruff format --check app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | yes | file already formatted |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff check | `git diff --check` | repo root | yes | no conflict markers or whitespace errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Worktree status | `git status --short` | repo root | yes | expected story files only |

## Commands that may be skipped only with justification

- Full backend `pytest -q` may be skipped only if targeted guard, service and API checks pass and the reason is recorded.
- Local app startup may be skipped because this story changes architecture tests and CONDAMAD evidence only, not runtime application code.
