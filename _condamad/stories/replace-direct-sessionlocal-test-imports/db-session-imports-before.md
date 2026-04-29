# Direct DB Session Import Baseline

Baseline capture before migration.

- Command: `rg -n "from app\.infra\.db\.session import (SessionLocal|engine)|import app\.infra\.db\.session|db_session_module\.(SessionLocal|engine) =" backend/app/tests backend/tests -g "*.py"`
- Source audit: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- Baseline finding: F-101 reported 89 files importing `SessionLocal` directly.
- Additional baseline evidence captured in this execution: `backend/app/tests/conftest.py` assigned both `db_session_module.engine` and `db_session_module.SessionLocal`.

The migration target was zero direct test imports of `SessionLocal` or `engine`
from `app.infra.db.session`, plus no global assignment in `backend/app/tests/conftest.py`.
