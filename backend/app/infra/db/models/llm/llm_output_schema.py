# Modèle DB des schémas de sortie LLM.
"""Déclare les contrats JSON de sortie réutilisés par les use cases LLM."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    UUID,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def utc_now() -> datetime:
    """Retourne l'instant UTC centralisé pour les colonnes d'audit LLM."""
    return datetime_provider.utcnow()


class LlmOutputSchemaModel(Base):
    """Représente un schéma JSON versionné attendu en sortie d'un appel LLM."""

    __tablename__ = "llm_output_schemas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    json_schema: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
