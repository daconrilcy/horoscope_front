# Commentaire global: persistance applicative des themes natals Astral deja produits.
"""Modèle SQLAlchemy des thèmes natals Astral stockés pour éviter les régénérations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class UserAstralNatalThemeModel(Base):
    """Stocke un résultat de job natal Astral rattaché à un utilisateur et un niveau."""

    __tablename__ = "user_astral_natal_themes"
    __table_args__ = (
        Index(
            "ix_user_astral_natal_themes_reusable_lookup",
            "user_id",
            "birth_profile_id",
            "theme_level",
            "birth_fingerprint",
            "status",
            "created_at",
        ),
        Index("ix_user_astral_natal_themes_run_id", "run_id", unique=True),
        Index("ix_user_astral_natal_themes_user_created", "user_id", "created_at"),
        Index("ix_user_astral_natal_themes_client_request", "client_request_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    birth_profile_id: Mapped[int] = mapped_column(
        ForeignKey("user_birth_profiles.id"),
        nullable=False,
        index=True,
    )
    birth_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    theme_level: Mapped[str] = mapped_column(String(16), nullable=False)
    requested_product: Mapped[str] = mapped_column(String(32), nullable=False)
    requested_plan: Mapped[str] = mapped_column(String(16), nullable=False)
    service_code: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    run_id: Mapped[str] = mapped_column(String(128), nullable=False)
    client_request_id: Mapped[str] = mapped_column(String(128), nullable=False)
    response_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
