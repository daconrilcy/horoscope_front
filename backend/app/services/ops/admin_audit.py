"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Literal

from sqlalchemy import or_, select

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.user import UserModel

logger = logging.getLogger(__name__)
AuditPeriod = Literal["7d", "30d", "all"]


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
        if len(target_id) <= 2:
            return "*" * len(target_id)
        if len(target_id) <= 4:
            return f"{'*' * (len(target_id) - 1)}{target_id[-1]}"
        return f"{target_id[:2]}...{target_id[-2:]}"
    return target_id


def _get_audit_query(
    actor: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    period: AuditPeriod | None = None,
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
        stmt = stmt.where(
            or_(
                UserModel.email.ilike(f"%{actor}%"),
                AuditEventModel.actor_role.ilike(f"%{actor}%"),
            )
        )
    if action:
        stmt = stmt.where(AuditEventModel.action == action)
    if target_type:
        stmt = stmt.where(AuditEventModel.target_type == target_type)
    if period in {"7d", "30d"}:
        days = 7 if period == "7d" else 30
        start_date = datetime_provider.utcnow() - timedelta(days=days)
        stmt = stmt.where(AuditEventModel.created_at >= start_date)

    return stmt


def _build_export_filename(period: AuditPeriod | None) -> str:
    timestamp = datetime_provider.utcnow().strftime("%Y%m%dT%H%M%SZ")
    suffix = period if period in {"7d", "30d"} else "all"
    return f"audit_log_{suffix}_{timestamp}.csv"
