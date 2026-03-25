from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Audience(str, Enum):
    B2C = "b2c"
    B2B = "b2b"
    INTERNAL = "internal"


class AccessMode(str, Enum):
    DISABLED = "disabled"
    UNLIMITED = "unlimited"
    QUOTA = "quota"


class PeriodUnit(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    LIFETIME = "lifetime"


class ResetMode(str, Enum):
    CALENDAR = "calendar"
    ROLLING = "rolling"
    LIFETIME = "lifetime"


class SourceOrigin(str, Enum):
    MANUAL = "manual"
    MIGRATED_FROM_BILLING_PLAN = "migrated_from_billing_plan"
    MIGRATED_FROM_ENTERPRISE_PLAN = "migrated_from_enterprise_plan"


class PlanCatalogModel(Base):
    __tablename__ = "plan_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    plan_name: Mapped[str] = mapped_column(String(128))
    audience: Mapped[str] = mapped_column(String(32), index=True)  # Using Enum Audience
    source_type: Mapped[str] = mapped_column(String(64), default="manual")
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class FeatureCatalogModel(Base):
    __tablename__ = "feature_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feature_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    feature_name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_metered: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class PlanFeatureBindingModel(Base):
    __tablename__ = "plan_feature_bindings"
    __table_args__ = (
        UniqueConstraint("plan_id", "feature_id", name="uq_plan_feature_bindings_plan_feature"),
        Index("ix_plan_feature_bindings_plan_id", "plan_id"),
        Index("ix_plan_feature_bindings_feature_id", "feature_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_catalog.id", ondelete="CASCADE"))
    feature_id: Mapped[int] = mapped_column(ForeignKey("feature_catalog.id", ondelete="CASCADE"))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    access_mode: Mapped[str] = mapped_column(String(32))  # Using Enum AccessMode
    variant_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_origin: Mapped[str] = mapped_column(String(64), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class PlanFeatureQuotaModel(Base):
    __tablename__ = "plan_feature_quotas"
    __table_args__ = (
        UniqueConstraint(
            "plan_feature_binding_id",
            "quota_key",
            "period_unit",
            "period_value",
            "reset_mode",
            name="uq_plan_feature_quotas_composite",
        ),
        CheckConstraint("quota_limit > 0", name="ck_plan_feature_quotas_quota_limit_positive"),
        CheckConstraint("period_value >= 1", name="ck_plan_feature_quotas_period_value_positive"),
        Index("ix_plan_feature_quotas_binding_id", "plan_feature_binding_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_feature_binding_id: Mapped[int] = mapped_column(
        ForeignKey("plan_feature_bindings.id", ondelete="CASCADE")
    )
    quota_key: Mapped[str] = mapped_column(String(64))
    quota_limit: Mapped[int] = mapped_column(Integer)
    period_unit: Mapped[str] = mapped_column(String(32))  # Using Enum PeriodUnit
    period_value: Mapped[int] = mapped_column(Integer, default=1)
    reset_mode: Mapped[str] = mapped_column(String(32))  # Using Enum ResetMode
    source_origin: Mapped[str] = mapped_column(String(64), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class FeatureUsageCounterModel(Base):
    __tablename__ = "feature_usage_counters"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "feature_code",
            "quota_key",
            "period_unit",
            "period_value",
            "reset_mode",
            "window_start",
            name="uq_feature_usage_counters_composite",
        ),
        CheckConstraint("used_count >= 0", name="ck_feature_usage_counters_used_count_non_negative"),
        Index("ix_feature_usage_counters_user_feature", "user_id", "feature_code"),
        Index("ix_feature_usage_counters_user_feature_quota", "user_id", "feature_code", "quota_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    feature_code: Mapped[str] = mapped_column(String(64), index=True)
    quota_key: Mapped[str] = mapped_column(String(64))
    period_unit: Mapped[str] = mapped_column(String(32))
    period_value: Mapped[int] = mapped_column(Integer)
    reset_mode: Mapped[str] = mapped_column(String(32))
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
