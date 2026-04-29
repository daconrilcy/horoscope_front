# DB Session Migration Batches

| Batch | Scope | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| B1 | `backend/tests` direct imports | `backend/tests/evaluation/__init__.py`, `backend/tests/unit/test_incident_service_user_statuses.py`, and subprocess-sensitive integration flows use `tests.integration.app_db`. | `pytest -q tests/integration/test_backend_sqlite_alignment.py`; full `pytest -q`. | PASS |
| B2 | `backend/app/tests/integration` direct imports | Integration tests now use `app.tests.helpers.db_session`; isolated fixtures route their session factory through the helper instead of direct production imports. | `pytest -q app/tests/integration/test_reference_data_api.py`; full `pytest -q`. | PASS |
| B3 | `backend/app/tests/unit` direct imports | Unit DB tests now use `app_test_engine()` and `open_app_test_db_session()`. | `pytest -q app/tests/unit/test_reference_data_service.py`; full `pytest -q`. | PASS |
| B4 | `backend/app/tests/conftest.py` global redirection | Removed process-wide assignment to `db_session_module.engine` and `db_session_module.SessionLocal`; FastAPI DB access is overridden explicitly. | `pytest -q app/tests/unit/test_backend_db_test_harness.py`; `pytest --collect-only -q --ignore=.tmp-pytest`. | PASS |

No compatibility import path or `SessionLocal` wrapper was added.
