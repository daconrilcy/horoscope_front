from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.main import app
from app.startup.dev_seed import seed_dev_admin

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
    monkeypatch.setattr(db_session_module, "engine", test_engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", test_session_local)
    Base.metadata.create_all(bind=test_engine)
    yield test_session_local
    test_engine.dispose()


def test_seed_dev_admin_success(test_db, monkeypatch: pytest.MonkeyPatch):
    # Setup: mock settings for dev env
    from app.startup import dev_seed

    # We patch the object attributes directly since 'settings' is already instantiated
    monkeypatch.setattr(dev_seed.settings, "app_env", "dev")
    monkeypatch.setattr(dev_seed.settings, "seed_admin", False)

    # Run seed
    seed_dev_admin()

    # Verify
    with test_db() as db:
        admin = db.scalar(select(UserModel).where(UserModel.role == "admin"))
        assert admin is not None
        assert admin.email == "admin@test.com"


def test_seed_dev_admin_idempotent(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.startup import dev_seed

    monkeypatch.setattr(dev_seed.settings, "app_env", "dev")
    monkeypatch.setattr(dev_seed.settings, "seed_admin", False)

    seed_dev_admin()
    seed_dev_admin()  # Second call

    with test_db() as db:
        admins = db.scalars(select(UserModel).where(UserModel.role == "admin")).all()
        assert len(admins) == 1


def test_seed_dev_admin_ignored_in_prod(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.startup import dev_seed

    monkeypatch.setattr(dev_seed.settings, "app_env", "production")
    monkeypatch.setattr(dev_seed.settings, "seed_admin", False)

    seed_dev_admin()

    with test_db() as db:
        admin = db.scalar(select(UserModel).where(UserModel.role == "admin"))
        assert admin is None


def test_seed_dev_admin_login_works(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.startup import dev_seed

    monkeypatch.setattr(dev_seed.settings, "app_env", "dev")
    monkeypatch.setattr(dev_seed.settings, "seed_admin", False)

    seed_dev_admin()

    # Try login via API
    # Note: the app's AuthService needs to use the same patched SessionLocal
    # In test_auth_api.py, they patch db_session_module.SessionLocal which works
    # because AuthService imports app.infra.db.repositories.* which likely use it.

    response = client.post(
        "/v1/auth/login", json={"email": "admin@test.com", "password": "admin123"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["user"]["role"] == "admin"
    assert "access_token" in response.json()["data"]["tokens"]
