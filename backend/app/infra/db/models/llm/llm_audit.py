# Mixins d'audit partages par les modeles LLM.
"""Factorise les colonnes d'audit repetees dans les tables LLM."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import utc_now


class CreatedAtMixin:
    """Ajoute la date de creation UTC commune aux modeles LLM."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class UpdatedAtMixin:
    """Ajoute la date de mise a jour UTC commune aux modeles LLM."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class CreatedByMixin:
    """Ajoute l'identifiant de createur commun aux modeles administrables."""

    created_by: Mapped[str] = mapped_column(String(255))


class PublishedAtMixin:
    """Ajoute la date optionnelle de publication aux modeles publiables."""

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CreatedUpdatedAtMixin(CreatedAtMixin, UpdatedAtMixin):
    """Regroupe les timestamps de creation et de mise a jour."""
