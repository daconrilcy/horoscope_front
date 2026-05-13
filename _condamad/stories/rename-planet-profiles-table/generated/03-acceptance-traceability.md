# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `PlanetProfileModel` uses `astral_prediction_daily_planet_profiles`. | `PlanetProfileModel.__tablename__` updated. | Targeted repository/migration tests passed. | Passed |
| AC2 | Alembic renames existing table without data loss and preserves useful indexes/constraints. | Added `20260513_0089_rename_daily_planet_profiles.py` with upgrade/downgrade rename and index normalization. | Targeted Alembic upgrade/downgrade tests passed on temporary DB. | Passed |
| AC3 | Tests/schema assertions expect the new table name. | Updated schema/reference migration tests. | Targeted pytest command passed. | Passed |
| AC4 | Active docs mention the new SQL table name. | Updated `docs/tables-planetes-et-roles.md`. | Canonical-name search passed; old active doc table name removed. | Passed |
| AC5 | Old `planet_profiles` remains only for Python runtime attributes/functions, historical artifacts, or migration history. | No compatibility table/view/shim added; runtime field names unchanged by design. | Scans classify remaining hits as runtime keys, negative assertions, or historical migrations. | Passed |
