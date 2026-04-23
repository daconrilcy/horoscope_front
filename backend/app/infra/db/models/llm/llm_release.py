# Modèles DB de release LLM.
"""Déclare les snapshots de release LLM et le pointeur de release active."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    UUID,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class ReleaseStatus(str, Enum):
    """Liste les statuts de cycle de vie d'une release LLM."""

    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    ARCHIVED = "archived"


class LlmReleaseSnapshotModel(Base):
    """Stocke un manifeste figé des assemblages, profils, personas et schémas LLM."""

    __tablename__ = "llm_release_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(String(64), index=True)

    # The manifest stores the map of target keys to resolved bundles.
    # Target Key: "feature:subfeature:plan:locale"
    # Bundle: { "assembly": {...}, "profile": {...}, "persona": {...}, "schema": {...} }
    manifest: Mapped[dict] = mapped_column(JSON)

    status: Mapped[ReleaseStatus] = mapped_column(
        String(16), index=True, default=ReleaseStatus.DRAFT
    )

    created_by: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    active_release: Mapped[Optional["LlmActiveReleaseModel"]] = relationship(
        "LlmActiveReleaseModel", back_populates="release_snapshot", uselist=False
    )

    __table_args__ = (UniqueConstraint("version", name="uq_llm_release_snapshots_version"),)


class LlmActiveReleaseModel(Base):
    """Pointe vers le snapshot de release LLM actuellement actif."""

    __tablename__ = "llm_active_releases"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    release_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("llm_release_snapshots.id", ondelete="CASCADE")
    )
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    activated_by: Mapped[str] = mapped_column(String(255))

    release_snapshot: Mapped[LlmReleaseSnapshotModel] = relationship(
        "LlmReleaseSnapshotModel", back_populates="active_release"
    )

    __table_args__ = (CheckConstraint("id = 1", name="ck_llm_active_releases_singleton_id"),)
