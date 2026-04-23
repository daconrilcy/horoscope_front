from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def _utc_now() -> datetime:

    return datetime_provider.utcnow()


class CanonicalEntitlementMutationAlertEventModel(Base):
    __tablename__ = "canonical_entitlement_mutation_alert_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_audits.id"),
        nullable=False,
        index=True,
    )
    dedupe_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    alert_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_level_snapshot: Mapped[str] = mapped_column(String(16), nullable=False)
    effective_review_status_snapshot: Mapped[str | None] = mapped_column(String(32), nullable=True)
    feature_code_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    plan_id_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    plan_code_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_type_snapshot: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_identifier_snapshot: Mapped[str] = mapped_column(String(128), nullable=False)
    sla_target_seconds_snapshot: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due_at_snapshot: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    age_seconds_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    delivery_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(32), nullable=False)
    delivery_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, index=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
