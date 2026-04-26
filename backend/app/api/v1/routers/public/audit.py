from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.router_logic.public.audit import (
    _enforce_audit_limits,
    _ensure_allowed_role,
    _error_response,
)
from app.api.v1.schemas.routers.public.audit import (
    AuditEventsApiResponse,
    ErrorEnvelope,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import (
    AuditEventListFilters,
    AuditService,
    AuditServiceError,
)

router = APIRouter(prefix="/v1/audit", tags=["audit"])


@router.get(
    "/events",
    response_model=AuditEventsApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def list_audit_events(
    request: Request,
    action: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    target_user_id: int | None = Query(default=None),
    limit: int = Query(default=50),
    offset: int = Query(default=0),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_allowed_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_audit_limits(
        role=current_user.role,
        user_id=current_user.id,
        operation="list_events",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        filters = AuditEventListFilters(
            action=action,
            status=status,
            target_user_id=target_user_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        result = AuditService.list_events(db, filters=filters)
        return {"data": result.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except AuditServiceError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
