# Final Evidence

Status: done

## Implementation Summary

- Ajout de `HouseRuntimeData` et de ses sous-structures runtime.
- Ajout des calculateurs `contained_signs`, `intercepted_signs` et `house_strength`.
- Ajout des builders occupants et maisons runtime sous `domain/astrology`.
- Branchement du pipeline natal apres resolution unique des `HouseRulerResolver`.
- Projection JSON publique enrichie, avec `sign` maintenu comme champ legacy explicite.
- Persistance `chart_results.result_payload.houses[]` enrichie via `NatalResult.model_dump()`.

## Files Changed

- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/constants/house_axes.py`
- `backend/app/domain/astrology/calculators/contained_signs.py`
- `backend/app/domain/astrology/calculators/intercepted_signs.py`
- `backend/app/domain/astrology/calculators/house_strength.py`
- `backend/app/domain/astrology/builders/house_occupants_builder.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/*`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_natal_metadata.py`
- `backend/app/tests/unit/test_natal_pipeline_swisseph.py`
- `backend/app/tests/unit/test_aspect_ruleset_schema.py`
- `backend/app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py`

## Validation

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` - PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology app/tests/unit/test_chart_json_builder.py app/tests/unit/test_house_ruler_resolver.py app/tests/unit/test_chart_result_service.py app/tests/unit/test_natal_metadata.py app/tests/unit/test_natal_pipeline_swisseph.py app/tests/unit/test_aspect_ruleset_schema.py app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py` - PASS, 101 tests.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(app.title)"` - PASS.
- `rg -n "house_runtime|HouseRuntimeData|contained_signs|intercepted_signs|HouseStrengthRuntimeData" backend\migrations backend\app\infra` - PASS zero-hit.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` - NOT RUN TO COMPLETION: timeout after 304 seconds.

## Review Findings

- Fixed: `sign` legacy was initially present only in chart JSON. It is now a serialized `HouseRuntimeData` field and is asserted through chart-result persistence.
- Fixed: Whole Sign interception guard initially covered only the literal string. It now normalizes enum values and has an enum regression test.
- Fixed: capsule evidence was incomplete before review. Traceability and final evidence are now updated.

## Remaining Risk

- Full backend pytest did not complete within the 304 second timeout. Targeted runtime/chart-result/natal suites pass.
