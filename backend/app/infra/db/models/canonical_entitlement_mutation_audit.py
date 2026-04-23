from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime_provider.utcnow()


class CanonicalEntitlementMutationAuditModel(Base):
    __tablename__ = "canonical_entitlement_mutation_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    operation: Mapped[str] = mapped_column(String(64), nullable=False)
    plan_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    plan_code_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    feature_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_origin: Mapped[str] = mapped_column(String(64), nullable=False)
    before_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    after_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
