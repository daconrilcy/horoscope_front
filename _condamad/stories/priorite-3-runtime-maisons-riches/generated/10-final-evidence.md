# Final Evidence

Status: done

## Implementation Summary

- Ajout de `HouseRuntimeData` et de ses sous-structures runtime.
- Ajout des calculateurs `contained_signs`, `intercepted_signs` et `house_strength`.
- Ajout des builders occupants et maisons runtime sous `domain/astrology`.
- Branchement du pipeline natal apres resolution unique des `HouseRulerResolver`.
- Projection JSON publique enrichie, avec `sign` maintenu comme champ legacy explicite.
- Persistance `chart_results.result_payload.houses[]` enrichie via `NatalResult.model_dump()`.
- Clarification de la source publique canonique: `houses[*].ruler` est la source runtime,
  `house_rulers[]` est une projection legacy.
- Centralisation de la projection legacy dans `json_builder` et reutilisation par
  `ChartResultService.persist_trace` pour eviter une divergence en base.
- Ajout du guardrail `RG-094` pour bloquer la relecture de `NatalResult.house_rulers`,
  `HouseRulerResolver`, `sign_rulerships` ou repositories de maitrises dans
  `app/services/chart`.

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
- `backend/app/services/chart/result_service.py`
- `backend/tests/unit/domain/astrology/*`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_natal_metadata.py`
- `backend/app/tests/unit/test_natal_pipeline_swisseph.py`
- `backend/app/tests/unit/test_aspect_ruleset_schema.py`
- `backend/app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py`

## Validation

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` - PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check app/services/chart/json_builder.py app/tests/unit/test_chart_json_builder.py` - PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app/services/chart/json_builder.py app/services/chart/result_service.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py; ruff check app/services/chart/json_builder.py app/services/chart/result_service.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py` - PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology app/tests/unit/test_chart_json_builder.py app/tests/unit/test_house_ruler_resolver.py app/tests/unit/test_chart_result_service.py app/tests/unit/test_natal_metadata.py app/tests/unit/test_natal_pipeline_swisseph.py app/tests/unit/test_aspect_ruleset_schema.py app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py` - PASS, 101 tests.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py tests/unit/domain/astrology/test_house_runtime_builder.py` - PASS, 23 tests.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(app.title)"` - PASS.
- `rg -n "house_runtime|HouseRuntimeData|contained_signs|intercepted_signs|HouseStrengthRuntimeData" backend\migrations backend\app\infra` - PASS zero-hit.
- `cd backend; rg -n "natal_result\.house_rulers|HouseRulerResolver|sign_rulerships|get_sign_rulerships" app/services/chart -g "*.py"` - PASS zero-hit.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` - NOT RUN TO COMPLETION: timeout after 304 seconds.

## Review Findings

- Fixed: `sign` legacy was initially present only in chart JSON. It is now a serialized `HouseRuntimeData` field and is asserted through chart-result persistence.
- Fixed: Whole Sign interception guard initially covered only the literal string. It now normalizes enum values and has an enum regression test.
- Fixed: capsule evidence was incomplete before review. Traceability and final evidence are now updated.
- Fixed: `house_rulers[]` could diverge from `houses[*].ruler` in JSON public and
  persisted `chart_results.result_payload`; both paths now project from the runtime
  house payload.
- Fixed: stale `NatalResult.house_rulers` entries are ignored when no runtime ruler
  exists for the house.
- Fixed: durable regression guardrail `RG-094` added for the projection contract.
- Re-review: CLEAN after independent read-only review.

## Remaining Risk

- Full backend pytest did not complete within the 304 second timeout. Targeted runtime/chart-result/natal suites pass.
