from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime_provider.utcnow()


class ConsultationTemplateModel(Base):
    """
    Modèle pour le catalogue des consultations types piloté par la base.
    Permet de modifier l'éditorial, les icônes et les prompts sans toucher au code.
    """

    __tablename__ = "consultation_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Clé métier stable (ex: 'period', 'career', 'orientation')
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    # Référence d'icône (emoji, path d'asset ou clé d'icône front)
    icon_ref: Mapped[str] = mapped_column(String(255))

    # Libellés éditoriaux
    title: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(Text)

    # Contenu du prompt associé à ce type de consultation
    prompt_content: Mapped[str] = mapped_column(Text)

    # Configuration additionnelle (tags, required_data pour le wizard, flags, etc.)
    # Format: {"tags": ["Introspection"], "required_data": ["birth_profile"],
    #          "fallback_allowed": true}
    metadata_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
