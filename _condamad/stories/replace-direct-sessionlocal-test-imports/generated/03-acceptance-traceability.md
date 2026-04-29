# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Direct DB import inventory is persisted. | Added before/after import inventory artifacts and emptied the DB session allowlist. | `db-session-imports-before.md`; `db-session-imports-after.md`; `pytest -q app/tests/unit/test_backend_db_test_harness.py`. | PASS |
| AC2 | Canonical DB helpers own test sessions. | Migrated direct `SessionLocal` / `engine` test consumers to `app.tests.helpers.db_session` or `tests.integration.app_db`. | `pytest -q app/tests/unit/test_backend_db_test_harness.py`; full `pytest -q`. | PASS |
| AC3 | SQLite alignment still runs. | Kept `ensure_configured_sqlite_file_matches_alembic_head` in the backend integration alignment path and app integration conftest. | `pytest -q tests/integration/test_backend_sqlite_alignment.py`. | PASS |
| AC4 | Global DB redirection is absent. | Removed `db_session_module.engine = ...` and `db_session_module.SessionLocal = ...` from `backend/app/tests/conftest.py`. | `rg -n "db_session_module\.(SessionLocal|engine) =" app/tests/conftest.py` returned zero hits. | PASS |
| AC5 | Batch evidence is complete. | Added `db-session-batches.md` and `global-db-redirection-decision.md`; completed final evidence. | `pytest --collect-only -q --ignore=.tmp-pytest`; full `pytest -q`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
