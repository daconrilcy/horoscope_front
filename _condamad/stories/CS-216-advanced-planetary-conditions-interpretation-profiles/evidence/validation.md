# Validation CS-216

## Baseline

- Initial `git status --short`: clean.
- `RG-143` present in `_condamad/stories/regression-guardrails.md`.
- `interpretation/advanced_conditions` package absent before implementation.
- Adjacent owners inspected: `planetary_conditions`, `dignities`, `natal_calculation.py`, `interpretation/profile_fields.py`.

## Commands

| Command | Result | Notes |
|---|---|---|
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py` | PASS | 12 passed |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | PASS | 13 passed |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | PASS | 25 passed |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py` | PASS | 8 passed after review fix |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | PASS | 26 passed after review fixes |
| `.\\.venv\\Scripts\\Activate.ps1; ruff format backend` | PASS | 1 file reformatted |
| `.\\.venv\\Scripts\\Activate.ps1; ruff format backend --check` | PASS | 1510 files already formatted |
| `.\\.venv\\Scripts\\Activate.ps1; ruff check backend` | PASS | all checks passed after import cleanup |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q` | PASS | first 2 minute attempt timed out; rerun passed: 2941 passed, 1 skipped, 1177 deselected |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q` | PASS | final rerun after review fixes: 2942 passed, 1 skipped, 1177 deselected |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | PASS | story validation passed |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | PASS | no missing required contracts |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | PASS | story lint passed |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | PASS | strict story lint passed |
| `.\\.venv\\Scripts\\Activate.ps1; Set-Location backend; python -B -c "from app.main import app; print(type(app).__name__)"` | PASS | FastAPI import smoke passed |

## Static Guards

| Guard | Result |
|---|---|
| `rg -n "\\bscore\\b|score_delta|strength_modifier|dignity_score" backend/app/domain/astrology/interpretation/advanced_conditions -g "*.py"` | PASS, zero hits |
| `rg -n "prompt|LLM|OpenAI|AIEngineAdapter|from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services|sqlalchemy|fastapi|pydantic|FastAPI|SQLAlchemy|Session|repository|json_builder|frontend|migrations|router" backend/app/domain/astrology/interpretation/advanced_conditions -g "*.py"` | PASS, zero hits |
| `rg -n "You are|This means|Votre|Vous|Cela signifie" backend/app/domain/astrology/interpretation/advanced_conditions -g "*.py"` | PASS, zero hits |
| `rg -n "calculate_solar_proximity|calculate_planetary_motion|calculate_solar_phase|calculate_planet_visibility|calculate_moon_phase|sun_longitude|moon_longitude|ephemeris|SwissEph|swe" backend/app/domain/astrology/interpretation/advanced_conditions -g "*.py"` | PASS, zero hits |
| `git diff -- backend/app/domain/astrology/planetary_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/interpretation_adapters backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | PASS, empty diff |
| `git diff --check` | PASS, only line-ending warnings for touched existing files |

## Note

- A smoke command was first attempted from `backend/` with `.\\.venv\\Scripts\\Activate.ps1`, which failed because the relative venv path exists at repo root. The command was rerun from repo root with activation before `Set-Location backend`; the rerun passed.
- Review fix: the source story implementation checklist was marked complete after an independent reviewer found it inconsistent with generated evidence.
- Review fix: the final worktree status is now persisted in `generated/10-final-evidence.md`.
- Review fix: contract and integration tests now guard optional `notes`, non-empty natal profile wiring and `new_moon` runtime resolution.
- Review fix: catalogue keywords now match the initial brief examples for `cazimi`, `stationary`, `emerging`, `full_moon` and `new_moon`, with regression assertions in profile runtime tests.
