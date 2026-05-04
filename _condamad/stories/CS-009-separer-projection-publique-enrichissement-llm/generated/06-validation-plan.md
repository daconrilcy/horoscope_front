# Validation Plan

## Environment assumptions

- Repository root: `c:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for Python validation: `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Projection contract and narrative separation | `pytest -q app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | yes | all tests pass |
| Prediction service/API contract | `pytest -q app/tests/unit/test_daily_prediction_service.py app/tests/integration/test_daily_prediction_api.py` | `backend/` | yes | all tests pass |
| Horoscope narration canonical service | `pytest -q app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/integration/test_horoscope_daily_variant_narration.py` | `backend/` | yes | all tests pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden runtime dependencies absent from projection | `rg -n "AIEngineAdapter\|uuid\\.uuid4\\(\|settings\|Session" app/prediction/public_projection.py` | `backend/` | yes | no hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format app tests` | `backend/` | yes | files formatted |
| Lint | `ruff check app tests` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Combined targeted regression | `pytest -q app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_daily_prediction_service.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/integration/test_horoscope_daily_variant_narration.py` | `backend/` | yes | all tests pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed, plus pre-existing story registry edits |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace errors |
| Worktree status | `git status --short` | repo root | yes | expected files reported |

## Commands that may be skipped only with justification

- Full `pytest -q` may be skipped if targeted regression and story-required commands pass; record the residual risk.
