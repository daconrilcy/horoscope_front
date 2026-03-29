from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def _utc_now() -> datetime:
    from datetime import timezone
    return datetime.now(timezone.utc)


class CanonicalEntitlementMutationAlertSuppressionRuleModel(Base):
    __tablename__ = "canonical_entitlement_mutation_alert_suppression_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    feature_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    plan_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    actor_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    suppression_key: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ops_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    updated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )
