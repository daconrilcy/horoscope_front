# Validation Plan

## Environment assumptions

- PowerShell on Windows.
- All Python commands must activate `.\.venv\Scripts\Activate.ps1` first.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted migration/reference tests | `.\\.venv\\Scripts\\Activate.ps1; pytest app/tests/integration/test_reference_data_migrations.py app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q` | `backend` | yes | tests pass |
| Lint | `.\\.venv\\Scripts\\Activate.ps1; ruff check .` | `backend` | yes | no lint errors |
| Format check | `.\\.venv\\Scripts\\Activate.ps1; ruff format --check .` | `backend` | yes | no formatting drift |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Old score profile table and old DB code columns absent | `rg -n "astral_essential_dignity_score_profiles|accidental_dignity_type_code" backend docs/db_seeder/astrology` | repo root | yes | no active old table or accidental code-column refs |
| Score profile linked by DB id | `rg -n "score_profile_code" backend/app/infra/db/models backend/migrations docs/db_seeder/astrology` | repo root | yes | no DB schema/seed column uses; repository lookup parameters are out of scope |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff check | `git diff --check` | repo root | yes | no whitespace/conflict errors |
| Status | `git status --short` | repo root | yes | expected files only |
