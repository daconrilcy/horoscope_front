"""Helper canonique pour la session DB effective des tests `tests/integration`."""

from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def app_engine() -> Engine:
    """Retourne le moteur applicatif effectif après l'alignement SQLite/Alembic."""
    from app.infra.db import session as db_session_module

    return db_session_module.engine


def open_app_db_session() -> Session:
    """Ouvre une session ORM via le propriétaire canonique de test."""
    from app.infra.db import session as db_session_module

    return db_session_module.SessionLocal()
