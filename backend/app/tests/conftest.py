"""Configuration pytest globale pour isoler les tests `app/tests`."""

from __future__ import annotations

import os

import pytest

from app.tests.helpers.db_session import (
    app_test_database_url,
    dispose_app_test_engine,
    open_app_test_db_session,
    override_app_test_db_session,
)

os.environ["DATABASE_URL"] = app_test_database_url()

from app.infra.db.base import Base
from app.infra.db.session import get_db_session
from app.main import app


def _clear_db_session_tables(db) -> None:
    """Vide les tables ORM connues pour isoler les tests qui committent."""
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()


@pytest.fixture(scope="session", autouse=True)
def _dispose_app_test_db_after_app_tests() -> None:
    try:
        yield
    finally:
        dispose_app_test_engine()


@pytest.fixture(autouse=True)
def _install_app_test_db_dependency_override() -> None:
    """Route explicitement les dépendances FastAPI vers la DB de test canonique."""
    app.dependency_overrides[get_db_session] = override_app_test_db_session
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture
def db_session():
    """Fournit une session ORM explicite sur la base canonique des tests `app/tests`."""
    db = open_app_test_db_session()
    try:
        _clear_db_session_tables(db)
        yield db
    finally:
        db.rollback()
        _clear_db_session_tables(db)
        db.close()
