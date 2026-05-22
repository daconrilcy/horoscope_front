<!-- Carte des fichiers cible generee pour CS-217. -->

# Target Files

## Must Read

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `_condamad/stories/regression-guardrails.md`

## Likely Modified

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/evidence/validation.md`
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/generated/*.md`
- `_condamad/stories/story-status.md`

## Forbidden Unless Blocker Is Recorded

- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/planetary_conditions/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `frontend/src/**`
