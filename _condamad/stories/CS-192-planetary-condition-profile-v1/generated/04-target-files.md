<!-- Carte des fichiers cibles pour CS-192. -->

# CS-192 Target Files

## Code

- `backend/migrations/versions/20260519_0130_add_condition_axes_to_dignity_weights.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/dignity_reference_repository.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/condition/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`

## Tests

- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`

## Evidence

- `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/natal-condition-profile-before.json`
- `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/natal-condition-profile-after.json`
- `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/condition-runtime-reference.md`
- `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/condition-guard-evidence.md`
