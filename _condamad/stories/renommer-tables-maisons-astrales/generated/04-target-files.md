# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `docs/tables-maisons-et-roles.md`
- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/migrations/versions/20260513_0089_rename_daily_planet_profiles.py`
- `backend/migrations/versions/20260513_0091_rename_planets_to_astral_planets.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/integration/test_migration_a_prediction_tables.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`

## Must search

- `rg --fixed-strings "house_profiles" backend/app backend/migrations docs/tables-maisons-et-roles.md`
- `rg --fixed-strings "house_category_weights" backend/app backend/migrations docs/tables-maisons-et-roles.md`
- `rg --fixed-strings "\"houses\"" backend/app backend/migrations docs/tables-maisons-et-roles.md`

## Likely modified

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/migrations/versions/20260513_0094_rename_house_tables.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/integration/test_migration_a_prediction_tables.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `docs/tables-maisons-et-roles.md`
- `_condamad/stories/renommer-tables-maisons-astrales/generated/*.md`
- `_condamad/stories/story-status.md`

## Forbidden unless directly justified

- Frontend files.
- Runtime JSON payload contracts using `houses`.
- Unrelated migrations and historical docs outside the target doc.
