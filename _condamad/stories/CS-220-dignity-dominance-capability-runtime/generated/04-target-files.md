# Target Files

## Must inspect

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dominance/contracts.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`

## Modified

- Runtime payload contract and phase validators.
- Builder initial capabilities for dignity/dominance candidates.
- New dignity and dominance chart-object selector/projector/enricher modules.
- Natal orchestration for dignity and dominance enrichment.
- Unit, integration and architecture tests.

## Forbidden unless explicit blocker

- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `frontend/**`
