# Implementation Plan

1. Inspect current Alembic head/recent revisions and existing schema tests.
2. Update `PlanetProfileModel.__tablename__` to `astral_prediction_daily_planet_profiles`.
3. Add a new Alembic migration that renames `planet_profiles` and normalizes index/constraint names for the new table.
4. Update schema tests and active docs to the new table name.
5. Run targeted backend validation with venv activated.
6. Complete traceability, final evidence, and story registry.

Rollback strategy: revert model/test/doc changes and downgrade the new migration to restore `planet_profiles`.

