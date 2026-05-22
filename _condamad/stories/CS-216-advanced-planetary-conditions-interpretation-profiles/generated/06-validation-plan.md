# Validation Plan - CS-216

All Python commands must be run after `.\\.venv\\Scripts\\Activate.ps1` from the repository root.

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Profile runtime tests | `pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py` | repo root | yes | all tests pass |
| Natal integration tests | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py` | repo root | yes | all tests pass |
| CS-214 regression | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py` | repo root | yes | all tests pass |
| CS-215 regression | `pytest -q backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | repo root | yes | all tests pass |
| Story validation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | repo root | yes | validation passes |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | repo root | yes | lint passes |
| Format | `ruff format backend` | repo root | yes | no formatting failures |
| Lint | `ruff check backend` | repo root | yes | no lint errors |
| Full backend tests | `pytest -q` | repo root | yes | all tests pass |
| Scoring guard | `rg -n "\\bscore\\b|score_delta|strength_modifier|dignity_score" backend/app/domain/astrology/interpretation/advanced_conditions -g "*.py"` | repo root | yes | zero hits |
| Surface guard | `rg -n "prompt|LLM|OpenAI|AIEngineAdapter|from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services|sqlalchemy|fastapi|pydantic|FastAPI|SQLAlchemy|Session|repository|json_builder|frontend|migrations|router" backend/app/domain/astrology/interpretation/advanced_conditions -g "*.py"` | repo root | yes | zero hits |
| Final-text guard | `rg -n "You are|This means|Votre|Vous|Cela signifie" backend/app/domain/astrology/interpretation/advanced_conditions -g "*.py"` | repo root | yes | zero hits |
| Recalculation guard | `rg -n "calculate_solar_proximity|calculate_planetary_motion|calculate_solar_phase|calculate_planet_visibility|calculate_moon_phase|sun_longitude|moon_longitude|ephemeris|SwissEph|swe" backend/app/domain/astrology/interpretation/advanced_conditions -g "*.py"` | repo root | yes | zero hits |
| Guardrail registry | `rg -n "RG-143" _condamad/stories/regression-guardrails.md` | repo root | yes | one matching invariant |
| Adjacent diff review | `git diff -- backend/app/domain/astrology/planetary_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/interpretation_adapters backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | repo root | yes | empty diff |
| Diff check | `git diff --check` | repo root | yes | no whitespace/conflict errors |

Skipped required commands must be recorded with reason, risk and compensating evidence.
