"""Tests d'intégration du catalogue public des langues d'interface."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models.reference import LanguageModel
from app.main import app
from app.tests.helpers.db_session import (
    reset_app_test_db_session_factory,
    use_app_test_db_session_factory,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Isole la base pour vérifier uniquement les langues seedées par le test."""
    database_url = f"sqlite:///{(tmp_path / 'test-reference-languages.db').as_posix()}"
    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    use_app_test_db_session_factory(test_session_local)
    Base.metadata.create_all(bind=test_engine)
    with test_session_local() as db:
        db.add_all(
            [
                LanguageModel(id=2, code="fr", name="french"),
                LanguageModel(id=1, code="en", name="english"),
            ]
        )
        db.commit()
    try:
        yield
    finally:
        reset_app_test_db_session_factory()
        test_engine.dispose()


def test_list_languages_returns_table_languages_sorted_by_code() -> None:
    """Vérifie que l'API expose la table `languages` sans constante front cachée."""
    response = client.get("/v1/reference-data/languages")

    assert response.status_code == 200
    assert response.json()["data"] == [
        {"code": "en", "name": "english"},
        {"code": "fr", "name": "french"},
    ]
