from __future__ import annotations

from pydantic import BaseModel, EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.core.rbac import is_valid_role
from app.core.security import (
    SecurityError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.infra.db.repositories.user_refresh_token_repository import UserRefreshTokenRepository
from app.infra.db.repositories.user_repository import UserRepository


class AuthServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthUser(BaseModel):
    id: int
    email: str
    role: str


class AuthResponse(BaseModel):
    user: AuthUser
    tokens: AuthTokens


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    try:
        validated = TypeAdapter(EmailStr).validate_python(normalized)
    except ValidationError as error:
        raise AuthServiceError(
            code="invalid_email",
            message="email is invalid",
            details={"field": "email"},
        ) from error
    return str(validated)


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise AuthServiceError(
            code="invalid_password",
            message="password must be at least 8 characters",
            details={"field": "password"},
        )


class AuthService:
    @staticmethod
    def _extract_refresh_jti(refresh_token: str) -> str:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except SecurityError as error:
            raise AuthServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error
        jti = payload.get("jti")
        if not isinstance(jti, str) or not jti.strip():
            raise AuthServiceError(
                code="invalid_token",
                message="token is invalid",
                details={},
            )
        return jti.strip()

    @staticmethod
    def register(db: Session, email: str, password: str, role: str = "user") -> AuthResponse:
        normalized_email = _normalize_email(email)
        _validate_password(password)
        if not is_valid_role(role):
            raise AuthServiceError(
                code="invalid_role",
                message="role is invalid",
                details={"field": "role"},
            )

        repo = UserRepository(db)
        if repo.get_by_email(normalized_email) is not None:
            raise AuthServiceError(
                code="email_already_registered",
                message="email is already registered",
                details={"email": normalized_email},
            )

        user = repo.create(
            email=normalized_email,
            password_hash=hash_password(password),
            role=role,
        )
        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role)
        refresh_jti = AuthService._extract_refresh_jti(refresh_token)
        UserRefreshTokenRepository(db).upsert_current_jti(user.id, refresh_jti)
        return AuthResponse(
            user=AuthUser(id=user.id, email=user.email, role=user.role),
            tokens=AuthTokens(access_token=access_token, refresh_token=refresh_token),
        )

    @staticmethod
    def login(db: Session, email: str, password: str) -> AuthResponse:
        normalized_email = _normalize_email(email)
        repo = UserRepository(db)
        user = repo.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthServiceError(
                code="invalid_credentials",
                message="credentials are invalid",
                details={},
            )

        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role)
        refresh_jti = AuthService._extract_refresh_jti(refresh_token)
        UserRefreshTokenRepository(db).upsert_current_jti(user.id, refresh_jti)
        return AuthResponse(
            user=AuthUser(id=user.id, email=user.email, role=user.role),
            tokens=AuthTokens(access_token=access_token, refresh_token=refresh_token),
        )

    @staticmethod
    def refresh(db: Session, refresh_token: str) -> AuthTokens:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except SecurityError as error:
            raise AuthServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error

        subject = payload.get("sub")
        role = payload.get("role")
        if not isinstance(subject, str) or not subject.isdigit():
            raise AuthServiceError(code="invalid_token", message="token is invalid", details={})
        if not isinstance(role, str) or not is_valid_role(role):
            raise AuthServiceError(code="invalid_token", message="token is invalid", details={})
        jti = payload.get("jti")
        if not isinstance(jti, str) or not jti.strip():
            raise AuthServiceError(code="invalid_token", message="token is invalid", details={})

        user = UserRepository(db).get_by_id(int(subject))
        if user is None:
            raise AuthServiceError(
                code="invalid_token",
                message="token subject is invalid",
                details={},
            )
        refresh_state = UserRefreshTokenRepository(db).get_by_user_id(user.id)
        if refresh_state is None or refresh_state.current_jti != jti:
            raise AuthServiceError(
                code="invalid_token",
                message="token is invalid",
                details={},
            )

        new_refresh_token = create_refresh_token(subject=str(user.id), role=user.role)
        new_refresh_jti = AuthService._extract_refresh_jti(new_refresh_token)
        UserRefreshTokenRepository(db).upsert_current_jti(user.id, new_refresh_jti)
        return AuthTokens(
            access_token=create_access_token(subject=str(user.id), role=user.role),
            refresh_token=new_refresh_token,
        )
