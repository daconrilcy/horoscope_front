# No Legacy / DRY Guardrails

## Canonical SQL table

- Canonical table: `astral_prediction_daily_planet_profiles`.
- Legacy SQL table name: `planet_profiles`.

## Forbidden

- Keeping an active SQLAlchemy model mapped to `planet_profiles`.
- Creating a compatibility view/table alias named `planet_profiles`.
- Dual-read or dual-write logic between both table names.
- Updating only docs while leaving runtime schema on the old name.

## Allowed residual references

- Python attributes/functions named `planet_profiles`, because they are DTO/runtime collection names, not SQL table names.
- Alembic historical revisions that create or mutate the old table before the rename migration.
- BMAD/CONDAMAD historical artifacts.

## Required evidence

- Targeted tests for model/repository/migrations/seeds.
- Scan proving active model/tests/docs use the canonical table name.
- Classification of remaining `planet_profiles` hits.

