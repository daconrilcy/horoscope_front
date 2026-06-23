"""Modèle SQLAlchemy du compte utilisateur et de ses préférences applicatives."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.models.language import LanguageModel


class UserModel(Base):
    """Utilisateur applicatif et préférences globales associées au compte."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), index=True)
    default_language_id: Mapped[int | None] = mapped_column(
        ForeignKey("languages.id"),
        nullable=True,
        index=True,
    )
    detected_locale: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detected_country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    detected_timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email_unsubscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    default_language: Mapped["LanguageModel | None"] = relationship()
