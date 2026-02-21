from __future__ import annotations

import hashlib
import hmac
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings


class SecurityError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{salt.hex()}${hashed.hex()}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_password_hash.split("$", 1)
    except ValueError:
        return False
    try:
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
    except ValueError:
        return False

    candidate_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return hmac.compare_digest(candidate_hash, expected_hash)


def create_token(
    subject: str,
    role: str,
    token_type: str,
    expires_minutes: int,
    jti: str | None = None,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "role": role,
        "token_type": token_type,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    if jti is not None:
        payload["jti"] = jti
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, role: str) -> str:
    return create_token(subject, role, "access", settings.jwt_access_minutes)


def create_refresh_token(subject: str, role: str) -> str:
    return create_token(
        subject,
        role,
        "refresh",
        settings.jwt_refresh_minutes,
        jti=str(uuid.uuid4()),
    )


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] | None = None
    expired_error: Exception | None = None
    for secret_key in settings.jwt_verification_secret_keys:
        try:
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            break
        except jwt.ExpiredSignatureError as error:
            expired_error = error
        except jwt.PyJWTError:
            continue
    if payload is None and expired_error is not None:
        raise SecurityError(
            code="token_expired",
            message="token is expired",
            details={},
        ) from expired_error
    if payload is None:
        raise SecurityError(
            code="invalid_token",
            message="token is invalid or expired",
            details={},
        )

    token_type = payload.get("token_type")
    if expected_type and token_type != expected_type:
        raise SecurityError(
            code="invalid_token_type",
            message="token type is invalid",
            details={"expected_type": expected_type},
        )
    return payload
