# Historique de revue d'audit du sous-domaine entitlement mutation.
"""Définit l'event log append-only des transitions de revue d'audit."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.shared.base_mixins import (
    OccurredAtMixin,
    RequestIdMixin,
    ReviewedByUserMixin,
)


class CanonicalEntitlementMutationAuditReviewEventModel(
    Base, OccurredAtMixin, RequestIdMixin, ReviewedByUserMixin
):
    """Trace chaque transition de revue avec son type et ses valeurs avant/après."""

    __tablename__ = "canonical_entitlement_mutation_audit_review_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_audits.id"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False, default="updated")
    previous_review_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    new_review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    previous_review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_incident_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    new_incident_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
