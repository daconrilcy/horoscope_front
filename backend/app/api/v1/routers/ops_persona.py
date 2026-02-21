from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.persona_config_service import (
    PersonaConfigData,
    PersonaConfigService,
    PersonaConfigServiceError,
    PersonaConfigUpdatePayload,
    PersonaProfileCreatePayload,
    PersonaProfileListData,
    PersonaRollbackData,
)


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class PersonaConfigApiResponse(BaseModel):
    data: PersonaConfigData
    meta: ResponseMeta


class PersonaRollbackApiResponse(BaseModel):
    data: PersonaRollbackData
    meta: ResponseMeta


class PersonaProfileListApiResponse(BaseModel):
    data: PersonaProfileListData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/ops/persona", tags=["ops-persona"])


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


def _ensure_ops_role(user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role != "ops":
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops", "actual_role": user.role},
        )
    return None


def _enforce_limits(
    *, user: AuthenticatedUser, request_id: str, operation: str
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"ops_persona:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(
            key=f"ops_persona:role:{user.role}:{operation}", limit=60, window_seconds=60
        )
        check_rate_limit(key=f"ops_persona:user:{user.id}:{operation}", limit=30, window_seconds=60)
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int,
    actor_role: str,
    action: str,
    target_id: str | None,
    status: str,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action=action,
            target_type="persona_config",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )


def _audit_failure_or_503(
    db: Session,
    *,
    request_id: str,
    actor: AuthenticatedUser,
    action: str,
    error_code: str,
) -> JSONResponse | None:
    try:
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=actor.id,
            actor_role=actor.role,
            action=action,
            target_id=None,
            status="failed",
            details={"error_code": error_code},
        )
        db.commit()
    except Exception:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )
    return None


@router.get(
    "/config",
    response_model=PersonaConfigApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_active_persona_config(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="get_config")
    if limit_error is not None:
        return limit_error
    response = PersonaConfigService.get_active(db)
    return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.get(
    "/profiles",
    response_model=PersonaProfileListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def list_persona_profiles(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="list_profiles"
    )
    if limit_error is not None:
        return limit_error
    response = PersonaConfigService.list_profiles(db)
    return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.post(
    "/profiles",
    response_model=PersonaConfigApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def create_persona_profile(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="create_profile"
    )
    if limit_error is not None:
        return limit_error
    try:
        parsed = PersonaProfileCreatePayload.model_validate(payload)
        response = PersonaConfigService.create_profile(
            db,
            user_id=current_user.id,
            payload=parsed,
        )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="ops_persona_create",
            target_id=str(response.id) if response.id is not None else None,
            status="success",
            details={"version": response.version, "profile_code": response.profile_code},
        )
        db.commit()
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_persona_profile_request",
            message="persona profile request validation failed",
            details={"errors": error.errors()},
        )
    except PersonaConfigServiceError as error:
        db.rollback()
        audit_error = _audit_failure_or_503(
            db,
            request_id=request_id,
            actor=current_user,
            action="ops_persona_create",
            error_code=error.code,
        )
        if audit_error is not None:
            return audit_error
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditServiceError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )


@router.put(
    "/config",
    response_model=PersonaConfigApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def update_active_persona_config(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="update_config"
    )
    if limit_error is not None:
        return limit_error
    try:
        parsed = PersonaConfigUpdatePayload.model_validate(payload)
        response = PersonaConfigService.update_active(
            db,
            user_id=current_user.id,
            payload=parsed,
        )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="ops_persona_update",
            target_id=str(response.id) if response.id is not None else None,
            status="success",
            details={"version": response.version, "profile_code": response.profile_code},
        )
        db.commit()
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_persona_config_request",
            message="persona config request validation failed",
            details={"errors": error.errors()},
        )
    except PersonaConfigServiceError as error:
        db.rollback()
        audit_error = _audit_failure_or_503(
            db,
            request_id=request_id,
            actor=current_user,
            action="ops_persona_update",
            error_code=error.code,
        )
        if audit_error is not None:
            return audit_error
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditServiceError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )


def _persona_profile_mutation(
    *,
    request: Request,
    profile_id: int,
    operation: str,
    action: str,
    service_call: Callable[..., PersonaConfigData],
    current_user: AuthenticatedUser,
    db: Session,
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation=operation)
    if limit_error is not None:
        return limit_error
    try:
        response = service_call(db=db, user_id=current_user.id, profile_id=profile_id)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action=action,
            target_id=str(response.id) if response.id is not None else None,
            status="success",
            details={"version": response.version, "profile_code": response.profile_code},
        )
        db.commit()
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except PersonaConfigServiceError as error:
        db.rollback()
        audit_error = _audit_failure_or_503(
            db,
            request_id=request_id,
            actor=current_user,
            action=action,
            error_code=error.code,
        )
        if audit_error is not None:
            return audit_error
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditServiceError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )


@router.post(
    "/profiles/{profile_id}/activate",
    response_model=PersonaConfigApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def activate_persona_profile(
    profile_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    return _persona_profile_mutation(
        request=request,
        profile_id=profile_id,
        operation="activate_profile",
        action="ops_persona_activate",
        service_call=PersonaConfigService.activate_profile,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/profiles/{profile_id}/archive",
    response_model=PersonaConfigApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def archive_persona_profile(
    profile_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    return _persona_profile_mutation(
        request=request,
        profile_id=profile_id,
        operation="archive_profile",
        action="ops_persona_archive",
        service_call=PersonaConfigService.archive_profile,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/profiles/{profile_id}/restore",
    response_model=PersonaConfigApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def restore_persona_profile(
    profile_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    return _persona_profile_mutation(
        request=request,
        profile_id=profile_id,
        operation="restore_profile",
        action="ops_persona_restore",
        service_call=PersonaConfigService.restore_profile,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/rollback",
    response_model=PersonaRollbackApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def rollback_persona_config(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="rollback")
    if limit_error is not None:
        return limit_error
    try:
        response = PersonaConfigService.rollback_active(
            db,
            user_id=current_user.id,
        )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="ops_persona_rollback",
            target_id=str(response.active.id) if response.active.id is not None else None,
            status="success",
            details={
                "rolled_back_version": response.rolled_back_version,
                "profile_code": response.active.profile_code,
            },
        )
        db.commit()
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except PersonaConfigServiceError as error:
        db.rollback()
        audit_error = _audit_failure_or_503(
            db,
            request_id=request_id,
            actor=current_user,
            action="ops_persona_rollback",
            error_code=error.code,
        )
        if audit_error is not None:
            return audit_error
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditServiceError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )
