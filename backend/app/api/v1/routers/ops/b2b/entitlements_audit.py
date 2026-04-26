"""Routeur ops B2B d'audit des droits d'entreprise."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.constants import VALID_RESOLUTION_SOURCES
from app.api.v1.schemas.common import ErrorEnvelope
from app.api.v1.schemas.routers.ops.b2b.entitlements_audit import (
    B2BAuditEntryPayload,
    B2BAuditListApiResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.audit_service import B2BAuditService
from app.services.b2b.ops_entitlements_audit_api import (
    _enforce_limits,
    _ensure_ops_role,
    _error_response,
)

router = APIRouter(prefix="/v1/ops/b2b/entitlements", tags=["ops-b2b-entitlements"])


@router.get(
    "/audit",
    response_model=B2BAuditListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_b2b_entitlements_audit(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    resolution_source: str | None = Query(default=None),
    blocker_only: bool = Query(default=False),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="entitlements_audit"
    )
    if limit_error is not None:
        return limit_error

    if resolution_source is not None and resolution_source not in VALID_RESOLUTION_SOURCES:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_resolution_source",
            message="Invalid resolution_source filter value",
            details={"allowed": sorted(VALID_RESOLUTION_SOURCES), "received": resolution_source},
        )

    items, total_count = B2BAuditService.list_b2b_entitlement_audit(
        db,
        page=page,
        page_size=page_size,
        resolution_source_filter=resolution_source,
        blocker_only=blocker_only,
    )

    return {
        "data": {
            "items": [B2BAuditEntryPayload(**vars(item)).model_dump(mode="json") for item in items],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        },
        "meta": {"request_id": request_id},
    }
