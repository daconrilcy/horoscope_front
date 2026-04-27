from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.errors import build_error_response
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.auth import (
    AuthApiResponse,
    AuthMeApiResponse,
    LoginRequest,
    RefreshApiResponse,
    RefreshRequest,
    RegisterRequest,
)
from app.services.auth.public_support import (
    AuditWriteError,
    _audit_unavailable_response,
    _record_audit_event,
    _resolve_refresh_actor,
)
from app.services.auth_service import AuthService, AuthServiceError
from app.services.email.service import EmailService

router = APIRouter(prefix="/v1/auth", tags=["auth"])
logger = logging.getLogger(__name__)


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
    request: Request,
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
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

        # AC1: Trigger welcome email J0 (non-blocking)
        background_tasks.add_task(
            EmailService.send_welcome_email,
            db=db,
            user_id=auth_response.user.id,
            email=auth_response.user.email,
        )

        if settings.email_onboarding_sequence_enabled:
            background_tasks.add_task(
                EmailService.schedule_onboarding_sequence,
                db=db,
                user_id=auth_response.user.id,
                email=auth_response.user.email,
            )

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
        return build_error_response(
            status_code=409,
            request_id=request_id,
            code="email_already_registered",
            message="email is already registered",
            details={"field": "email"},
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
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
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
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
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
        return build_error_response(
            status_code=401,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id)
