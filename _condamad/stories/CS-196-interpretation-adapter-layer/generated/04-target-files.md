# CS-196 Target Files

## Backend Domain

- `backend/app/domain/astrology/interpretation_adapters/*`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`

## Infra / Seeds / Migrations

- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/services/reference_data/dignity_seed_service.py`
- `backend/migrations/versions/20260519_0136_create_interpretation_adapter_references.py`
- `docs/db_seeder/astrology/astral_interpretation_*.json`

## Public JSON / Tests

- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_*interpretation*`
- `backend/app/tests/unit/test_astrology_runtime_reference_*`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
