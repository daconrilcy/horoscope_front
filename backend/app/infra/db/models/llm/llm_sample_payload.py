# Modèle DB des payloads d'exemple LLM.
"""Déclare les exemples d'entrée administrables pour qualifier les use cases LLM."""

from __future__ import annotations

import uuid

from sqlalchemy import JSON, UUID, Boolean, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import CreatedUpdatedAtMixin
from app.infra.db.models.llm.llm_field_lengths import (
    FEATURE_LENGTH,
    LOCALE_LENGTH,
    PLAN_LENGTH,
    SAMPLE_PAYLOAD_NAME_LENGTH,
    SUBFEATURE_LENGTH,
)


class LlmSamplePayloadModel(CreatedUpdatedAtMixin, Base):
    """Représente un payload d'exemple versionné par feature et locale."""

    __tablename__ = "llm_sample_payloads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(SAMPLE_PAYLOAD_NAME_LENGTH), nullable=False)
    feature: Mapped[str] = mapped_column(String(FEATURE_LENGTH), nullable=False, index=True)
    subfeature: Mapped[str] = mapped_column(String(SUBFEATURE_LENGTH), nullable=False, default="")
    plan: Mapped[str] = mapped_column(String(PLAN_LENGTH), nullable=False, default="")
    locale: Mapped[str] = mapped_column(
        String(LOCALE_LENGTH), nullable=False, default="fr-FR", index=True
    )
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index(
            "ix_llm_sample_payload_feature_locale_name_unique",
            "feature",
            "subfeature",
            "plan",
            "locale",
            "name",
            unique=True,
        ),
        Index(
            "ix_llm_sample_payload_feature_locale_default_unique",
            "feature",
            "subfeature",
            "plan",
            "locale",
            unique=True,
            postgresql_where=(is_default == True),  # noqa: E712
            sqlite_where=(is_default == True),  # noqa: E712
        ),
    )
