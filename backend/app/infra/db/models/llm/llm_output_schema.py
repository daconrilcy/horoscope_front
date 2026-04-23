# Modèle DB des schémas de sortie LLM.
"""Déclare les contrats JSON de sortie réutilisés par les use cases LLM."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    UUID,
    DateTime,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class LlmOutputSchemaModel(Base):
    """Représente un schéma JSON versionné attendu en sortie d'un appel LLM."""

    __tablename__ = "llm_output_schemas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64))
    json_schema: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_llm_output_schemas_name_version"),
        Index("ix_llm_output_schemas_name", "name"),
    )
