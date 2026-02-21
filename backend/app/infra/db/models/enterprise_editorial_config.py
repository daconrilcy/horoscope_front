from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EnterpriseEditorialConfigModel(Base):
    __tablename__ = "enterprise_editorial_configs"
    __table_args__ = (
        UniqueConstraint(
            "enterprise_account_id",
            "version_number",
            name="uq_enterprise_editorial_configs_account_version",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enterprise_account_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise_accounts.id"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    tone: Mapped[str] = mapped_column(String(16), default="neutral")
    length_style: Mapped[str] = mapped_column(String(16), default="medium")
    output_format: Mapped[str] = mapped_column(String(16), default="paragraph")
    preferred_terms: Mapped[list[str]] = mapped_column(JSON, default=list)
    avoided_terms: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_by_credential_id: Mapped[int | None] = mapped_column(
        ForeignKey("enterprise_api_credentials.id"),
        nullable=True,
        index=True,
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
