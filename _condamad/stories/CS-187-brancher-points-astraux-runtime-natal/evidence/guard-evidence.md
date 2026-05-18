# Guard evidence

## Tests

- `pytest -q app/tests/unit/test_astral_point_seed_integrity.py` - PASS.
- `pytest -q app/tests/unit/test_astral_point_repository.py app/tests/unit/test_astrology_runtime_reference_repository.py` - PASS.
- `pytest -q tests/unit/domain/astrology/test_astral_point_calculation_resolver.py tests/unit/domain/astrology/test_natal_result_contains_configured_points.py tests/unit/domain/astrology/test_natal_aspects_include_points.py` - PASS.
- `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_natal_calculation_service.py` - PASS.
- `pytest -q app/tests/integration/test_natal_calculate_api.py::test_calculate_natal_passes_include_points_in_aspects tests/unit/domain/astrology/test_natal_aspects_include_points.py` - PASS, 3 passed, 1 deselected.
- `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astral_point_repository.py app/tests/unit/test_astrology_runtime_reference_guard.py tests/unit/domain/astrology/test_natal_aspects_include_points.py` - PASS, 17 passed.
- `pytest -q app/tests/unit/test_astral_point_seed_integrity.py app/tests/unit/test_astral_point_repository.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_prediction_reference_repository.py tests/unit/domain/astrology/test_astral_point_calculation_resolver.py tests/unit/domain/astrology/test_natal_result_contains_configured_points.py tests/unit/domain/astrology/test_natal_aspects_include_points.py app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_natal_calculation_service.py app/tests/integration/test_natal_calculate_api.py::test_calculate_natal_passes_include_points_in_aspects` - PASS, 79 passed, 1 deselected.
- `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_calibration_job.py::test_job_stores_raw_day app/tests/unit/test_percentile_calculator.py::test_calibration_injected_in_db` - PASS, 3 passed.
- `pytest -q` - PASS, 2634 passed, 1 skipped, 1176 deselected.
- Backend startup smoke: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8017`, then `GET /openapi.json` - PASS.

## Scans

- `rg -n "true_node|mean_node|\\blilith\\b" app/domain/astrology app/services/natal -g "*.py"` - zero hit.
- `rg -n "ASTRAL_POINTS\\s*=|POINT_VARIANTS\\s*=|NODE_VARIANTS\\s*=|LILITH_VARIANTS\\s*=" app/domain/astrology app/services/natal -g "*.py"` - zero hit.
- `rg -n "AstralPointInterpretationKeywordModel|AstralPointInterpretationProfileModel|keyword_set|micro_note" app/domain/astrology/natal_calculation.py app/domain/astrology/calculators -g "*.py"` - zero hit.
- `rg -n "dict\\[str, Any\\]|list\\[dict" app/domain/astrology/runtime app/infra/db/repositories/astrology_runtime_reference_repository.py app/infra/db/repositories/astrology_runtime_reference_mapper.py -g "*.py"` - hits only on pre-existing non-point runtime payload helpers: `aspect_calculation_contracts.py` and `house_runtime_data.py`.

## Runtime artifacts

- `evidence/astral-points-runtime-before.json` was generated from `AstrologyRuntimeReferenceRepository(db).load("1.0.0")` in a detached HEAD worktree at `989acc7a`.
- `evidence/natal-payload-before.json` was generated from `NatalCalculationService.calculate(...).model_dump(mode="json")` in the same detached HEAD worktree.
- `evidence/astral-points-runtime-after.json` was generated from `AstrologyRuntimeReferenceRepository(db).load("1.0.0")` against a freshly seeded in-memory SQLite DB on the current implementation.
- `evidence/natal-payload-after.json` was generated from `NatalCalculationService.calculate(...).model_dump(mode="json")` with `include_points_in_aspects=false` on the current implementation.
