# Validation Plan

| Command | Purpose | Expected success | Required |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py app/tests/unit/test_prediction_reference_repository.py -q` | Targeted schema, seed, repository validation. | All selected tests pass. | yes |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | Format backend Python. | No formatting error. | yes |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | Lint backend Python. | No lint error. | yes |
| `rg -n "__tablename__ = \"planet_profiles\"|create_table\\(\"planet_profiles\"|drop_table\\(\"planet_profiles\"" backend/app backend/tests docs` | Ensure no active model/test/doc recreates old table. | Zero active hits or historical migration classification. | yes |
| `rg -n "astral_prediction_daily_planet_profiles" backend docs` | Confirm canonical table name is present in code/docs/tests. | Hits in model, migration, tests/docs. | yes |

If a command cannot run, record exact reason and risk in final evidence.

