# Validation Evidence

## Baseline

- `pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`
  - PASS, 3 passed before implementation.
- `rg -n "aspect_source_positions|aspect_positions|build_aspect_body_from_position|calculate_major_aspects" backend/app/domain/astrology/natal_calculation.py`
  - showed legacy natal aspect input construction at lines 787-810 before implementation.
- `rg -n "object_type ==|\.object_type|ChartObjectType" backend/app/domain/astrology/calculators -g "*.py"`
  - zero hit before implementation.

## Final Checks

- `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`
  - PASS, 10 passed after review fixes.
- `pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`
  - PASS, 5 passed after review fixes.
- `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
  - PASS, 3 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
  - PASS, 4 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`
  - PASS, 3 passed.
- `ruff format .` from `backend/`
  - PASS, no changes on final run.
- `ruff check .` from `backend/`
  - PASS.
- `pytest -q` from `backend/`
  - PASS, 2965 passed, 1 skipped, 1177 deselected.

## Aspect Pair Inventory

- Stable natal chart:
  - birth date: `1990-06-15`
  - birth time: `10:30`
  - birth place: `Paris`
  - timezone: `Europe/Paris`
  - reference: `complete_reference()`
  - house system: `equal`
- Final inventory:
  - `("conjunction", "jupiter", "mercury", 6.711141)`
  - `("conjunction", "mars", "moon", 0.578196)`
- This inventory is locked by
  `test_default_planetary_aspect_pairs_remain_stable`.

## Review Fix Validation

- Accepted technical finding: projector did not reject non-finite/non-numeric
  longitude strongly enough.
  - Fix: `_required_longitude` in `aspect_inputs.py`.
  - Evidence: projector tests for `nan`, `inf`, `-inf` and non-numeric value.
- Accepted conformance finding: AC8 proof was not discriminating enough.
  - Fix: sentinel `ChartObjectRuntimeData` absent from historical collections.
  - Evidence: `test_aspect_flow_consumes_chart_objects_runtime_source`.
- Accepted conformance finding: Mars was not explicitly covered.
  - Fix: Mars included in projected chart-object calculation test.
- Accepted conformance finding: AC9 lacked persistent pair inventory.
  - Fix: pair inventory test and evidence above.

## Scan Classification

- `object_type` / `ChartObjectType` scan in calculators:
  - zero active hit.
- Historical collection scan in calculators:
  - hits are `calculate_planet_positions` in `calculators/natal.py` and its
    package export; both are outside the aspect-engine input boundary.
- Specialized builder scan:
  - hits are expected guard constants in `test_chart_object_runtime_architecture.py`.
- `build_aspect_body_from_position` scan:
  - remaining hit is the helper definition in `aspects.py`;
  - no natal orchestration import or call remains.

## Contract Checks

- Story validation: PASS.
- Story validation with contract explanation: PASS, no missing contracts.
- Story lint: PASS.
- Story lint strict: PASS.
