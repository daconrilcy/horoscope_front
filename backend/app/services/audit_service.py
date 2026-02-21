from __future__ import annotations

import logging
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.db.models.audit_event import AuditEventModel
from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)


class AuditServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuditEventData(BaseModel):
    event_id: int
    request_id: str
    actor_user_id: int | None
    actor_role: str
    action: str
    target_type: str
    target_id: str | None
    status: str
    details: dict[str, object]
    created_at: datetime


class AuditEventListData(BaseModel):
    events: list[AuditEventData]
    total: int
    limit: int
    offset: int


class AuditEventCreatePayload(BaseModel):
    request_id: str
    actor_user_id: int | None
    actor_role: str
    action: str
    target_type: str
    target_id: str | None = None
    status: str
    details: dict[str, object] = Field(default_factory=dict)


class AuditEventListFilters(BaseModel):
    action: str | None = None
    status: str | None = None
    target_user_id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 50
    offset: int = 0


class AuditService:
    @staticmethod
    def _to_data(model: AuditEventModel) -> AuditEventData:
        return AuditEventData(
            event_id=model.id,
            request_id=model.request_id,
            actor_user_id=model.actor_user_id,
            actor_role=model.actor_role,
            action=model.action,
            target_type=model.target_type,
            target_id=model.target_id,
            status=model.status,
            details=model.details,
            created_at=model.created_at,
        )

    @staticmethod
    def record_event(db: Session, *, payload: AuditEventCreatePayload) -> AuditEventData:
        if not payload.request_id.strip():
            raise AuditServiceError(
                code="audit_validation_error",
                message="request_id is required",
                details={"field": "request_id"},
            )
        if payload.status not in {"success", "failed"}:
            raise AuditServiceError(
                code="audit_validation_error",
                message="status is invalid",
                details={"field": "status"},
            )
        event = AuditEventModel(
            request_id=payload.request_id,
            actor_user_id=payload.actor_user_id,
            actor_role=payload.actor_role,
            action=payload.action,
            target_type=payload.target_type,
            target_id=payload.target_id,
            status=payload.status,
            details=payload.details,
        )
        db.add(event)
        db.flush()
        increment_counter("audit_events_total", 1.0)
        if payload.status == "failed":
            increment_counter("audit_events_failures_total", 1.0)
        logger.info(
            "audit_event_recorded request_id=%s action=%s status=%s "
            "actor_role=%s target_type=%s target_id=%s",
            payload.request_id,
            payload.action,
            payload.status,
            payload.actor_role,
            payload.target_type,
            payload.target_id or "",
        )
        return AuditService._to_data(event)

    @staticmethod
    def list_events(db: Session, *, filters: AuditEventListFilters) -> AuditEventListData:
        if filters.limit <= 0 or filters.limit > 100:
            raise AuditServiceError(
                code="audit_validation_error",
                message="audit pagination is invalid",
                details={"field": "limit"},
            )
        if filters.offset < 0:
            raise AuditServiceError(
                code="audit_validation_error",
                message="audit pagination is invalid",
                details={"field": "offset"},
            )

        query = select(AuditEventModel)
        count_query = select(func.count(AuditEventModel.id))

        if filters.action is not None:
            query = query.where(AuditEventModel.action == filters.action)
            count_query = count_query.where(AuditEventModel.action == filters.action)
        if filters.status is not None:
            query = query.where(AuditEventModel.status == filters.status)
            count_query = count_query.where(AuditEventModel.status == filters.status)
        if filters.target_user_id is not None:
            target_id = str(filters.target_user_id)
            query = query.where(
                AuditEventModel.target_type == "user",
                AuditEventModel.target_id == target_id,
            )
            count_query = count_query.where(
                AuditEventModel.target_type == "user",
                AuditEventModel.target_id == target_id,
            )
        if filters.date_from is not None:
            query = query.where(AuditEventModel.created_at >= filters.date_from)
            count_query = count_query.where(AuditEventModel.created_at >= filters.date_from)
        if filters.date_to is not None:
            query = query.where(AuditEventModel.created_at <= filters.date_to)
            count_query = count_query.where(AuditEventModel.created_at <= filters.date_to)

        query = (
            query.order_by(AuditEventModel.created_at.desc(), AuditEventModel.id.desc())
            .limit(filters.limit)
            .offset(filters.offset)
        )
        events = db.scalars(query).all()
        total = int(db.scalar(count_query) or 0)
        return AuditEventListData(
            events=[AuditService._to_data(event) for event in events],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )
