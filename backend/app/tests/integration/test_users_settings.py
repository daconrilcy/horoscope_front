from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test-users-settings.db').as_posix()}"
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
    try:
        yield
    finally:
        test_engine.dispose()


@pytest.fixture
def auth_token() -> str:
    payload = {"email": "test@example.com", "password": "password123"}
    response = client.post("/v1/auth/register", json=payload)
    assert response.status_code == 200
    return response.json()["data"]["tokens"]["access_token"]


def test_get_me_settings_authenticated(auth_token: str):
    response = client.get(
        "/v1/users/me/settings", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "astrologer_profile" in data
    assert "default_astrologer_id" in data
    assert data["astrologer_profile"] == "standard"
    assert data["default_astrologer_id"] is None


def test_patch_me_settings_astrologer_profile(auth_token: str):
    # Change to humaniste
    response = client.patch(
        "/v1/users/me/settings",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"astrologer_profile": "humaniste"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["astrologer_profile"] == "humaniste"

    # Verify via GET
    response = client.get(
        "/v1/users/me/settings", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.json()["data"]["astrologer_profile"] == "humaniste"


def test_patch_me_settings_default_astrologer_id(auth_token: str):
    # Set a default astrologer
    astro_id = "astro-123"
    response = client.patch(
        "/v1/users/me/settings",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"default_astrologer_id": astro_id},
    )
    assert response.status_code == 200
    assert response.json()["data"]["default_astrologer_id"] == astro_id

    # Verify via GET
    response = client.get(
        "/v1/users/me/settings", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.json()["data"]["default_astrologer_id"] == astro_id

    # Reset to None
    response = client.patch(
        "/v1/users/me/settings",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"default_astrologer_id": None},
    )
    assert response.status_code == 200
    assert response.json()["data"]["default_astrologer_id"] is None


def test_patch_me_settings_invalid_profile(auth_token: str):
    response = client.patch(
        "/v1/users/me/settings",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"astrologer_profile": "invalid_one"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_astrologer_profile"


def test_patch_me_settings_partial_update(auth_token: str):
    # Initial state
    client.patch(
        "/v1/users/me/settings",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"astrologer_profile": "karmique", "default_astrologer_id": "original-astro"},
    )

    # Partial update: only profile
    response = client.patch(
        "/v1/users/me/settings",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"astrologer_profile": "vedique"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["astrologer_profile"] == "vedique"
    assert data["default_astrologer_id"] == "original-astro"

    # Partial update: only default_astrologer_id
    response = client.patch(
        "/v1/users/me/settings",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"default_astrologer_id": "new-astro"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["astrologer_profile"] == "vedique"
    assert data["default_astrologer_id"] == "new-astro"
