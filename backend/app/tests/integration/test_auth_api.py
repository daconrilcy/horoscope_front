from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import sessionmaker

from app.core.security import create_token
from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_refresh_token import UserRefreshTokenModel
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_auth_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    database_url = f"sqlite:///{(tmp_path / 'auth-api.db').as_posix()}"
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


def _cleanup_users() -> None:
    Base.metadata.create_all(bind=db_session_module.engine)
    with db_session_module.SessionLocal() as db:
        db.execute(delete(AuditEventModel))
        db.execute(delete(UserRefreshTokenModel))
        db.execute(delete(UserModel))
        db.commit()


def test_register_success_and_duplicate_email() -> None:
    _cleanup_users()
    payload = {"email": "user@example.com", "password": "strong-pass-123"}
    first = client.post("/v1/auth/register", json=payload)
    duplicate = client.post("/v1/auth/register", json=payload)

    assert first.status_code == 200
    assert first.json()["data"]["user"]["email"] == "user@example.com"
    assert "access_token" in first.json()["data"]["tokens"]
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "email_already_registered"
    assert duplicate.json()["error"]["message"]
    assert "details" in duplicate.json()["error"]
    assert "request_id" in duplicate.json()["error"]


def test_register_invalid_email() -> None:
    _cleanup_users()
    response = client.post(
        "/v1/auth/register",
        json={"email": "not-an-email", "password": "strong-pass-123"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_email"
    assert response.json()["error"]["message"]
    assert "details" in response.json()["error"]
    assert "request_id" in response.json()["error"]


def test_login_success_and_invalid_credentials() -> None:
    _cleanup_users()
    client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "strong-pass-123"},
    )
    success = client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "strong-pass-123"},
    )
    invalid = client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "bad-pass"},
    )

    assert success.status_code == 200
    assert "refresh_token" in success.json()["data"]["tokens"]
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "invalid_credentials"
    assert invalid.json()["error"]["message"]
    assert "details" in invalid.json()["error"]
    assert "request_id" in invalid.json()["error"]


def test_refresh_success_and_invalid_token() -> None:
    _cleanup_users()
    register = client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "strong-pass-123"},
    )
    refresh_token = register.json()["data"]["tokens"]["refresh_token"]
    refreshed = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    invalid = client.post("/v1/auth/refresh", json={"refresh_token": "not-a-token"})

    assert refreshed.status_code == 200
    assert "access_token" in refreshed.json()["data"]
    assert "refresh_token" in refreshed.json()["data"]
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] in {"invalid_token", "invalid_token_type"}
    assert invalid.json()["error"]["message"]
    assert "details" in invalid.json()["error"]
    assert "request_id" in invalid.json()["error"]


def test_refresh_expired_token() -> None:
    _cleanup_users()
    expired_refresh = create_token(
        subject="1",
        role="user",
        token_type="refresh",
        expires_minutes=-1,
    )
    response = client.post("/v1/auth/refresh", json={"refresh_token": expired_refresh})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "token_expired"
    assert response.json()["error"]["message"]
    assert "details" in response.json()["error"]
    assert "request_id" in response.json()["error"]


def test_me_returns_authenticated_user_profile() -> None:
    _cleanup_users()
    register = client.post(
        "/v1/auth/register",
        json={"email": "me@example.com", "password": "strong-pass-123"},
    )
    access_token = register.json()["data"]["tokens"]["access_token"]
    response = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["role"] == "user"
    assert isinstance(data["id"], int)
    assert data["email"] == "me@example.com"
    assert "created_at" in data
    assert "request_id" in response.json()["meta"]


def test_me_requires_bearer_token() -> None:
    _cleanup_users()
    response = client.get("/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_refresh_token_replay_is_rejected() -> None:
    _cleanup_users()
    register = client.post(
        "/v1/auth/register",
        json={"email": "replay@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    refresh_token = register.json()["data"]["tokens"]["refresh_token"]

    first_refresh = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    replay_refresh = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert first_refresh.status_code == 200
    assert replay_refresh.status_code == 401
    assert replay_refresh.json()["error"]["code"] == "invalid_token"


def test_register_returns_503_when_audit_write_fails(monkeypatch: object) -> None:
    _cleanup_users()

    def _raise_audit_error(*args: object, **kwargs: object) -> None:
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr("app.api.v1.routers.auth.AuditService.record_event", _raise_audit_error)
    response = client.post(
        "/v1/auth/register",
        json={"email": "register-audit-fail@example.com", "password": "strong-pass-123"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "audit_unavailable"


def test_refresh_success_records_actor_identity_in_audit_event() -> None:
    _cleanup_users()
    register = client.post(
        "/v1/auth/register",
        json={"email": "refresh-audit@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    user_id = register.json()["data"]["user"]["id"]
    refresh_token = register.json()["data"]["tokens"]["refresh_token"]

    refreshed = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200

    with db_session_module.SessionLocal() as db:
        event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.action == "auth_refresh", AuditEventModel.status == "success")
            .order_by(AuditEventModel.id.desc())
            .limit(1)
        )
        assert event is not None
        assert event.actor_user_id == user_id
        assert event.actor_role == "user"
