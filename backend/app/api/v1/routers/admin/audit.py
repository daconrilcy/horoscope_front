from __future__ import annotations

import csv
import io
import json
import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.router_logic.admin.audit import (
    _build_export_filename,
    _get_audit_query,
    _mask_email,
    _mask_target_id,
)
from app.api.v1.schemas.routers.admin.audit import (
    AdminAuditExportRequest,
    AdminAuditLogResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/audit", tags=["admin-audit"])
AuditPeriod = Literal["7d", "30d", "all"]


@router.get("", response_model=AdminAuditLogResponse)
def get_audit_log(
    request: Request,
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    period: AuditPeriod | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, le=100),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get global audit logs with filters and pagination.
    """
    stmt = _get_audit_query(actor, action, target_type, period)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    results = db.execute(stmt.offset((page - 1) * per_page).limit(per_page)).all()

    data = []
    for r in results:
        data.append(
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "actor_email_masked": _mask_email(r.actor_email),
                "actor_role": r.actor_role,
                "action": r.action,
                "target_type": r.target_type,
                "target_id_masked": _mask_target_id(r.target_id, r.target_type),
                "status": r.status,
                "details": r.details or {},
            }
        )

    return {
        "data": data,
        "total": total or 0,
        "page": page,
        "per_page": per_page,
    }


@router.post("/export")
def export_audit_log(
    request: Request,
    payload: AdminAuditExportRequest,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Export filtered audit logs to CSV.
    """
    stmt = _get_audit_query(payload.actor, payload.action, payload.target_type, payload.period)

    # Limit to 5000 for MVP
    results = db.execute(stmt.limit(5000)).all()

    # 1. Audit the export action itself
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="audit_log_exported",
            target_type="system",
            target_id=None,
            status="success",
            details={
                "filters": payload.model_dump(),
                "record_count": len(results),
            },
        ),
    )
    db.commit()

    # 2. Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)

    header = [
        "ID",
        "Timestamp",
        "Actor Email (Masked)",
        "Actor Role",
        "Action",
        "Target Type",
        "Target ID (Masked)",
        "Status",
        "Details (JSON)",
    ]
    writer.writerow(header)

    for r in results:
        writer.writerow(
            [
                r.id,
                r.timestamp.isoformat(),
                _mask_email(r.actor_email),
                r.actor_role,
                r.action,
                r.target_type,
                _mask_target_id(r.target_id, r.target_type),
                r.status,
                json.dumps(r.details or {}, ensure_ascii=False, sort_keys=True),
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={_build_export_filename(payload.period)}"
        },
    )
