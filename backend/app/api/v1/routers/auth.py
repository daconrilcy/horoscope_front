from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rbac import is_valid_role
from app.core.request_id import resolve_request_id
from app.core.security import SecurityError, decode_token
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService
from app.services.auth_service import AuthResponse, AuthService, AuthServiceError, AuthTokens


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthApiResponse(BaseModel):
    data: AuthResponse
    meta: ResponseMeta


class RefreshApiResponse(BaseModel):
    data: AuthTokens
    meta: ResponseMeta


class AuthMeData(BaseModel):
    id: int
    role: str
    email: str
    created_at: str


class AuthMeApiResponse(BaseModel):
    data: AuthMeData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/auth", tags=["auth"])
logger = logging.getLogger(__name__)


class AuditWriteError(Exception):
    pass


def _audit_unavailable_response(request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "audit_unavailable",
                "message": "audit persistence is unavailable",
                "details": {},
                "request_id": request_id,
            }
        },
    )


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int | None,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str | None,
    status: str,
    details: dict[str, object] | None = None,
) -> None:
    try:
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                action=action,
                target_type=target_type,
                target_id=target_id,
                status=status,
                details=details or {},
            ),
        )
    except Exception as error:
        logger.exception("audit_event_write_failed action=%s request_id=%s", action, request_id)
        raise AuditWriteError("audit event write failed") from error


def _resolve_refresh_actor(refresh_token: str) -> tuple[int | None, str]:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except SecurityError:
        return None, "anonymous"
    subject = payload.get("sub")
    role = payload.get("role")
    actor_user_id = int(subject) if isinstance(subject, str) and subject.isdigit() else None
    actor_role = role if isinstance(role, str) and is_valid_role(role) else "anonymous"
    return actor_user_id, actor_role


@router.get(
    "/me",
    response_model=AuthMeApiResponse,
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
def me(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    request_id = resolve_request_id(request)
    return {
        "data": {
            "id": current_user.id,
            "role": current_user.role,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat(),
        },
        "meta": {"request_id": request_id},
    }


@router.post(
    "/register",
    response_model=AuthApiResponse,
    responses={
        400: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def register(
    request: Request, payload: RegisterRequest, db: Session = Depends(get_db_session)
) -> Any:
    request_id = resolve_request_id(request)
    try:
        auth_response = AuthService.register(db, email=payload.email, password=payload.password)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=auth_response.user.id,
            actor_role=auth_response.user.role,
            action="auth_register",
            target_type="user",
            target_id=str(auth_response.user.id),
            status="success",
        )
        db.commit()
        return {"data": auth_response.model_dump(), "meta": {"request_id": request_id}}
    except IntegrityError:
        db.rollback()
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=None,
            actor_role="anonymous",
            action="auth_register",
            target_type="user",
            target_id=None,
            status="failed",
            details={"error_code": "email_already_registered"},
        )
        db.commit()
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "email_already_registered",
                    "message": "email is already registered",
                    "details": {"field": "email"},
                    "request_id": request_id,
                }
            },
        )
    except AuthServiceError as error:
        db.rollback()
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=None,
            actor_role="anonymous",
            action="auth_register",
            target_type="user",
            target_id=None,
            status="failed",
            details={"error_code": error.code},
        )
        db.commit()
        status_code = 409 if error.code == "email_already_registered" else 400
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id)


@router.post(
    "/login",
    response_model=AuthApiResponse,
    responses={401: {"model": ErrorEnvelope}, 503: {"model": ErrorEnvelope}},
)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db_session)) -> Any:
    request_id = resolve_request_id(request)
    try:
        auth_response = AuthService.login(db, email=payload.email, password=payload.password)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=auth_response.user.id,
            actor_role=auth_response.user.role,
            action="auth_login",
            target_type="user",
            target_id=str(auth_response.user.id),
            status="success",
        )
        db.commit()
        return {"data": auth_response.model_dump(), "meta": {"request_id": request_id}}
    except AuthServiceError as error:
        db.rollback()
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=None,
            actor_role="anonymous",
            action="auth_login",
            target_type="user",
            target_id=None,
            status="failed",
            details={"error_code": error.code},
        )
        db.commit()
        status_code = 401 if error.code == "invalid_credentials" else 400
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id)


@router.post(
    "/refresh",
    response_model=RefreshApiResponse,
    responses={401: {"model": ErrorEnvelope}, 503: {"model": ErrorEnvelope}},
)
def refresh(
    request: Request, payload: RefreshRequest, db: Session = Depends(get_db_session)
) -> Any:
    request_id = resolve_request_id(request)
    actor_user_id, actor_role = _resolve_refresh_actor(payload.refresh_token)
    try:
        tokens = AuthService.refresh(db, payload.refresh_token)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action="auth_refresh",
            target_type="user",
            target_id=str(actor_user_id) if actor_user_id is not None else None,
            status="success",
        )
        db.commit()
        return {"data": tokens.model_dump(), "meta": {"request_id": request_id}}
    except AuthServiceError as error:
        db.rollback()
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action="auth_refresh",
            target_type="user",
            target_id=str(actor_user_id) if actor_user_id is not None else None,
            status="failed",
            details={"error_code": error.code},
        )
        db.commit()
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id)
