# Validation Plan

## Environment assumptions

- PowerShell on Windows.
- Every Python command is run after `.\.venv\Scripts\Activate.ps1`.
- Working directory for Python validation: `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| SQLite/Alembic alignment | `pytest -q tests/integration/test_backend_sqlite_alignment.py` | `backend/` | yes | all tests pass |
| DB harness guard | `pytest -q app/tests/unit/test_backend_db_test_harness.py` | `backend/` | yes | all tests pass |
| Migrated app test lot | `pytest -q app/tests/integration/test_admin_content_api.py` | `backend/` | yes | all tests pass |
| Migrated backend test lot | `pytest -q tests/integration/test_llm_release.py -k "activation_evidence_requires_timezone_aware_datetime or activate_endpoint_rejects_naive_generated_at_with_422 or llm_release_lifecycle or snapshot_validation_independence"` | `backend/` | yes | selected migrated DB subset passes |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Direct import inventory | `rg -n "from app\.infra\.db\.session import .*\b(SessionLocal|engine)\b|db_session_module\.SessionLocal" app/tests tests -g "*.py"` | `backend/` | yes | only allowlisted files plus canonical helpers |
| Main DB create_all scan | `rg -n "Base\.metadata\.create_all" app/tests tests -g "*.py"` | `backend/` | yes | no `create_all` on `horoscope.db`; scoped test DB usage classified |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | formatting completes |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Collect tests | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | collection succeeds |
| Full backend tests | `pytest -q` | `backend/` | yes | all tests pass or limitation recorded |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Diff whitespace | `git diff --check` | repo root | yes | no errors |
| Final status | `git status --short` | repo root | yes | expected files only |
