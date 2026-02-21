from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import delete

from app.core.security import (
    SecurityError,
    create_access_token,
    create_refresh_token,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService, AuthServiceError


def _cleanup_users() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserModel))
        db.commit()


def test_hash_and_verify_password() -> None:
    password_hash = hash_password("super-secret-password")
    assert verify_password("super-secret-password", password_hash)
    assert not verify_password("wrong-password", password_hash)
    assert not verify_password("wrong-password", "invalid-hash")


def test_create_and_decode_tokens() -> None:
    access = create_access_token("1", "user")
    refresh = create_refresh_token("1", "user")
    access_payload = decode_token(access, expected_type="access")
    refresh_payload = decode_token(refresh, expected_type="refresh")
    assert access_payload["sub"] == "1"
    assert refresh_payload["sub"] == "1"


def test_decode_token_expired_returns_specific_error() -> None:
    expired = create_token(subject="1", role="user", token_type="access", expires_minutes=-1)
    try:
        decode_token(expired, expected_type="access")
    except SecurityError as error:
        assert error.code == "token_expired"
    else:
        raise AssertionError("Expected SecurityError")


def test_decode_token_accepts_previous_rotation_key(monkeypatch: object) -> None:
    from app.core import security as security_module

    monkeypatch.setattr(security_module.settings, "jwt_secret_key", "jwt-current-key")
    monkeypatch.setattr(security_module.settings, "jwt_previous_secret_keys", ["jwt-previous-key"])
    monkeypatch.setattr(security_module.settings, "jwt_algorithm", "HS256")

    payload = {
        "sub": "1",
        "role": "user",
        "token_type": "access",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=10),
    }
    token = jwt.encode(payload, "jwt-previous-key", algorithm="HS256")
    decoded = decode_token(token, expected_type="access")
    assert decoded["sub"] == "1"


def test_register_and_login_flow() -> None:
    _cleanup_users()
    with SessionLocal() as db:
        register_result = AuthService.register(
            db,
            email="user@example.com",
            password="strong-pass-123",
        )
        db.commit()
        login_result = AuthService.login(
            db,
            email="user@example.com",
            password="strong-pass-123",
        )

    assert register_result.user.email == "user@example.com"
    assert login_result.user.email == "user@example.com"


def test_refresh_token_rotation_rejects_replay() -> None:
    _cleanup_users()
    with SessionLocal() as db:
        register_result = AuthService.register(
            db,
            email="rotate@example.com",
            password="strong-pass-123",
        )
        db.commit()
        first_refresh = AuthService.refresh(db, register_result.tokens.refresh_token)
        db.commit()
        try:
            AuthService.refresh(db, register_result.tokens.refresh_token)
        except AuthServiceError as error:
            assert error.code == "invalid_token"
        else:
            raise AssertionError("Expected AuthServiceError")

    assert first_refresh.access_token


def test_login_invalid_credentials() -> None:
    _cleanup_users()
    with SessionLocal() as db:
        AuthService.register(db, email="user@example.com", password="strong-pass-123")
        db.commit()
        try:
            AuthService.login(db, email="user@example.com", password="bad-password")
        except AuthServiceError as error:
            assert error.code == "invalid_credentials"
        else:
            raise AssertionError("Expected AuthServiceError")
