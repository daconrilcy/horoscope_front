"""Modèles des traductions des référentiels astrologiques stables."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.models.interpretation_reference import (
        AstralAspectInterpretationProfileModel,
        AstralPlanetInterpretationProfileModel,
        HouseInterpretationProfileModel,
    )
    from app.infra.db.models.reference import (
        AspectModel,
        AstralSignModel,
        HouseModel,
        LanguageModel,
        PlanetModel,
    )


class AstralSignTranslationModel(Base):
    """Traduction localisée d'un signe astrologique canonique."""

    __tablename__ = "astral_sign_translations"
    __table_args__ = (
        UniqueConstraint(
            "astral_sign_id",
            "language_id",
            name="uq_astral_sign_translations_sign_language",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    astral_sign_id: Mapped[int] = mapped_column(
        ForeignKey("astral_signs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    translated_name: Mapped[str] = mapped_column(String(128), nullable=False)

    sign: Mapped["AstralSignModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralHouseTranslationModel(Base):
    """Traduction localisée d'une maison astrologique canonique."""

    __tablename__ = "astral_house_translations"
    __table_args__ = (
        UniqueConstraint(
            "house_id",
            "language_id",
            name="uq_astral_house_translations_house_language",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    house_id: Mapped[int] = mapped_column(
        ForeignKey("astral_houses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    translated_name: Mapped[str] = mapped_column(String(128), nullable=False)

    house: Mapped["HouseModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralPlanetTranslationModel(Base):
    """Traduction localisée d'une planète astrologique canonique."""

    __tablename__ = "astral_planet_translations"
    __table_args__ = (
        UniqueConstraint(
            "planet_id",
            "language_id",
            name="uq_astral_planet_translations_planet_language",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    translated_name: Mapped[str] = mapped_column(String(128), nullable=False)

    planet: Mapped["PlanetModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralAspectTranslationModel(Base):
    """Traduction localisée d'un aspect astrologique canonique."""

    __tablename__ = "astral_aspect_translations"
    __table_args__ = (
        UniqueConstraint(
            "aspect_id",
            "language_id",
            name="uq_astral_aspect_translations_aspect_language",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aspect_id: Mapped[int] = mapped_column(
        ForeignKey("astral_aspects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    translated_name: Mapped[str] = mapped_column(String(128), nullable=False)

    aspect: Mapped["AspectModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralHouseInterpretationProfileTranslationModel(Base):
    """Traduction éditoriale d'un profil source de maison astrologique."""

    __tablename__ = "astral_house_interpretation_profile_translations"
    __table_args__ = (
        UniqueConstraint(
            "source_profile_id",
            "language_id",
            name="uq_astral_house_interpretation_profile_translations_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_profile_id: Mapped[int] = mapped_column(
        ForeignKey("astral_house_interpretation_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_profile: Mapped["HouseInterpretationProfileModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralPlanetInterpretationProfileTranslationModel(Base):
    """Traduction éditoriale d'un profil source de planète astrologique."""

    __tablename__ = "astral_planet_interpretation_profile_translations"
    __table_args__ = (
        UniqueConstraint(
            "source_profile_id",
            "language_id",
            name="uq_astral_planet_interpretation_profile_translations_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_profile_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planet_interpretation_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_profile: Mapped["AstralPlanetInterpretationProfileModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralAspectInterpretationProfileTranslationModel(Base):
    """Traduction éditoriale d'un profil source d'aspect astrologique."""

    __tablename__ = "astral_aspect_interpretation_profile_translations"
    __table_args__ = (
        UniqueConstraint(
            "source_profile_id",
            "language_id",
            name="uq_astral_aspect_interpretation_profile_translations_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_profile_id: Mapped[int] = mapped_column(
        ForeignKey("astral_aspect_interpretation_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_profile: Mapped["AstralAspectInterpretationProfileModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()
