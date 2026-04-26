"""Audit applicatif des exports administrateur."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)


def _record_export_audit(
    db: Session,
    request_id: str,
    user: AuthenticatedUser,
    export_type: str,
    count: int,
    filters: dict,
):
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=user.id,
            actor_role=user.role,
            action="sensitive_data_exported",
            target_type="system",
            target_id=None,
            status="success",
            details={
                "export_type": export_type,
                "filters": filters,
                "record_count": count,
            },
        ),
    )
    db.commit()
