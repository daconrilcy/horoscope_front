from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from pydantic import ValidationError
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.infra.db.models.privacy import UserPrivacyRequestModel
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.support import (
    PrivacyRequestSummary,
    SupportContextApiResponse,
    SupportContextData,
    SupportContextUserData,
    SupportIncidentApiResponse,
    SupportIncidentListApiResponse,
)
from app.services.billing.service import BillingService
from app.services.ops.incident_service import (
    IncidentService,
    IncidentServiceError,
    SupportIncidentCreatePayload,
    SupportIncidentData,
    SupportIncidentListFilters,
    SupportIncidentUpdatePayload,
)
from app.services.ops.public_support import (
    _enforce_support_limits,
    _ensure_support_role,
    _raise_error,
    _recent_audit_events_for_user,
    _record_audit_event,
)

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/v1/support", tags=["support"])


@router.get(
    "/users/context",
    response_model=SupportContextApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_support_context_by_query(
    request: Request,
    user_id: int | None = Query(default=None),
    email: str | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_support_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_support_limits(
        role=current_user.role,
        user_id=current_user.id,
        operation="get_user_context",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error

    user = None
    if user_id is not None:
        user = db.get(UserModel, user_id)
    elif email is not None:
        user = db.scalars(select(UserModel).where(UserModel.email == email)).first()

    if user is None:
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code="support_context_not_found",
            message="user support context was not found",
            details={"user_id": str(user_id), "email": email or ""},
        )

    subscription = BillingService.get_subscription_status_readonly(db, user_id=user.id)
    privacy_requests_models = db.scalars(
        select(UserPrivacyRequestModel)
        .where(UserPrivacyRequestModel.user_id == user.id)
        .order_by(desc(UserPrivacyRequestModel.requested_at), desc(UserPrivacyRequestModel.id))
        .limit(20)
    ).all()
    incidents = IncidentService.list_incidents_for_user(db, user_id=user.id, limit=20)
    incident_ids = [item.incident_id for item in incidents]
    audit_events = _recent_audit_events_for_user(db, user_id=user.id, incident_ids=incident_ids)

    data = SupportContextData(
        user=SupportContextUserData(
            user_id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        ),
        subscription=subscription,
        privacy_requests=[
            PrivacyRequestSummary(
                request_id=model.id,
                request_kind=model.request_kind,
                status=model.status,
                requested_at=model.requested_at,
                completed_at=model.completed_at,
                error_reason=model.error_reason,
            )
            for model in privacy_requests_models
        ],
        incidents=incidents,
        audit_events=audit_events,
    )
    return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.get(
    "/users/{user_id}/context",
    response_model=SupportContextApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_user_support_context(
    user_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_support_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_support_limits(
        role=current_user.role,
        user_id=current_user.id,
        operation="get_user_context",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error

    user = db.get(UserModel, user_id)
    if user is None:
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code="support_context_not_found",
            message="user support context was not found",
            details={"user_id": str(user_id)},
        )

    subscription = BillingService.get_subscription_status_readonly(db, user_id=user.id)
    privacy_requests_models = db.scalars(
        select(UserPrivacyRequestModel)
        .where(UserPrivacyRequestModel.user_id == user.id)
        .order_by(desc(UserPrivacyRequestModel.requested_at), desc(UserPrivacyRequestModel.id))
        .limit(20)
    ).all()
    incidents = IncidentService.list_incidents_for_user(db, user_id=user.id, limit=20)
    incident_ids = [item.incident_id for item in incidents]
    audit_events = _recent_audit_events_for_user(db, user_id=user.id, incident_ids=incident_ids)

    data = SupportContextData(
        user=SupportContextUserData(
            user_id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        ),
        subscription=subscription,
        privacy_requests=[
            PrivacyRequestSummary(
                request_id=model.id,
                request_kind=model.request_kind,
                status=model.status,
                requested_at=model.requested_at,
                completed_at=model.completed_at,
                error_reason=model.error_reason,
            )
            for model in privacy_requests_models
        ],
        incidents=incidents,
        audit_events=audit_events,
    )
    return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.get(
    "/incidents",
    response_model=SupportIncidentListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def list_support_incidents(
    request: Request,
    user_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    limit: int = Query(default=50),
    offset: int = Query(default=0),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_support_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_support_limits(
        role=current_user.role,
        user_id=current_user.id,
        operation="list_incidents",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        filters = SupportIncidentListFilters(
            user_id=user_id,
            status=status,
            priority=priority,
            limit=limit,
            offset=offset,
        )
        result = IncidentService.list_incidents(db, filters=filters)
        return {"data": result.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except IncidentServiceError as error:
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/incidents/{incident_id}",
    response_model=SupportIncidentApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_support_incident(
    incident_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_support_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_support_limits(
        role=current_user.role,
        user_id=current_user.id,
        operation="get_incident",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    incident = db.get(SupportIncidentModel, incident_id)
    if incident is None:
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code="incident_not_found",
            message="incident was not found",
            details={"incident_id": str(incident_id)},
        )
    data = SupportIncidentData(
        incident_id=incident.id,
        user_id=incident.user_id,
        created_by_user_id=incident.created_by_user_id,
        assigned_to_user_id=incident.assigned_to_user_id,
        category=incident.category,
        title=incident.title,
        description=incident.description,
        support_response=incident.support_response,
        status=incident.status,
        priority=incident.priority,
        resolved_at=incident.resolved_at,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
    )
    return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.post(
    "/incidents",
    response_model=SupportIncidentApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def create_support_incident(
    payload: dict[str, Any],
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_support_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_support_limits(
        role=current_user.role,
        user_id=current_user.id,
        operation="create_incident",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error

    try:
        parsed = SupportIncidentCreatePayload.model_validate(payload)
        incident = IncidentService.create_incident(
            db,
            payload=parsed,
            actor_user_id=current_user.id,
            request_id=request_id,
        )
        db.commit()
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="support_incident_create",
            target_type="incident",
            target_id=str(incident.incident_id),
            status="success",
            details={"user_id": incident.user_id, "status": incident.status},
        )
        return {"data": incident.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code="incident_validation_error",
            message="incident payload validation failed",
            details={"errors": error.errors()},
        )
    except IncidentServiceError as error:
        db.rollback()
        status_code = (
            404 if error.code in {"incident_not_found", "incident_user_not_found"} else 422
        )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="support_incident_create",
            target_type="incident",
            target_id=None,
            status="failed",
            details={"error_code": error.code},
        )
        return _raise_error(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.patch(
    "/incidents/{incident_id}",
    response_model=SupportIncidentApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def update_support_incident(
    incident_id: int,
    payload: dict[str, Any],
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_support_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_support_limits(
        role=current_user.role,
        user_id=current_user.id,
        operation="update_incident",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        parsed = SupportIncidentUpdatePayload.model_validate(payload)
        incident = IncidentService.update_incident(
            db,
            incident_id=incident_id,
            payload=parsed,
            request_id=request_id,
        )
        db.commit()
        audit_action = (
            "support_incident_close"
            if incident.status in {"resolved", "closed"}
            else "support_incident_update"
        )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action=audit_action,
            target_type="incident",
            target_id=str(incident.incident_id),
            status="success",
            details={"status": incident.status, "priority": incident.priority},
        )
        return {"data": incident.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code="incident_validation_error",
            message="incident payload validation failed",
            details={"errors": error.errors()},
        )
    except IncidentServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "incident_not_found" else 422
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="support_incident_update",
            target_type="incident",
            target_id=str(incident_id),
            status="failed",
            details={"error_code": error.code},
        )
        return _raise_error(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
