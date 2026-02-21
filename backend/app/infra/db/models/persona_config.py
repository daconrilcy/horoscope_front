from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PersonaConfigModel(Base):
    __tablename__ = "persona_configs"
    __table_args__ = (
        Index(
            "uq_persona_configs_single_active",
            "status",
            unique=True,
            sqlite_where=text("status = 'active'"),
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[int] = mapped_column(Integer, index=True)
    profile_code: Mapped[str] = mapped_column(String(64), index=True, default="legacy-default")
    display_name: Mapped[str] = mapped_column(String(128), default="Astrologue Principal")
    tone: Mapped[str] = mapped_column(String(32))
    prudence_level: Mapped[str] = mapped_column(String(32))
    scope_policy: Mapped[str] = mapped_column(String(32))
    response_style: Mapped[str] = mapped_column(String(32))
    fallback_policy: Mapped[str] = mapped_column(String(32), default="safe_fallback")
    status: Mapped[str] = mapped_column(String(16), index=True)
    rollback_from_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
