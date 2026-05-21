# Validation Plan

All Python commands must run after:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story tests | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | repo root | yes | all pass |
| Calculator tests only | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py` | repo root | yes | all pass |
| Contract tests only | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | repo root | yes | all pass |

## Architecture / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden imports | `rg -n "from app\\.api\|from app\\.infra\|from app\\.infrastructure\|from app\\.services" backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py` | repo root | yes | zero hits |
| Forbidden dependencies | `rg -n "sqlalchemy\|fastapi\|pydantic\|OpenAI\|AIEngineAdapter" backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py` | repo root | yes | zero hits |
| Forbidden scoring | `rg -n "\\bscore\\b\|score_delta\|accidental_score_delta\|essential_score_delta\|strength_modifier" backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py` | repo root | yes | zero hits |
| Forbidden narrative/visibility terms | `rg -n "interpretation\|meaning\|description\|narrative\|prompt\|heliacal\|visibility" backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py` | repo root | yes | zero hits |
| Adjacent public symbol scan | `rg -n "SolarPhaseRelationThresholds\|calculate_solar_phase_relation\|calculate_solar_phase_relations" <adjacent_roots>` | repo root | yes | zero hits |
| Adjacent diff | `git diff -- <adjacent_roots>` | repo root | yes | empty |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no remaining formatting changes |
| Lint | `ruff check .` | repo root | yes | pass |
| Regression suite | `pytest -q` | repo root | yes | pass |

## Story validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story contract | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md` | repo root | yes | pass |
| Story contracts explained | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md` | repo root | yes | pass |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md` | repo root | yes | pass |
| Strict story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md` | repo root | yes | pass |
