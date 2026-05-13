# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Backend commands run from `backend/` after `.\.venv\Scripts\Activate.ps1` from repository root.
- Full test suite is explicitly skipped by user request.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted repository/model tests | `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py -q` | `backend/` | yes | all selected tests pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Active old table names in app/tests | `rg -n --fixed-strings "house_profiles" app tests` | `backend/` | yes | no active SQL table name hits outside object-field names/tests intentionally classified |
| Active old table names in app/tests | `rg -n --fixed-strings "house_category_weights" app tests` | `backend/` | yes | no active SQL table name hits outside object-field names/tests intentionally classified |
| Stable house table versioning guard | `rg -n "HouseModel\.reference_version_id|HouseModel\(reference_version_id|__tablename__ = \"houses\"|ForeignKey\(\"houses\.id\"\)" app tests` | `backend/` | yes | zero hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint changed backend files | `ruff check app/infra/db/models/reference.py app/infra/db/models/prediction_reference.py app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py migrations/versions/20260513_0094_rename_house_tables.py` | `backend/` | yes | no lint errors |
| Format check changed backend files | `ruff format --check app/infra/db/models/reference.py app/infra/db/models/prediction_reference.py app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py migrations/versions/20260513_0094_rename_house_tables.py` | `backend/` | yes | no formatting changes required |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend pytest | `pytest -q` | `backend/` | no | skipped by explicit user request |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed by Codex |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace or conflict marker issues |
| Final status | `git status --short` | repo root | yes | expected files plus pre-existing dirty files |
