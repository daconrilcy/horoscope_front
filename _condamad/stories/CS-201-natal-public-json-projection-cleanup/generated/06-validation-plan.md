# Validation Plan

## Environment Assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted projection tests | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` | repo root | yes | all tests pass |
| Persisted payload tests | `pytest -q backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | all tests pass |
| Natal contract tests | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | all tests pass |
| Golden cases | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | yes | all tests pass |
| Regression dignity | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | repo root | yes | all tests pass |
| Regression advanced conditions | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` | repo root | yes | all tests pass |
| Regression profiles | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` | repo root | yes | all tests pass |
| Regression dominance | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` | repo root | yes | all tests pass |
| Regression adapter | `pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` | repo root | yes | all tests pass |
| Format | `ruff format .` | repo root | yes | no formatting drift remains |
| Lint | `ruff check .` | repo root | yes | no lint errors |
| OpenAPI import contract | `python -c "from backend.app.main import app; app.openapi()"` | repo root | yes | command exits 0 |
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace/conflict issues |
| Diff scope | `git diff --stat` | repo root | yes | only story-scoped files changed |

## Scans

Run the forbidden projection, legacy alias, doctrine constant, horizon tuple, pure-domain import, evidence and adjacent-surface scans from `00-story.md` section 21.

Skipped commands must be recorded in `generated/10-final-evidence.md` and `evidence/public-json-validation.md`.
