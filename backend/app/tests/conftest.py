from __future__ import annotations

import atexit
import uuid
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module

_TEST_DB_ROOT = Path(__file__).resolve().parents[2] / ".tmp-pytest"
_TEST_DB_ROOT.mkdir(parents=True, exist_ok=True)
_TEST_DB_PATH = _TEST_DB_ROOT / f"horoscope-pytest-db-{uuid.uuid4().hex}.sqlite3"


def _cleanup_test_db_file() -> None:
    try:
        _TEST_DB_PATH.unlink(missing_ok=True)
    except PermissionError:
        # Pytest can still hold a SQLite connection when the interpreter exits.
        pass


atexit.register(_cleanup_test_db_file)


def _build_test_engine():
    engine = create_engine(
        f"sqlite:///{_TEST_DB_PATH.as_posix()}",
        connect_args={"check_same_thread": False, "timeout": 30},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, _connection_record):  # type: ignore[misc]
        dbapi_conn.execute("PRAGMA journal_mode=WAL")
        dbapi_conn.execute("PRAGMA synchronous=NORMAL")
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    return engine


_TEST_ENGINE = _build_test_engine()
_TEST_SESSION_LOCAL = sessionmaker(
    bind=_TEST_ENGINE,
    autoflush=False,
    autocommit=False,
    future=True,
)

# Global redirection for the whole pytest process.
# Many legacy tests import `engine` / `SessionLocal` directly from app.infra.db.session
# at module import time, so this patch must happen before those modules are imported.
db_session_module.engine = _TEST_ENGINE
db_session_module.SessionLocal = _TEST_SESSION_LOCAL
db_session_module._local_schema_ready = False
