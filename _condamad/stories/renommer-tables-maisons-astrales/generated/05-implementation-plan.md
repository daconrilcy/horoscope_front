# Implementation Plan

## Findings

- `PlanetProfileModel` already uses a renamed SQL table and has migration pattern `20260513_0089`.
- `PlanetModel` already uses `astral_planets` and migration pattern `20260513_0091`.
- `HouseModel`, `HouseProfileModel`, and `HouseCategoryWeightModel` still use old SQL names.
- `RG-092` applies: house vocabulary must remain non-versioned after rename.

## Patch

1. Update SQLAlchemy `__tablename__` and FK targets.
2. Add Alembic migration `20260513_0094_rename_house_tables.py` after `20260513_0093`.
3. Update targeted migration/model tests to assert canonical names and old-name absence.
4. Update `docs/tables-maisons-et-roles.md`.
5. Complete traceability/final evidence and story status.

## Tests

- Run only targeted backend tests and changed-file lint/format checks in the venv.
- Run No Legacy scans and diff checks.

## Rollback

- Alembic downgrade renames the three tables back to their previous names and restores old index names.
