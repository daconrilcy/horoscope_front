# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | SQLAlchemy models use canonical table names and FKs to `astral_houses.id`. | `HouseModel`, `HouseProfileModel`, `HouseCategoryWeightModel` updated. | `test_house_models_use_canonical_astral_table_names`; strict `__tablename__`/FK scan zero-hit. | PASS |
| AC2 | Alembic migration renames three tables with downgrade support. | `20260513_0094_rename_house_tables.py` added with upgrade/downgrade rename and canonical indexes. | Targeted migration tests passed; `alembic heads` reports `20260513_0094 (head)`. | PASS |
| AC3 | Tests expect new names and old SQL names are not active at head. | Migration tests assert canonical tables/FKs and absence of old table names. | `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py -q` passed. | PASS |
| AC4 | Documentation uses canonical SQL names. | `docs/tables-maisons-et-roles.md` updated for canonical SQL table names. | Targeted search reviewed; remaining old names are Python runtime fields/methods or historical migration/downgrade references. | PASS |
| AC5 | Only targeted tests/checks are run. | Full suite excluded from validation plan. | Commands logged in final evidence; full `pytest -q` intentionally skipped. | PASS |
