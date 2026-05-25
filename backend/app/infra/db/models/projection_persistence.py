# Modele de persistance canonique des projections internes auditees.
"""Stocke les payloads de projection avec version, provenance et hash."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class PersistedProjectionModel(Base):
    """Projection interne persistée pour audit et reutilisation contrôlée."""

    __tablename__ = "persisted_projections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chart_id: Mapped[str] = mapped_column(String(36), index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    projection_type: Mapped[str] = mapped_column(String(96), index=True)
    projection_version: Mapped[str] = mapped_column(String(64), index=True)
    projection_hash: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON)
    source_versions: Mapped[dict[str, object]] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(String(128), index=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
    )
