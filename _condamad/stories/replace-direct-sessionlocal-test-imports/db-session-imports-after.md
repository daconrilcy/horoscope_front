# Direct DB Session Import After Snapshot

After migration, the forbidden import scans are zero-hit.

| Check | Command | Result |
|---|---|---|
| Direct `SessionLocal` / `engine` imports | `cd backend; rg -n "from app\.infra\.db\.session import (SessionLocal|engine)" app/tests tests -g "*.py"` | zero hits, exit 1 |
| Broad direct import form | `cd backend; rg -n "from app\.infra\.db\.session import .*\\b(SessionLocal|engine)\\b" app/tests tests -g "*.py"` | zero hits, exit 1 |
| Global redirection assignment | `cd backend; rg -n "db_session_module\.(SessionLocal|engine) =" app/tests/conftest.py` | zero hits, exit 1 |

Remaining classified internal access:

- `backend/tests/integration/app_db.py` calls `db_session_module.SessionLocal()` as the canonical helper for `backend/tests`.
