"""Modèles SQLAlchemy des référentiels éditoriaux d'interprétation astrologique."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base
from app.infra.db.models.reference import _ensure_reference_version_is_mutable

if TYPE_CHECKING:
    from app.infra.db.models.reference import HouseModel, ReferenceVersionModel


class HouseInterpretationProfileModel(Base):
    """Profil éditorial versionné pour interpréter une maison astrologique."""

    __tablename__ = "house_interpretation_profiles"
    __table_args__ = (
        UniqueConstraint("reference_version_id", "house_id", "language", "tradition"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
        nullable=False,
        index=True,
    )
    house_id: Mapped[int] = mapped_column(
        ForeignKey("astral_houses.id"),
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    tradition: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    core_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    shadow_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    psychological_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    material_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    relationship_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    health_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    spiritual_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_parts_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    archetypes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    dos_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    donts_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_hints_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    house: Mapped["HouseModel"] = relationship()


@event.listens_for(HouseInterpretationProfileModel, "before_update")
def _prevent_update_on_locked_interpretation_version(
    mapper: object, connection: object, target: object
) -> None:
    """Bloque les modifications directes d'un profil rattaché à une version verrouillée."""
    del mapper, connection
    _ensure_reference_version_is_mutable(target)
