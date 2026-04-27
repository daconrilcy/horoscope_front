from __future__ import annotations

from typing import Any

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.api.errors.raising import ApiHttpError
from app.core.auth_context import AuthenticatedUser
from app.core.rbac import is_valid_role
from app.core.security import SecurityError, decode_token
from app.infra.db.repositories.user_repository import UserRepository
from app.infra.db.session import get_db_session


class UserAuthenticationError(ApiHttpError):
    """Erreur applicative d'authentification utilisateur."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
            details=details or {},
        )


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

    if user.is_suspended:
        raise UserAuthenticationError(
            code="account_suspended",
            message="this account is suspended",
            status_code=403,
            details={},
        )

    return AuthenticatedUser(
        id=user.id,
        role=user.role,
        email=user.email,
        created_at=user.created_at,
    )


def require_admin_user(
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> AuthenticatedUser:
    if user.role != "admin":
        raise UserAuthenticationError(
            code="insufficient_role",
            message="admin role is required",
            status_code=403,
            details={"required_role": "admin", "actual_role": user.role},
        )
    return user


def require_ops_user(
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> AuthenticatedUser:
    if user.role not in {"ops", "admin"}:
        raise UserAuthenticationError(
            code="insufficient_role",
            message="ops or admin role is required",
            status_code=403,
            details={"required_roles": "ops, admin", "actual_role": user.role},
        )
    return user


def get_optional_authenticated_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db_session),
) -> AuthenticatedUser | None:
    if authorization is None:
        return None
    return require_authenticated_user(authorization=authorization, db=db)
