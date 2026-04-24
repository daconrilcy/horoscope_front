# Current state de revue d'audit du sous-domaine entitlement mutation.
"""Définit la table de revue courante d'un audit de mutation d'entitlements."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.shared.base_mixins import (
    CreatedAtMixin,
    RequestIdMixin,
    ReviewedByUserMixin,
    UpdatedAtMixin,
)
from app.infra.db.models.entitlement_mutation.shared.timestamps import now_utc


class CanonicalEntitlementMutationAuditReviewModel(
    Base, CreatedAtMixin, UpdatedAtMixin, RequestIdMixin, ReviewedByUserMixin
):
    """Porte l'état courant et versionné de la revue d'un audit."""

    __tablename__ = "canonical_entitlement_mutation_audit_reviews"
    __table_args__ = (UniqueConstraint("audit_id", name="uq_cemar_audit_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_audits.id"),
        nullable=False,
        index=True,
    )
    review_status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc
    )
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    incident_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    review_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
