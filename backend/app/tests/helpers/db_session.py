"""Helper canonique pour accéder à la base de test effective de `app/tests`."""

from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def app_test_engine() -> Engine:
    """Retourne le moteur DB déjà remplacé et aligné par le harnais `app/tests`."""
    from app.infra.db import session as db_session_module

    return db_session_module.engine


def open_app_test_db_session() -> Session:
    """Ouvre une session ORM sur la base de test effective du harnais `app/tests`."""
    from app.infra.db import session as db_session_module

    return db_session_module.SessionLocal()
