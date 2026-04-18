"""Accès au moteur / `SessionLocal` effectifs pour les tests sous `tests/integration/`."""

from __future__ import annotations

from sqlalchemy.engine import Engine


def app_engine() -> Engine:
    """Après un éventuel remplacement global dans `app/tests/conftest.py`."""
    from app.infra.db import session as db_session_module

    return db_session_module.engine


def open_app_db_session():
    """Comme `app_engine`, pour les sessions ORM."""
    from app.infra.db import session as db_session_module

    return db_session_module.SessionLocal()
