# Modèle DB des schémas de sortie LLM.
"""Declare les contrats JSON de sortie reutilises par les use cases LLM."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    JSON,
    UUID,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import CreatedAtMixin
from app.infra.db.models.llm.llm_field_lengths import FEATURE_LENGTH


class LlmOutputSchemaModel(CreatedAtMixin, Base):
    """Represente un schema JSON versionne attendu en sortie d un appel LLM."""

    __tablename__ = "llm_output_schemas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(FEATURE_LENGTH))
    json_schema: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    assemblies = relationship("PromptAssemblyConfigModel", back_populates="output_schema")

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_llm_output_schemas_name_version"),
        Index("ix_llm_output_schemas_name", "name"),
    )
