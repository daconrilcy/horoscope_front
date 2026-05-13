# Target Files

## Must read

- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/tests/integration/test_migration_a_prediction_tables.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `docs/tables-planetes-et-roles.md`
- Existing recent Alembic revisions under `backend/migrations/versions/`

## Must search

- `rg -n "planet_profiles|astral_prediction_daily_planet_profiles" backend docs _condamad _bmad-output`
- `rg -n "ix_planet_profiles|uq_planet_profiles" backend`

## Likely modified

- `backend/app/infra/db/models/prediction_reference.py`
- New Alembic migration under `backend/migrations/versions/`
- Backend integration tests asserting table names/indexes
- Active docs under `docs/`
- CONDAMAD capsule files

## Forbidden unless directly justified

- Frontend files.
- Business scoring formulas.
- Seed values.
- User-unrelated dirty files.

