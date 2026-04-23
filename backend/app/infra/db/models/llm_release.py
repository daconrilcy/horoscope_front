from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    UUID,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime_provider.utcnow()


class ReleaseStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    ARCHIVED = "archived"


class LlmReleaseSnapshotModel(Base):
    """
    Story 66.32: Atomic release snapshot for LLM configurations.
    Stores a frozen manifest of all assemblies, profiles, personas and schemas.
    """

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


class LlmActiveReleaseModel(Base):
    """
    Story 66.32: Pointer to the currently active LLM release snapshot.
    Only one row should exist in this table (or the one with the latest activated_at is used).
    """

    __tablename__ = "llm_active_releases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    release_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("llm_release_snapshots.id", ondelete="CASCADE")
    )
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    activated_by: Mapped[str] = mapped_column(String(255))

    release_snapshot: Mapped[LlmReleaseSnapshotModel] = relationship("LlmReleaseSnapshotModel")
