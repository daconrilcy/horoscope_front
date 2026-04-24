# Journal technique des tentatives de delivery d'alerte.
"""Définit l'historique append-only des tentatives de delivery d'une alerte."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, synonym

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.shared.base_mixins import (
    CreatedAtMixin,
    RequestIdMixin,
)


class CanonicalEntitlementMutationAlertDeliveryAttemptModel(Base, CreatedAtMixin, RequestIdMixin):
    """Trace chaque tentative technique de delivery d'une alerte."""

    __tablename__ = "canonical_entitlement_mutation_alert_delivery_attempts"
    __table_args__ = (
        UniqueConstraint("alert_event_id", "attempt_number", name="uq_alert_delivery_attempt"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_alert_events.id"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    delivery_provider: Mapped[str] = mapped_column("delivery_channel", String(32), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(32), nullable=False)
    delivery_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    response_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_retryable: Mapped[bool | None] = mapped_column(nullable=True)

    delivery_channel = synonym("delivery_provider")
