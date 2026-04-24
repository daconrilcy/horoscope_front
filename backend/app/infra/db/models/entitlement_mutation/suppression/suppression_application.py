# Trace relationnelle des suppressions effectivement appliquées.
"""Définit la table reliant une alerte à la règle de suppression effectivement appliquée."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.shared.base_mixins import RequestIdMixin
from app.infra.db.models.entitlement_mutation.shared.timestamps import now_utc


class CanonicalEntitlementMutationAlertSuppressionApplicationModel(Base, RequestIdMixin):
    """Porte une application effective de suppression, manuelle ou issue d'une règle."""

    __tablename__ = "canonical_entitlement_mutation_alert_suppression_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_alert_events.id"),
        nullable=False,
        index=True,
    )
    suppression_rule_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_alert_suppression_rules.id"),
        nullable=True,
        index=True,
    )
    suppression_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    application_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    application_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc, index=True
    )
