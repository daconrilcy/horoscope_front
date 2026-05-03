# Validation Plan

## Environment assumptions

- Commands run from `backend/` after `.\\.venv\\Scripts\\Activate.ps1`.
- No new dependency.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story tests and guards | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_persistence_explainability.py app/tests/unit/test_calibration_versioning.py app/tests/integration/test_v3_baselines.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend/` | yes | all tests pass |
| V3 schema regression | `pytest -q app/tests/unit/test_schemas_v3.py` | `backend/` | yes | all tests pass |

## Architecture / negative scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Classified legacy scan | `rg -n "EngineOutput|TimeBlock|engine_output=|\bcategories\b|LLMNarrator" app tests` | `backend/` | yes | hits classified; removed surfaces only in guard/canonical owners |
| OpenAPI smoke | `python -c "from app.main import app; schema = app.openapi(); assert 'paths' in schema; assert '/v1/predictions/daily' in schema['paths']"` | `backend/` | yes | command exits 0 |

## Lint / static checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff lint | `ruff check app tests` | `backend/` | yes | no lint errors |
| Diff whitespace | `git diff --check` | `backend/` | yes | no whitespace errors |

## Full regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend suite | `pytest -q` | `backend/` | yes | all tests pass |

## Rule for skipped commands

Skipped commands must record exact command, reason, risk, and compensating evidence. No command was skipped for this execution.
