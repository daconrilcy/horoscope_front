# Validation Plan - CS-209

All Python commands must be run from repository root after:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Targeted checks

| Purpose | Command | Required | Expected result |
|---|---|---:|---|
| Calculator and contract tests | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | yes | pass |
| Contract guard | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | yes | pass |

## Quality checks

| Purpose | Command | Required | Expected result |
|---|---|---:|---|
| Format | `ruff format .` | yes | pass |
| Lint | `ruff check .` | yes | pass |
| Full backend regression | `pytest -q` | yes | pass |

## Required scans

| Purpose | Command | Required | Expected result |
|---|---|---:|---|
| Calculator forbidden imports | `rg -n "from app\\.api\|from app\\.infra\|from app\\.infrastructure\|from app\\.services" backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py` | yes | zero hit |
| Calculator forbidden dependencies | `rg -n "sqlalchemy\|fastapi\|pydantic\|OpenAI\|AIEngineAdapter" backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py` | yes | zero hit |
| Calculator forbidden scoring | `rg -n "\\bscore\\b\|score_delta\|accidental_score_delta\|essential_score_delta\|strength_modifier" backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py` | yes | zero hit |
| Calculator forbidden text/LLM surface | `rg -n "interpretation\|meaning\|description\|narrative\|prompt" backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py` | yes | zero hit |
| Contract forbidden imports | `rg -n "from app\\.api\|from app\\.infra\|from app\\.infrastructure\|from app\\.services\|sqlalchemy\|fastapi\|pydantic" backend/app/domain/astrology/planetary_conditions/contracts.py` | yes | zero hit |
| Contract no free annotations/calculators | `rg -n "calculate_\|compute_\|resolve_\|detect_\|score_delta\|interpretation_weight\|prompt\|OpenAI\|AIEngineAdapter" backend/app/domain/astrology/planetary_conditions/contracts.py` and `rg -n "\\bAny\\b\|dict\\[str, Any\\]" backend/app/domain/astrology/planetary_conditions/contracts.py` | yes | zero hit |
| Public symbol placement | `rg -n "SolarProximityThresholds\|calculate_solar_proximity_condition" backend/app/domain/astrology/planetary_conditions backend/tests/unit/domain/astrology/planetary_conditions` | yes | hits limited to package and tests |
| Adjacent diff | `git diff -- backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/domain/astrology/natal_calculation.py backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | yes | empty |

## Story checks

| Purpose | Command | Required | Expected result |
|---|---|---:|---|
| Story validation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md` | yes | pass |
| Story contract explanation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md` | yes | pass |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md` | yes | pass |
| Story strict lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md` | yes | pass |
