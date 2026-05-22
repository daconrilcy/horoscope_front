# Target Files

## Inspected

- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`
- `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`

## Modified

- `backend/app/domain/astrology/calculators/aspect_inputs.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`
- `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`

## Evidence / Tracking

- `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/generated/*`
- `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/evidence/validation.md`
- `_condamad/stories/story-status.md`

## Forbidden Scope Kept Untouched

- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/planetary_conditions/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `frontend/src/**`
