# Target Files

## Must read

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/migrations/versions/20260218_0001_create_reference_tables.py`
- `backend/migrations/versions/20260307_0032_migration_a_prediction_reference_tables.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`

## Must search

- `rg -n "reference_version_id" backend/app/infra/db/models backend/app/infra/db/repositories backend/app/services/prediction backend/app/tests backend/migrations/versions`
- `rg -n "PlanetModel\\(|SignModel\\(|HouseModel\\(|AspectModel\\(|AstroPointModel\\(" backend/app backend/tests`

## Likely modified

- Backend models, repositories, seed service, Alembic migration, tests.

## Forbidden unless justified

- Frontend files.
- Existing user-modified `.codex-artifacts/**`.
- Broad docs unrelated to this data model.
