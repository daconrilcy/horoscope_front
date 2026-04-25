# Current state de handling d'alerte du sous-domaine entitlement mutation.
"""Définit l'état courant de traitement d'une alerte entitlement mutation."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, synonym

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.shared.base_mixins import (
    ActionUserMixin,
    CreatedAtMixin,
    OpsCommentMixin,
    RequestIdMixin,
    UpdatedAtMixin,
)
from app.infra.db.models.entitlement_mutation.shared.timestamps import now_utc


class CanonicalEntitlementMutationAlertHandlingModel(
    Base,
    CreatedAtMixin,
    UpdatedAtMixin,
    RequestIdMixin,
    OpsCommentMixin,
    ActionUserMixin,
):
    """Porte l'état courant durci de traitement d'une alerte."""

    __tablename__ = "canonical_entitlement_mutation_alert_event_handlings"
    __table_args__ = (UniqueConstraint("alert_event_id", name="uq_cemae_handling_alert_event_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_alert_events.id"),
        nullable=False,
        index=True,
    )
    handling_status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    handled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc
    )
    resolution_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    incident_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    requires_followup: Mapped[bool] = mapped_column(nullable=False, default=False)
    followup_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suppression_application_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_alert_suppression_applications.id"),
        nullable=True,
    )
    suppression_application_key: Mapped[str | None] = mapped_column(
        "suppression_key", String(64), nullable=True
    )
    handling_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    suppression_key = synonym("suppression_application_key")


__all__ = ["CanonicalEntitlementMutationAlertHandlingModel"]
