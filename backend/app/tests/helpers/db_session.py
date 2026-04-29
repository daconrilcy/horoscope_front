"""Helper canonique pour accéder à la base de test effective de `app/tests`."""

from __future__ import annotations

import atexit
import uuid
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_TEST_DB_ROOT = Path(__file__).resolve().parents[3] / ".tmp-pytest"
_TEST_DB_ROOT.mkdir(parents=True, exist_ok=True)
_TEST_DB_PATH = _TEST_DB_ROOT / f"horoscope-pytest-db-{uuid.uuid4().hex}.sqlite3"


def _cleanup_test_db_file() -> None:
    """Supprime le fichier SQLite de test quand le processus pytest se termine."""
    try:
        _TEST_DB_PATH.unlink(missing_ok=True)
    except PermissionError:
        # Pytest peut encore tenir une connexion SQLite pendant l'arrêt de l'interpréteur.
        pass


atexit.register(_cleanup_test_db_file)


def _build_test_engine() -> Engine:
    """Construit le moteur SQLite fichier partagé par les tests `app/tests`."""
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
_TEST_SESSION_FACTORY = sessionmaker(
    bind=_TEST_ENGINE,
    autoflush=False,
    autocommit=False,
    future=True,
)
_ACTIVE_SESSION_FACTORY = _TEST_SESSION_FACTORY


def app_test_database_url() -> str:
    """Retourne l'URL SQLite possédée par le harnais DB `app/tests`."""
    return f"sqlite:///{_TEST_DB_PATH.as_posix()}"


def app_test_engine() -> Engine:
    """Retourne le moteur DB possédé explicitement par le harnais `app/tests`."""
    return _TEST_ENGINE


def open_app_test_db_session() -> Session:
    """Ouvre une session ORM sur la base de test effective du harnais `app/tests`."""
    return _ACTIVE_SESSION_FACTORY()


def use_app_test_db_session_factory(session_factory) -> None:
    """Remplace temporairement la factory DB active pour un test isolé."""
    global _ACTIVE_SESSION_FACTORY
    _ACTIVE_SESSION_FACTORY = session_factory


def reset_app_test_db_session_factory() -> None:
    """Restaure la factory DB partagée du harnais `app/tests`."""
    global _ACTIVE_SESSION_FACTORY
    _ACTIVE_SESSION_FACTORY = _TEST_SESSION_FACTORY


def override_app_test_db_session() -> Generator[Session, None, None]:
    """Fournit une dépendance FastAPI explicite vers la session DB de test."""
    db = open_app_test_db_session()
    try:
        yield db
    finally:
        db.close()


def dispose_app_test_engine() -> None:
    """Libère le moteur SQLite de test en fin de session pytest."""
    _TEST_ENGINE.dispose()
