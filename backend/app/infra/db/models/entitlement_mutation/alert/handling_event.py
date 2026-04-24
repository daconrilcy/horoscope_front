# Historique de handling d'alerte du sous-domaine entitlement mutation.
"""Définit l'event log append-only du traitement d'une alerte."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, synonym

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.shared.base_mixins import (
    ActionUserMixin,
    OpsCommentMixin,
    RequestIdMixin,
)
from app.infra.db.models.entitlement_mutation.shared.timestamps import now_utc


class CanonicalEntitlementMutationAlertHandlingEventModel(
    Base, RequestIdMixin, OpsCommentMixin, ActionUserMixin
):
    """Trace chaque changement de handling avec un type d'événement explicite."""

    __tablename__ = "canonical_entitlement_mutation_alert_event_handling_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_alert_events.id"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False, default="updated")
    handling_status: Mapped[str] = mapped_column(String(32), nullable=False)
    handled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc, index=True
    )
    resolution_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    incident_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    requires_followup: Mapped[bool] = mapped_column(nullable=False, default=False)
    followup_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suppression_application_key: Mapped[str | None] = mapped_column(
        "suppression_key", String(64), nullable=True
    )

    suppression_key = synonym("suppression_application_key")


# Alias legacy conservé pour éviter les régressions durant la migration des imports.
CanonicalEntitlementMutationAlertEventHandlingEventModel = (
    CanonicalEntitlementMutationAlertHandlingEventModel
)

__all__ = [
    "CanonicalEntitlementMutationAlertEventHandlingEventModel",
    "CanonicalEntitlementMutationAlertHandlingEventModel",
]
