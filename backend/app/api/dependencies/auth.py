from __future__ import annotations

from typing import Any

from fastapi import Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.rbac import is_valid_role
from app.core.security import SecurityError, decode_token
from app.infra.db.repositories.user_repository import UserRepository
from app.infra.db.session import get_db_session


class AuthenticatedUser(BaseModel):
    id: int
    role: str


class UserAuthenticationError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


def require_authenticated_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db_session),
) -> AuthenticatedUser:
    if authorization is None or not authorization.startswith("Bearer "):
        raise UserAuthenticationError(
            code="missing_access_token",
            message="missing bearer access token",
            status_code=401,
            details={},
        )

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, expected_type="access")
    except SecurityError as error:
        raise UserAuthenticationError(
            code=error.code,
            message=error.message,
            status_code=401,
            details=error.details,
        ) from error

    subject = payload.get("sub")
    role = payload.get("role")
    if not isinstance(subject, str) or not subject.isdigit():
        raise UserAuthenticationError(
            code="invalid_token",
            message="token is invalid",
            status_code=401,
            details={},
        )
    if not isinstance(role, str) or not is_valid_role(role):
        raise UserAuthenticationError(
            code="insufficient_role",
            message="role is not allowed",
            status_code=403,
            details={"role": str(role)},
        )

    user = UserRepository(db).get_by_id(int(subject))
    if user is None:
        raise UserAuthenticationError(
            code="invalid_token",
            message="token subject is invalid",
            status_code=401,
            details={},
        )

    return AuthenticatedUser(id=user.id, role=user.role)


def get_optional_authenticated_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db_session),
) -> AuthenticatedUser | None:
    if authorization is None:
        return None
    return require_authenticated_user(authorization=authorization, db=db)
