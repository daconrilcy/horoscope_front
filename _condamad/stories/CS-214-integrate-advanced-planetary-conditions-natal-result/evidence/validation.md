# CS-214 Validation Evidence

## Baseline

- `advanced_planetary_conditions_runtime.py`: absent before implementation.
- `signal_factory.py`: absent before implementation.
- `RG-141`: present before final validation.
- Existing calculators CS-209 to CS-213 reused.

## Commands Run

All Python commands were run after activating `.venv` from repository root.

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py
ruff format .
ruff check .
pytest -q
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md
```

## Results

- Targeted CS-214 tests: 7 passed.
- CS-209 to CS-213 tests: 97 passed.
- `ruff format .`: PASS.
- `ruff check .`: PASS.
- Persistence regression tests: PASS.
- `pytest -q`: 2920 passed, 1 skipped, 1177 deselected.
- Story validation and lint: PASS.

## Scans

- Forbidden dependencies in new modules: zero hit.
- Forbidden scoring terms in new modules: zero hit.
- Forbidden interpretation/LLM terms in new modules: zero hit.
- `json_builder`/`frontend` in new modules: zero hit.
- Public symbols found only in planetary conditions, natal runtime and tests.
- `advanced_planetary_conditions` absent from `NatalResult.model_json_schema()`
  and app OpenAPI schemas.
- `natal_calculation.py` detailed-condition scan hits only pre-existing
  `is_retrograde` field/property transfer lines.
- Adjacent diff over forbidden production surfaces: empty.
