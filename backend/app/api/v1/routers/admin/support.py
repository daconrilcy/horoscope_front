from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.errors import raise_api_error
from app.core.datetime_provider import datetime_provider
from app.core.request_id import resolve_request_id
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.flagged_content import FlaggedContentModel
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.api_contracts.admin.support import (
    AdminFlaggedContentResponse,
    AdminSupportTicketDetailResponse,
    AdminSupportTicketResponse,
    FlaggedContentReviewUpdate,
    TicketStatusUpdate,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/support", tags=["admin-support"])


@router.get("/tickets", response_model=AdminSupportTicketResponse)
def list_tickets(
    request: Request,
    status: str = Query(default="open"),
    category: str = Query(default="all"),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    stmt = (
        select(
            SupportIncidentModel.id,
            SupportIncidentModel.user_id,
            UserModel.email.label("user_email"),
            SupportIncidentModel.category,
            SupportIncidentModel.title,
            SupportIncidentModel.status,
            SupportIncidentModel.priority,
            SupportIncidentModel.created_at,
        )
        .join(UserModel, UserModel.id == SupportIncidentModel.user_id)
        .order_by(SupportIncidentModel.created_at.desc())
    )

    if status != "all":
        stmt = stmt.where(SupportIncidentModel.status == status)
    if category != "all":
        stmt = stmt.where(SupportIncidentModel.category == category)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    results = db.execute(stmt.limit(50)).all()

    return {
        "data": results,
        "total": total or 0,
    }


@router.get("/tickets/{ticket_id}", response_model=AdminSupportTicketDetailResponse)
def get_ticket_detail(
    ticket_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    stmt = (
        select(
            SupportIncidentModel.id,
            SupportIncidentModel.user_id,
            UserModel.email.label("user_email"),
            SupportIncidentModel.category,
            SupportIncidentModel.title,
            SupportIncidentModel.description,
            SupportIncidentModel.support_response,
            SupportIncidentModel.status,
            SupportIncidentModel.priority,
            SupportIncidentModel.resolved_at,
            SupportIncidentModel.created_at,
            SupportIncidentModel.updated_at,
        )
        .join(UserModel, UserModel.id == SupportIncidentModel.user_id)
        .where(SupportIncidentModel.id == ticket_id)
    )
    result = db.execute(stmt).first()
    if not result:
        raise_api_error(status_code=404, message="Ticket not found")

    audit_events = db.scalars(
        select(AuditEventModel)
        .where(
            AuditEventModel.target_type == "support_ticket",
            AuditEventModel.target_id == str(ticket_id),
        )
        .order_by(AuditEventModel.created_at.desc())
        .limit(20)
    ).all()

    ticket = dict(result._mapping)
    ticket["audit_trail"] = [
        {
            "id": event.id,
            "action": event.action,
            "actor_role": event.actor_role,
            "status": event.status,
            "details": event.details or {},
            "created_at": event.created_at,
        }
        for event in audit_events
    ]

    return {"data": ticket}


@router.patch("/tickets/{ticket_id}")
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    ticket = db.get(SupportIncidentModel, ticket_id)
    if not ticket:
        raise_api_error(status_code=404, message="Ticket not found")

    before = ticket.status
    ticket.status = payload.status
    if payload.status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = datetime_provider.utcnow()

    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="support_ticket_action",
            target_type="support_ticket",
            target_id=str(ticket_id),
            status="success",
            details={"action_type": "status_changed", "before": before, "after": payload.status},
        ),
    )
    db.commit()
    return {"status": "success"}


@router.get("/flagged-content", response_model=AdminFlaggedContentResponse)
def list_flagged_content(
    request: Request,
    status: str = Query(default="pending"),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    stmt = (
        select(
            FlaggedContentModel.id,
            FlaggedContentModel.user_id,
            UserModel.email.label("user_email"),
            FlaggedContentModel.content_type,
            FlaggedContentModel.content_ref_id,
            FlaggedContentModel.excerpt,
            FlaggedContentModel.reason,
            FlaggedContentModel.reported_at,
            FlaggedContentModel.status,
        )
        .join(UserModel, UserModel.id == FlaggedContentModel.user_id)
        .order_by(FlaggedContentModel.reported_at.desc())
    )

    if status != "all":
        stmt = stmt.where(FlaggedContentModel.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    results = db.execute(stmt.limit(50)).all()

    return {
        "data": results,
        "total": total or 0,
    }


@router.patch("/flagged-content/{content_id}")
def review_flagged_content(
    content_id: int,
    payload: FlaggedContentReviewUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    content = db.get(FlaggedContentModel, content_id)
    if not content:
        raise_api_error(status_code=404, message="Content not found")

    content.status = payload.status
    content.reviewed_at = datetime_provider.utcnow()
    content.reviewed_by = current_user.id

    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="flagged_content_reviewed",
            target_type="flagged_content",
            target_id=str(content_id),
            status="success",
            details={"resolution": payload.status},
        ),
    )
    db.commit()
    return {"status": "success"}
