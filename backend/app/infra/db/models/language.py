# Commentaire global: modèle SQLAlchemy minimal des langues applicatives.
"""Déclare la table des langues supportées hors référentiel astrologique local."""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class LanguageModel(Base):
    """Représente une langue disponible pour l'interface et les appels Astral."""

    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
