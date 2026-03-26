from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    Boolean,
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
    __table_args__ = (
        CheckConstraint(
            "LOWER(audience) IN ('b2c', 'b2b', 'internal')", name="ck_plan_catalog_audience_valid"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    plan_name: Mapped[str] = mapped_column(String(128), nullable=False)
    audience: Mapped[Audience] = mapped_column(
        SAEnum(Audience, native_enum=False, validate_strings=True),
        index=True,
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(String(64), default="manual", nullable=False)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class FeatureCatalogModel(Base):
    __tablename__ = "feature_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feature_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    feature_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_metered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class PlanFeatureBindingModel(Base):
    __tablename__ = "plan_feature_bindings"
    __table_args__ = (
        UniqueConstraint("plan_id", "feature_id", name="uq_plan_feature_bindings_plan_feature"),
        CheckConstraint(
            "LOWER(access_mode) IN ('disabled', 'unlimited', 'quota')",
            name="ck_plan_feature_bindings_access_mode_valid",
        ),
        CheckConstraint(
            "LOWER(source_origin) IN "
            "('manual', 'migrated_from_billing_plan', 'migrated_from_enterprise_plan')",
            name="ck_plan_feature_bindings_source_origin_valid",
        ),
        Index("ix_plan_feature_bindings_plan_id", "plan_id"),
        Index("ix_plan_feature_bindings_feature_id", "feature_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("plan_catalog.id", ondelete="CASCADE"), nullable=False
    )
    feature_id: Mapped[int] = mapped_column(
        ForeignKey("feature_catalog.id", ondelete="CASCADE"), nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    access_mode: Mapped[AccessMode] = mapped_column(
        SAEnum(AccessMode, native_enum=False, validate_strings=True),
        nullable=False,
    )
    variant_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_origin: Mapped[SourceOrigin] = mapped_column(
        SAEnum(SourceOrigin, native_enum=False, validate_strings=True),
        default=SourceOrigin.MANUAL,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
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
        CheckConstraint(
            "LOWER(period_unit) IN ('day', 'week', 'month', 'year', 'lifetime')",
            name="ck_plan_feature_quotas_period_unit_valid",
        ),
        CheckConstraint(
            "LOWER(reset_mode) IN ('calendar', 'rolling', 'lifetime')",
            name="ck_plan_feature_quotas_reset_mode_valid",
        ),
        CheckConstraint(
            "LOWER(source_origin) IN "
            "('manual', 'migrated_from_billing_plan', 'migrated_from_enterprise_plan')",
            name="ck_plan_feature_quotas_source_origin_valid",
        ),
        Index("ix_plan_feature_quotas_binding_id", "plan_feature_binding_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_feature_binding_id: Mapped[int] = mapped_column(
        ForeignKey("plan_feature_bindings.id", ondelete="CASCADE"),
        nullable=False,
    )
    quota_key: Mapped[str] = mapped_column(String(64), nullable=False)
    quota_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    period_unit: Mapped[PeriodUnit] = mapped_column(
        SAEnum(PeriodUnit, native_enum=False, validate_strings=True),
        nullable=False,
    )
    period_value: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reset_mode: Mapped[ResetMode] = mapped_column(
        SAEnum(ResetMode, native_enum=False, validate_strings=True),
        nullable=False,
    )
    source_origin: Mapped[SourceOrigin] = mapped_column(
        SAEnum(SourceOrigin, native_enum=False, validate_strings=True),
        default=SourceOrigin.MANUAL,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
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
        CheckConstraint(
            "period_value >= 1", name="ck_feature_usage_counters_period_value_positive"
        ),
        CheckConstraint(
            "used_count >= 0", name="ck_feature_usage_counters_used_count_non_negative"
        ),
        CheckConstraint(
            "LOWER(period_unit) = 'lifetime' OR window_end IS NOT NULL",
            name="ck_feature_usage_counters_window_end_required_unless_lifetime",
        ),
        CheckConstraint(
            "LOWER(period_unit) IN ('day', 'week', 'month', 'year', 'lifetime')",
            name="ck_feature_usage_counters_period_unit_valid",
        ),
        CheckConstraint(
            "LOWER(reset_mode) IN ('calendar', 'rolling', 'lifetime')",
            name="ck_feature_usage_counters_reset_mode_valid",
        ),
        Index("ix_feature_usage_counters_user_feature", "user_id", "feature_code"),
        Index(
            "ix_feature_usage_counters_user_feature_quota", "user_id", "feature_code", "quota_key"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    feature_code: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
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
