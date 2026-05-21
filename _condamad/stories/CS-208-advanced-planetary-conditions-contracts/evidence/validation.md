# Validation CS-208

## Baseline

- `Test-Path backend/app/domain/astrology/planetary_conditions`: `False`
- `rg -n "AdvancedPlanetaryConditionsResult|SolarProximityCondition" backend/app/domain/astrology backend/tests`: zero hits before implementation.
- `RG-135`: present in `_condamad/stories/regression-guardrails.md`.

## Validation finale

| Check | Result | Evidence |
|---|---|---|
| Venv activation | PASS | Every Python command was run from PowerShell after `.\\.venv\\Scripts\\Activate.ps1` in the same command invocation. |
| Targeted tests | PASS | `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`: 9 passed after adding the mutable-signal regression guard. |
| Format | PASS | `ruff format .`: 1487 files left unchanged. |
| Lint | PASS | `ruff check .`: all checks passed after import sorting fix. |
| Full pytest | PASS | `.\\.venv\\Scripts\\Activate.ps1; pytest -q`: 2825 passed, 1 skipped, 1177 deselected after the final review/fix loop. |
| Story validation | PASS | `condamad_story_validate.py`, `--explain-contracts`, `condamad_story_lint.py`, `--strict`: PASS. |
| Forbidden imports scan | PASS | zero hit in `backend/app/domain/astrology/planetary_conditions`. |
| Forbidden frameworks scan | PASS | zero hit for `sqlalchemy`, `fastapi`, `pydantic`. |
| Forbidden calculation scan | PASS | zero hit for calculation/scoring/interpretation-weight names. |
| Forbidden prompt/LLM scan | PASS | zero hit for `prompt`, `OpenAI`, `AIEngineAdapter`. |
| Free annotation scan | PASS | zero hit for `Any` and `dict[str, Any]` in the production package. |
| Adjacent surface diff | PASS | empty diff for advanced_conditions, dignities, condition, dominance, natal_calculation, json_builder, API, infra, migrations and frontend. |
| Adjacent integration scan | PASS | `rg -n "planetary_conditions" backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/natal_calculation.py backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src`: zero hits. |
| Diff check | PASS | `git diff --check`: no whitespace errors; line-ending warnings only for pre-existing tracked markdown files. |

## Review/fix closure

- Review iteration 3 found `CR-3`: caller-provided mutable `signals` lists could
  remain mutable inside frozen contracts.
- Fix: `PlanetaryConditionsBundle` and `AdvancedPlanetaryConditionsResult`
  normalize `signals` to tuples in `__post_init__`.
- Regression guard: `test_signal_collections_are_normalized_to_tuples`.
- Final review iteration 4 verdict: CLEAN.
