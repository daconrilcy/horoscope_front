# Target Files

## Inspect First

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `_condamad/stories/regression-guardrails.md`

## Likely Modified

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/evidence/validation.md`
- `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/generated/10-final-evidence.md`
- `_condamad/stories/story-status.md`

## Forbidden

- `frontend/**`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `backend/app/services/chart/json_builder.py`
- condition calculators except read-only inspection.
