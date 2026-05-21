# Validation Plan

## Environment Assumptions

- All Python commands run from repository root after `.\.venv\Scripts\Activate.ps1`.
- No frontend validation is required because CS-212 must not touch `frontend/**`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted calculator tests | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py` | repo root | yes | all tests pass |
| Contract regression tests | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | repo root | yes | all tests pass |

## Architecture / Import Guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden app layer imports | `rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services" backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py` | repo root | yes | zero hits |
| Forbidden external/runtime deps | `rg -n "sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter" backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py` | repo root | yes | zero hits |
| Forbidden scoring | `rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py` | repo root | yes | zero hits |
| Forbidden interpretation | `rg -n "interpretation|meaning|description|narrative|prompt" backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py` | repo root | yes | zero hits |
| Forbidden adjacent domains | `rg -n "NatalResult|transit|progression|eclipse|ephemeris|FastAPI|SQLAlchemy" backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py` | repo root | yes | zero hits |
| Adjacent integration scan | `rg -n "calculate_moon_phase_condition|MoonPhaseCondition|MoonPhaseKey|WaxingWaningState" <adjacent_roots>` | repo root | yes | zero hits outside allowed references |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no formatting errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |
| Regression suite | `pytest -q` | repo root | yes | all tests pass |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Diff summary | `git diff --stat` | repo root | yes | only story files and pre-existing registry/status changes |
| Final status | `git status --short` | repo root | yes | expected files only |

## Skipped Command Rule

Any skipped command must be recorded in final evidence with exact command, reason, risk and compensating evidence.
