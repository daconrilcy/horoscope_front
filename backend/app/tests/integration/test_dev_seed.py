"""Tests d'intégration du seed administrateur de développement."""

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.main import app
from app.startup.dev_seed import seed_dev_admin
from app.tests.helpers.db_session import (
    open_app_test_db_session,
    reset_app_test_db_session_factory,
    use_app_test_db_session_factory,
)

client = TestClient(app)


@pytest.fixture
def test_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    database_url = f"sqlite:///{(tmp_path / 'test_seed.db').as_posix()}"
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
    from app.startup import dev_seed

    monkeypatch.setattr(dev_seed, "_open_dev_seed_session", open_app_test_db_session)
    Base.metadata.create_all(bind=test_engine)
    try:
        yield test_session_local
    finally:
        reset_app_test_db_session_factory()
        test_engine.dispose()


def test_seed_dev_admin_success(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.startup import dev_seed

    monkeypatch.setattr(dev_seed.settings, "app_env", "dev")
    monkeypatch.setattr(dev_seed.settings, "seed_admin", False)

    asyncio.run(seed_dev_admin())

    with test_db() as db:
        admin = db.scalar(select(UserModel).where(UserModel.role == "admin"))
        assert admin is not None
        assert admin.email == "admin@test.com"


def test_seed_dev_admin_idempotent(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.startup import dev_seed

    monkeypatch.setattr(dev_seed.settings, "app_env", "dev")
    monkeypatch.setattr(dev_seed.settings, "seed_admin", False)

    asyncio.run(seed_dev_admin())
    asyncio.run(seed_dev_admin())

    with test_db() as db:
        admins = db.scalars(select(UserModel).where(UserModel.role == "admin")).all()
        assert len(admins) == 1


def test_seed_dev_admin_ignored_in_prod(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.startup import dev_seed

    monkeypatch.setattr(dev_seed.settings, "app_env", "production")
    monkeypatch.setattr(dev_seed.settings, "seed_admin", False)

    asyncio.run(seed_dev_admin())

    with test_db() as db:
        admin = db.scalar(select(UserModel).where(UserModel.role == "admin"))
        assert admin is None


def test_seed_dev_admin_login_works(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.startup import dev_seed

    monkeypatch.setattr(dev_seed.settings, "app_env", "dev")
    monkeypatch.setattr(dev_seed.settings, "seed_admin", False)

    asyncio.run(seed_dev_admin())

    response = client.post(
        "/v1/auth/login", json={"email": "admin@test.com", "password": "admin123"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["user"]["role"] == "admin"
    assert "access_token" in response.json()["data"]["tokens"]
