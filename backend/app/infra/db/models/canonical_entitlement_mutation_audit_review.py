from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def _utc_now() -> datetime:
    return datetime_provider.utcnow()


class CanonicalEntitlementMutationAuditReviewModel(Base):
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
    reviewed_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    incident_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
