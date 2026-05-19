# Target Files

## Must Read

- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
- `_condamad/stories/regression-guardrails.md`

## Likely Modified

- `backend/migrations/versions/*.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/reference_data/dignity_seed_service.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_signal_builder.py`
- `backend/app/domain/astrology/condition/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`

## Tests

- `backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`

## Forbidden Unless Recut

- `frontend/**`
- `backend/app/services/llm_generation/**`
- `backend/app/domain/prediction/**`
- `backend/app/domain/astrology/dignities/**` dignity scoring logic

