from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base
from app.infra.db.models.product_entitlements import PeriodUnit, ResetMode


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EnterpriseFeatureUsageCounterModel(Base):
    __tablename__ = "enterprise_feature_usage_counters"
    __table_args__ = (
        UniqueConstraint(
            "enterprise_account_id",
            "feature_code",
            "quota_key",
            "period_unit",
            "period_value",
            "reset_mode",
            "window_start",
            name="uq_enterprise_feature_usage_counters_composite",
        ),
        CheckConstraint("period_value >= 1", name="ck_enterprise_fuc_period_value_positive"),
        CheckConstraint("used_count >= 0", name="ck_enterprise_fuc_used_count_non_negative"),
        CheckConstraint(
            "LOWER(period_unit) = 'lifetime' OR window_end IS NOT NULL",
            name="ck_enterprise_fuc_window_end_required",
        ),
        CheckConstraint(
            "LOWER(period_unit) IN ('day', 'week', 'month', 'year', 'lifetime')",
            name="ck_enterprise_fuc_period_unit_valid",
        ),
        CheckConstraint(
            "LOWER(reset_mode) IN ('calendar', 'rolling', 'lifetime')",
            name="ck_enterprise_fuc_reset_mode_valid",
        ),
        Index("ix_enterprise_fuc_account_id", "enterprise_account_id"),
        Index("ix_enterprise_fuc_feature_code", "feature_code"),
        Index(
            "ix_enterprise_fuc_account_feature_window",
            "enterprise_account_id",
            "feature_code",
            "window_start",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enterprise_account_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise_accounts.id", ondelete="CASCADE"), nullable=False
    )
    feature_code: Mapped[str] = mapped_column(String(64), nullable=False)
    quota_key: Mapped[str] = mapped_column(String(64), nullable=False)
    period_unit: Mapped[PeriodUnit] = mapped_column(
        SAEnum(PeriodUnit, native_enum=False, validate_strings=True),
        nullable=False,
    )
    period_value: Mapped[int] = mapped_column(Integer, nullable=False)
    reset_mode: Mapped[ResetMode] = mapped_column(
        SAEnum(ResetMode, native_enum=False, validate_strings=True),
        nullable=False,
    )
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
