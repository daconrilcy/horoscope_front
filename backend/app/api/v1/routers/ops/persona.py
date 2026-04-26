from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_ops_user,
)
from app.api.v1.router_logic.ops.persona import (
    _audit_failure_or_503,
    _enforce_limits,
    _error_response,
    _persona_profile_mutation,
    _record_audit_event,
)
from app.api.v1.schemas.routers.ops.persona import (
    ErrorEnvelope,
    PersonaConfigApiResponse,
    PersonaProfileListApiResponse,
    PersonaRollbackApiResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.llm_generation.guidance.persona_config_service import (
    PersonaConfigService,
    PersonaConfigServiceError,
    PersonaConfigUpdatePayload,
    PersonaProfileCreatePayload,
)
from app.services.ops.audit_service import AuditServiceError

router = APIRouter(prefix="/v1/ops/persona", tags=["ops-persona"])


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
    current_user: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
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
