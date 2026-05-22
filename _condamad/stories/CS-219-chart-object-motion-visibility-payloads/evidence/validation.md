# Validation CS-219

## Baseline

Captured by repository inspection before implementation:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
- `_condamad/stories/regression-guardrails.md` with `RG-146`.

## Commands

| Command | Working directory | Result | Summary |
|---|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | FIXED_AFTER_FAIL_THEN_PASS | First run failed because `ChartObjectVisibilityPayload` was not imported in the builder; final rerun after review fixes passed `24 passed`. |
| `pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py` | repo root | PASS | `36 passed`. |
| `ruff format .` | `backend` | PASS | `1518 files left unchanged` after prior local formatting. |
| `ruff check .` | `backend` | PASS | `All checks passed`. |
| `pytest -q` | `backend` | PASS | Final rerun after review fixes: `2978 passed, 1 skipped, 1177 deselected`. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | PASS | Story validation passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | PASS | No missing required contracts. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | PASS | Story lint passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | PASS | Strict story lint passed. |

## Scan Classification

| Scan | Result | Classification |
|---|---|---|
| `rg -n "combust|cazimi|under_beams|under beams|retrograde|stationary" backend/app/domain/astrology -g "*.py"` | Hits | Expected hits in existing calculators/contracts/dignities/interpretation plus CS-219 mapper fields. No duplicate calculator or local threshold introduced in chart-object builder/runtime. |
| `rg -n "if .*object_type|\.object_type ==" backend/app/domain/astrology -g "*.py"` | Zero hit | PASS: no consumer branch on `object_type`. |
| `rg -n "\b8\.5\b|\b17\b|\b0\.2833\b|\b0\.01\b" backend/app/domain/astrology -g "*.py"` | Hits | Existing canonical thresholds or unrelated orb/ayanamsa tolerance: `planetary_conditions/contracts.py`, `ephemeris_provider.py`, `aspect_runtime_builder.py`, `interpretation/aspect_strength.py`. No hit in CS-219 builder/runtime. |
| `rg -n "calculate_solar_proximity|calculate_planetary_motion|calculate_solar_phase|calculate_planet_visibility" backend/app/domain/astrology/builders backend/app/domain/astrology/runtime -g "*.py"` | Zero hit | PASS: builder/runtime do not call condition calculators. |
| `rg -n "RG-146" _condamad/stories/regression-guardrails.md` | Hit | PASS: RG-146 is registered. |
| `Test-Path _condamad/stories/CS-219-chart-object-motion-visibility-payloads/evidence/validation.md` | `True` | PASS: persistent evidence exists. |
| `rg -n 'planet_position' backend/app/domain/astrology/builders/chart_object_runtime_builder.py backend/tests/unit/domain/astrology -g '*.py'` | Hits | PASS: no `source="planet_position"` fallback remains; hits are parameter names, historical collections, test helper names, and allowed assertions. |
| `rg -n 'source="planet_position"\|source: str = "planet_position"' backend/app backend/tests -g "*.py"` | Zero hit | PASS: no implicit payload source fallback remains. |

## Review Fixes

| Finding | Decision | Fix | Validation |
|---|---|---|---|
| Story conformance: missing natal integration proof for motion payloads. | Accepted | Added `test_natal_chart_objects_expose_motion_payloads_when_positions_have_speeds`. | Targeted tests and full backend suite passed. |
| Story conformance: threshold guard omitted `17`. | Accepted | Added `17` and `17.0` to persistent architecture guard. | Architecture tests passed. |
| Story conformance: source story status still `ready-to-dev`. | Accepted | Updated `00-story.md` to `ready-to-review`. | Story lint/validation previously passed; status now synchronized. |
| Source closure: fallback path kept non-canonical motion payloads alive. | Accepted | Removed builder fallback from raw `PlanetPosition` motion facts; motion payloads now require `PlanetaryMotionCondition`. | Targeted tests, scans, lint, full backend suite passed. |
| Source closure: AC6 direct missing-payload evidence absent. | Accepted | Added direct validator test for `supports_visibility=True` with empty payloads. | Targeted tests passed. |
| Review iteration 2: `ChartObjectMotionPayload.source` still defaulted to `planet_position`. | Accepted | Changed the default to `planetary_conditions.motion` and made the regression test explicit. | Targeted tests, source scan, lint, full backend suite passed. |

## Result

PASS. CS-219 implementation is closed after a fresh clean review. Python
commands were run after activating `.\.venv\Scripts\Activate.ps1`.
