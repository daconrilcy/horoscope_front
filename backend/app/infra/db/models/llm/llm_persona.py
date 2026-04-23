# Modèle DB des personas LLM.
"""Declare les personas, tons et niveaux de verbosite utilises par le prompting LLM."""

from __future__ import annotations

import uuid
from enum import Enum

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import CreatedUpdatedAtMixin
from app.infra.db.models.llm.llm_constraints import allowed_values_check
from app.infra.db.models.llm.llm_field_lengths import FEATURE_LENGTH, SHORT_STATUS_LENGTH
from app.infra.db.models.llm.llm_json_validators import (
    persona_default_formatting,
    validate_persona_formatting,
    validate_string_list_field,
)


class PersonaTone(str, Enum):
    """Liste les tons autorisés pour un persona LLM."""

    WARM = "warm"
    DIRECT = "direct"
    MYSTICAL = "mystical"
    RATIONAL = "rational"


class PersonaVerbosity(str, Enum):
    """Liste les niveaux de verbosité autorisés pour un persona LLM."""

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class LlmPersonaModel(CreatedUpdatedAtMixin, Base):
    """Décrit un persona LLM activable dans les flows de prompting."""

    __tablename__ = "llm_personas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str | None] = mapped_column(
        String(FEATURE_LENGTH), unique=True, index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    tone: Mapped[PersonaTone] = mapped_column(
        String(SHORT_STATUS_LENGTH), default=PersonaTone.DIRECT
    )
    verbosity: Mapped[PersonaVerbosity] = mapped_column(
        String(SHORT_STATUS_LENGTH), default=PersonaVerbosity.MEDIUM
    )

    # JSON list of strings
    style_markers: Mapped[list[str]] = mapped_column(JSON, default=list)
    # JSON list of strings
    boundaries: Mapped[list[str]] = mapped_column(JSON, default=list)
    # JSON list of strings
    allowed_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    # JSON list of strings
    disallowed_topics: Mapped[list[str]] = mapped_column(JSON, default=list)

    # JSON : sections bool, bullets bool, emojis bool
    formatting: Mapped[dict] = mapped_column(JSON, default=persona_default_formatting)

    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    @validates("style_markers", "boundaries", "allowed_topics", "disallowed_topics")
    def validate_string_list(self, key: str, value: object) -> list[str]:
        """Garantit que les listes JSON de persona restent des listes de textes."""
        return validate_string_list_field(key, value)

    @validates("formatting")
    def validate_formatting(self, key: str, value: object) -> dict[str, bool]:
        """Garantit le contrat JSON borne des options de presentation."""
        return validate_persona_formatting(value)

    __table_args__ = (
        allowed_values_check(
            "ck_llm_personas_tone",
            "tone",
            tuple(item.value for item in PersonaTone),
        ),
        allowed_values_check(
            "ck_llm_personas_verbosity",
            "verbosity",
            tuple(item.value for item in PersonaVerbosity),
        ),
        Index("ix_llm_personas_enabled", "enabled"),
    )
