from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EnterpriseDailyUsageModel(Base):
    __tablename__ = "enterprise_daily_usages"
    __table_args__ = (
        UniqueConstraint(
            "enterprise_account_id",
            "credential_id",
            "usage_date",
            name="uq_enterprise_daily_usages_account_credential_date",
        ),
        Index(
            "ix_enterprise_daily_usages_account_date",
            "enterprise_account_id",
            "usage_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enterprise_account_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise_accounts.id"), index=True
    )
    credential_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise_api_credentials.id"), index=True
    )
    usage_date: Mapped[date] = mapped_column(index=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
