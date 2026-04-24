# État courant d'une alerte entitlement mutation.
"""Définit l'entité centrale d'alerte avec son cycle de vie métier et technique."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, synonym

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.shared.base_mixins import (
    CreatedAtMixin,
    RequestIdMixin,
    UpdatedAtMixin,
)


class CanonicalEntitlementMutationAlertEventModel(
    Base, CreatedAtMixin, UpdatedAtMixin, RequestIdMixin
):
    """Porte le current state d'une alerte et ses snapshots d'émission."""

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
    alert_status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
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
    last_delivery_status: Mapped[str] = mapped_column("delivery_status", String(32), nullable=False)
    last_delivery_error: Mapped[str | None] = mapped_column("delivery_error", Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    first_delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_delivered_at: Mapped[datetime | None] = mapped_column(
        "delivered_at", DateTime(timezone=True), nullable=True
    )
    delivery_attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_suppressed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    suppressed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suppression_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    review_status_snapshot = synonym("effective_review_status_snapshot")
    delivery_status = synonym("last_delivery_status")
    delivery_error = synonym("last_delivery_error")
    delivered_at = synonym("last_delivered_at")
