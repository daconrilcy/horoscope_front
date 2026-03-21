from __future__ import annotations

from collections.abc import Generator
from threading import Lock

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.infra.db import models as _models  # noqa: F401

connect_args: dict[str, object] = {}
engine_kwargs: dict[str, object] = {"future": True}
if settings.database_url.startswith("sqlite"):
    # timeout=30: wait up to 30s when DB is locked (default is 5s)
    connect_args = {"check_same_thread": False, "timeout": 30}

engine = create_engine(settings.database_url, connect_args=connect_args, **engine_kwargs)

if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_wal_mode(dbapi_conn, _connection_record):  # type: ignore[misc]
        dbapi_conn.execute("PRAGMA journal_mode=WAL")
        dbapi_conn.execute("PRAGMA synchronous=NORMAL")
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
_bootstrap_lock = Lock()
_local_schema_ready = False


def _ensure_local_sqlite_schema_ready_once() -> None:
    global _local_schema_ready
    if _local_schema_ready:
        return

    with _bootstrap_lock:
        if _local_schema_ready:
            return
        from app.infra.db.bootstrap import ensure_local_sqlite_schema_ready

        ensure_local_sqlite_schema_ready()
        _local_schema_ready = True


def get_db_session() -> Generator[Session, None, None]:
    _ensure_local_sqlite_schema_ready_once()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
