from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EnterpriseBillingPlanModel(Base):
    __tablename__ = "enterprise_billing_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128))
    monthly_fixed_cents: Mapped[int] = mapped_column(Integer)
    included_monthly_units: Mapped[int] = mapped_column(Integer, default=0)
    overage_unit_price_cents: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        index=True,
    )


class EnterpriseAccountBillingPlanModel(Base):
    __tablename__ = "enterprise_account_billing_plans"
    __table_args__ = (
        UniqueConstraint(
            "enterprise_account_id",
            name="uq_enterprise_account_billing_plans_account",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enterprise_account_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise_accounts.id"),
        index=True,
    )
    plan_id: Mapped[int] = mapped_column(ForeignKey("enterprise_billing_plans.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        index=True,
    )


class EnterpriseBillingCycleModel(Base):
    __tablename__ = "enterprise_billing_cycles"
    __table_args__ = (
        UniqueConstraint(
            "enterprise_account_id",
            "period_start",
            "period_end",
            name="uq_enterprise_billing_cycles_account_period",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enterprise_account_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise_accounts.id"),
        index=True,
    )
    plan_id: Mapped[int] = mapped_column(ForeignKey("enterprise_billing_plans.id"), index=True)
    period_start: Mapped[date] = mapped_column(Date, index=True)
    period_end: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(16), default="closed", index=True)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    fixed_amount_cents: Mapped[int] = mapped_column(Integer)
    included_units: Mapped[int] = mapped_column(Integer, default=0)
    consumed_units: Mapped[int] = mapped_column(Integer, default=0)
    billable_units: Mapped[int] = mapped_column(Integer, default=0)
    unit_price_cents: Mapped[int] = mapped_column(Integer, default=0)
    variable_amount_cents: Mapped[int] = mapped_column(Integer, default=0)
    total_amount_cents: Mapped[int] = mapped_column(Integer)
    limit_mode: Mapped[str] = mapped_column(String(16), default="block")
    overage_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    calculation_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    closed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        index=True,
    )
