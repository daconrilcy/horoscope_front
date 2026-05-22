# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands: activate `.\.venv\Scripts\Activate.ps1` from repository root before running Python tools.
- Backend command scope: `Set-Location backend` after activation for `ruff` and full `pytest`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Calculator and contracts tests | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | repo root | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden dependencies | `rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services|sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter" backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py` | repo root | yes | zero hits |
| Forbidden scoring | `rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py` | repo root | yes | zero hits |
| Forbidden text generation | `rg -n "interpretation|meaning|description|narrative|prompt" backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py` | repo root | yes | zero hits |
| Forbidden observation/integration | `rg -n "horizon|altitude|weather|topocentric|magnitude|latitude|ephemeris|NatalResult|FastAPI|SQLAlchemy" backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py` | repo root | yes | zero hits |
| Public symbols in allowed package/tests | `rg -n "PlanetVisibilityThresholds|calculate_planet_visibility_condition|calculate_planet_visibility_conditions|CONJUNCT_SOLAR" backend/app/domain/astrology/planetary_conditions backend/tests/unit/domain/astrology/planetary_conditions` | repo root | yes | hits limited to contracts, exports, calculator and tests |
| Public symbols absent from adjacent surfaces | `rg -n "PlanetVisibilityThresholds|calculate_planet_visibility_condition|calculate_planet_visibility_conditions|CONJUNCT_SOLAR" backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/domain/astrology/natal_calculation.py backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | repo root | yes | zero hits |
| Adjacent diff review | `git diff -- backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/domain/astrology/natal_calculation.py backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | repo root | yes | empty diff |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format, lint and backend regression suite | `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .; ruff check .; pytest -q` | repo root | yes | all pass |

## Story validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validator and linter | `.\.venv\Scripts\Activate.ps1; $story = "_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md"; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story` | repo root | yes | all pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Worktree status | `git status --short` | repo root | yes | expected story files only |

## Commands that may be skipped only with justification

- None for CS-213. Required commands must run or the story remains blocked.
