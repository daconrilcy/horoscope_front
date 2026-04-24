# Mixins et helpers temporels partages par les modeles LLM.
"""Factorise les colonnes d'audit et les defaults temporels communs du perimetre LLM."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider, utc_now
from app.infra.db.models.llm.llm_field_lengths import ACTOR_IDENTIFIER_LENGTH


def utc_now_plus_days(days: int):
    """Retourne un callable SQLAlchemy partage pour une expiration relative en UTC."""

    def _factory() -> datetime:
        return datetime_provider.utcnow() + timedelta(days=days)

    return _factory


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

    created_by: Mapped[str] = mapped_column(String(ACTOR_IDENTIFIER_LENGTH))


class PublishedAtMixin:
    """Ajoute la date optionnelle de publication aux modeles publiables."""

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CreatedUpdatedAtMixin(CreatedAtMixin, UpdatedAtMixin):
    """Regroupe les timestamps de creation et de mise a jour."""
