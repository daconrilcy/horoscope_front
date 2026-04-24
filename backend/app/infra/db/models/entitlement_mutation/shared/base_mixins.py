# Mixins SQLAlchemy partagés du sous-domaine entitlement mutation.
"""Factorise les colonnes techniques communes aux modèles entitlement mutation."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.models.entitlement_mutation.shared.timestamps import now_utc


class CreatedAtMixin:
    """Ajoute une date de création en UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc, index=True
    )


class UpdatedAtMixin:
    """Ajoute une date de mise à jour en UTC."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc
    )


class OccurredAtMixin:
    """Ajoute une date d'occurrence append-only en UTC."""

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc, index=True
    )


class RequestIdMixin:
    """Ajoute un identifiant de requête optionnel."""

    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class OpsCommentMixin:
    """Ajoute un commentaire ops optionnel."""

    ops_comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class ActionUserMixin:
    """Ajoute l'identifiant de l'utilisateur ayant effectué l'action."""

    handled_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ReviewedByUserMixin:
    """Ajoute l'identifiant de l'utilisateur ayant effectué la revue."""

    reviewed_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
