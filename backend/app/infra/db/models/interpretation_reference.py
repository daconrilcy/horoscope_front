"""Modèles SQLAlchemy des référentiels éditoriaux d'interprétation astrologique."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base
from app.infra.db.models.reference import _ensure_reference_version_is_mutable

if TYPE_CHECKING:
    from app.infra.db.models.reference import (
        AspectModel,
        AstralSystemModel,
        HouseModel,
        LanguageModel,
        PlanetModel,
        ReferenceVersionModel,
    )


class HouseInterpretationProfileModel(Base):
    """Profil éditorial versionné pour interpréter une maison astrologique."""

    __tablename__ = "astral_house_interpretation_profiles"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "house_id",
            "language_id",
            "astral_system_id",
            name="uq_astral_house_interpretation_profiles_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    house_id: Mapped[int] = mapped_column(
        ForeignKey("astral_houses.id"),
        nullable=False,
        index=True,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id"),
        nullable=False,
        index=True,
    )
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"),
        nullable=False,
        index=True,
    )
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
    astral_system: Mapped["AstralSystemModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralAspectInterpretationProfileModel(Base):
    """Profil éditorial versionné pour interpréter un aspect astrologique."""

    __tablename__ = "astral_aspect_interpretation_profiles"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "aspect_id",
            "astral_system_id",
            "language_id",
            name="uq_astral_aspect_interpretation_profiles_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    aspect_id: Mapped[int] = mapped_column(
        ForeignKey("astral_aspects.id"),
        nullable=False,
        index=True,
    )
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"),
        nullable=False,
        index=True,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    core_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    shadow_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    psychological_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    relationship_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    spiritual_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    energetic_dynamics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    growth_patterns_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    conflict_patterns_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    archetypes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    dos_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    donts_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_hints_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    aspect: Mapped["AspectModel"] = relationship()
    astral_system: Mapped["AstralSystemModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralPlanetInterpretationProfileModel(Base):
    """Profil éditorial versionné pour interpréter une planète astrologique."""

    __tablename__ = "astral_planet_interpretation_profiles"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "planet_id",
            "astral_system_id",
            "language_id",
            name="uq_astral_planet_interpretation_profiles_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"),
        nullable=False,
        index=True,
    )
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"),
        nullable=False,
        index=True,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    core_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    shadow_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    psychological_expression_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    relational_expression_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    vocational_expression_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    spiritual_expression_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    energetic_dynamics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    growth_patterns_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    conflict_patterns_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    archetypes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    dos_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    donts_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_hints_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    planet: Mapped["PlanetModel"] = relationship()
    astral_system: Mapped["AstralSystemModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralHouseAxisDefinitionModel(Base):
    """Définition localisée d'un axe de maisons astrologiques."""

    __tablename__ = "astral_house_axis_definitions"
    __table_args__ = (
        UniqueConstraint(
            "astral_system_id",
            "key",
            "language_id",
            name="uq_astral_house_axis_definitions_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id"),
        nullable=False,
        index=True,
    )
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    astral_system: Mapped["AstralSystemModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralHouseAxisMemberModel(Base):
    """Association canonique entre une maison, son axe et sa maison opposée."""

    __tablename__ = "astral_house_axis_members"
    __table_args__ = (
        UniqueConstraint("house_id", name="uq_astral_house_axis_members_house_id"),
        UniqueConstraint(
            "axis_id",
            "house_id",
            name="uq_astral_house_axis_members_axis_house",
        ),
        CheckConstraint(
            "house_id <> opposite_house_id",
            name="ck_astral_house_axis_members_distinct_houses",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    axis_id: Mapped[int] = mapped_column(
        ForeignKey("astral_house_axis_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    house_id: Mapped[int] = mapped_column(
        ForeignKey("astral_houses.id"),
        nullable=False,
        index=True,
    )
    opposite_house_id: Mapped[int] = mapped_column(
        ForeignKey("astral_houses.id"),
        nullable=False,
        index=True,
    )

    axis: Mapped["AstralHouseAxisDefinitionModel"] = relationship()
    house: Mapped["HouseModel"] = relationship(foreign_keys=[house_id])
    opposite_house: Mapped["HouseModel"] = relationship(foreign_keys=[opposite_house_id])


@event.listens_for(HouseInterpretationProfileModel, "before_update")
def _prevent_update_on_locked_interpretation_version(
    mapper: object, connection: object, target: object
) -> None:
    """Bloque les modifications directes d'un profil rattaché à une version verrouillée."""
    del mapper, connection
    _ensure_reference_version_is_mutable(target)


@event.listens_for(AstralAspectInterpretationProfileModel, "before_update")
def _prevent_update_on_locked_aspect_interpretation_version(
    mapper: object, connection: object, target: object
) -> None:
    """Bloque les modifications directes d'un profil d'aspect publié."""
    del mapper, connection
    _ensure_reference_version_is_mutable(target)


@event.listens_for(AstralPlanetInterpretationProfileModel, "before_update")
def _prevent_update_on_locked_planet_interpretation_version(
    mapper: object, connection: object, target: object
) -> None:
    """Bloque les modifications directes d'un profil planétaire publié."""
    del mapper, connection
    _ensure_reference_version_is_mutable(target)
