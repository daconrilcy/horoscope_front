from __future__ import annotations

import csv
import io
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.admin_audit import (
    AdminAuditExportRequest,
    AdminAuditLogItem,
    AdminAuditLogResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/audit", tags=["admin-audit"])


def _mask_email(email: str | None) -> str | None:
    if not email:
        return None
    parts = email.split("@")
    if len(parts) != 2:
        return email[:3] + "***"
    name, domain = parts
    return f"{name[:3]}***@{domain}"


def _mask_target_id(target_id: str | None, target_type: str | None) -> str | None:
    if not target_id:
        return None
    if target_type == "user" and target_id.isdigit():
        if len(target_id) <= 4:
            return target_id
        return f"{target_id[:2]}...{target_id[-2:]}"
    return target_id


def _get_audit_query(
    db: Session,
    actor: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    period: str | None = None,
):
    stmt = (
        select(
            AuditEventModel.id,
            AuditEventModel.created_at.label("timestamp"),
            UserModel.email.label("actor_email"),
            AuditEventModel.actor_role,
            AuditEventModel.action,
            AuditEventModel.target_type,
            AuditEventModel.target_id,
            AuditEventModel.status,
            AuditEventModel.details,
        )
        .outerjoin(UserModel, UserModel.id == AuditEventModel.actor_user_id)
        .order_by(AuditEventModel.created_at.desc())
    )

    if actor:
        stmt = stmt.where(or_(UserModel.email.ilike(f"%{actor}%"), AuditEventModel.actor_role.ilike(f"%{actor}%")))
    if action:
        stmt = stmt.where(AuditEventModel.action == action)
    if target_type:
        stmt = stmt.where(AuditEventModel.target_type == target_type)
    if period:
        days = 7 if period == "7d" else 30
        start_date = datetime.now(UTC) - timedelta(days=days)
        stmt = stmt.where(AuditEventModel.created_at >= start_date)

    return stmt


@router.get("", response_model=AdminAuditLogResponse)
def get_audit_log(
    request: Request,
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    period: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, le=100),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get global audit logs with filters and pagination.
    """
    stmt = _get_audit_query(db, actor, action, target_type, period)
    
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    
    results = db.execute(
        stmt.offset((page - 1) * per_page).limit(per_page)
    ).all()

    data = []
    for r in results:
        data.append({
            "id": r.id,
            "timestamp": r.timestamp,
            "actor_email_masked": _mask_email(r.actor_email),
            "actor_role": r.actor_role,
            "action": r.action,
            "target_type": r.target_type,
            "target_id_masked": _mask_target_id(r.target_id, r.target_type),
            "status": r.status,
            "details": r.details or {},
        })

    return {
        "data": data,
        "total": total or 0,
        "page": page,
        "per_page": per_page
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
    stmt = _get_audit_query(db, payload.actor, payload.action, payload.target_type, payload.period)
    
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
                "record_count": len(results)
            },
        ),
    )
    db.commit()

    # 2. Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    header = [
        "ID", "Timestamp", "Actor Email (Masked)", "Actor Role", "Action", 
        "Target Type", "Target ID (Masked)", "Status", "Details (JSON)"
    ]
    writer.writerow(header)
    
    for r in results:
        writer.writerow([
            r.id,
            r.timestamp.isoformat(),
            _mask_email(r.actor_email),
            r.actor_role,
            r.action,
            r.target_type,
            _mask_target_id(r.target_id, r.target_type),
            r.status,
            str(r.details or {})
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_log.csv"}
    )
