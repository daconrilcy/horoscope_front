# Global DB Redirection Decision

Decision: remove the global mutation of `app.infra.db.session` from `backend/app/tests/conftest.py`.

Replacement:

- `backend/app/tests/helpers/db_session.py` owns the app-test SQLite engine and session factory.
- `backend/app/tests/conftest.py` installs an explicit FastAPI dependency override for `get_db_session`.
- Isolated DB fixtures can temporarily route their local `sessionmaker` through the helper-owned active factory.
- `backend/tests/integration/app_db.py` remains the canonical helper for `backend/tests` flows that intentionally use the configured application DB.

Rejected path:

- no `SessionLocal` compatibility wrapper;
- no re-export preserving the production import path;
- no global `db_session_module.SessionLocal = ...` assignment.
