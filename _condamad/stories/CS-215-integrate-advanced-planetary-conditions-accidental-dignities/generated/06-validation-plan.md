<!-- Plan de validation executable pour CS-215. -->

# Validation Plan

All Python commands must be run after:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Targeted Tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Modifiers engine | `pytest -q backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | repo root | yes | all pass |
| Scoring integration | `pytest -q backend/tests/unit/domain/astrology/dignities/test_accidental_dignity_conditions_integration.py` | repo root | yes | all pass |
| Contract regression | `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py` | repo root | yes | all pass |
| Accidental calculator regression | `pytest -q backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py` | repo root | yes | all pass |
| Scoring service regression | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | repo root | yes | all pass |
| CS-214 runtime regression | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py` | repo root | yes | all pass |
| CS-208 to CS-213 regressions | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py` | repo root | yes | all pass |

## Architecture / Import Guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden deps | `rg -n $forbidden_deps $new_modules` | repo root | yes | zero hits |
| Forbidden surface terms | `rg -n $forbidden_surface_terms $new_modules` | repo root | yes | zero hits |
| Forbidden duplication | `rg -n $forbidden_duplication $new_modules` | repo root | yes | zero hits |
| Public symbols | `rg -n "calculate_advanced_condition_modifiers|AccidentalDignityModifier|advanced_condition_modifier" backend/app/domain/astrology/dignities backend/tests -g "*.py"` | repo root | yes | only expected files |
| RG-142 present | `Select-String "RG-142" _condamad/stories/regression-guardrails.md` | repo root | yes | row found |
| Adjacent diff | `git diff -- $adjacent_diff_paths` | repo root | yes | empty diff |

## Quality And Regression

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format backend` | repo root | yes | no changes or formatted |
| Backend lint | `ruff check backend` | repo root | yes | no errors |
| Repo lint | `ruff check .` | repo root | yes | no errors |
| Full tests | `pytest -q` | repo root | yes | all pass |
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/00-story.md` | repo root | yes | PASS |
| Story lint strict | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/00-story.md` | repo root | yes | PASS |

## Skipped Commands

No skipped command is expected.
