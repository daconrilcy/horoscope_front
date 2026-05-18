"""Modèles SQLAlchemy des données de référence astrologiques."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, object_session, relationship

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class ReferenceVersionModel(Base):
    __tablename__ = "astral_reference_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    is_locked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PlanetModel(Base):
    """Planète astrologique stable utilisée comme vocabulaire canonique."""

    __tablename__ = "astral_planets"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))
    swe_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AstralSignModel(Base):
    """Signe astrologique stable, indépendant des versions de paramétrage."""

    __tablename__ = "astral_signs"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))


class AstralConstellationModel(Base):
    """Constellation astronomique stable utilisée comme vocabulaire astral."""

    __tablename__ = "astral_constellations"
    __table_args__ = (
        UniqueConstraint("key"),
        UniqueConstraint("abbreviation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    latin_name: Mapped[str] = mapped_column(String(128), nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    zodiacal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hemisphere_id: Mapped[int | None] = mapped_column(
        ForeignKey("astral_hemispheres.id"), nullable=True, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    hemisphere: Mapped["AstralHemisphereModel | None"] = relationship()


class AstralHemisphereModel(Base):
    """Hémisphère céleste stable utilisé comme métadonnée astronomique."""

    __tablename__ = "astral_hemispheres"
    __table_args__ = (UniqueConstraint("key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    usage_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class AstralZodiacalReferenceSystemCategoryModel(Base):
    """Catégorie stable des systèmes de référence zodiacaux."""

    __tablename__ = "astral_zodiacal_reference_system_categories"
    __table_args__ = (UniqueConstraint("key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    usage_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class AstralZodiacalReferenceSystemModel(Base):
    """Système de référence zodiacal stable utilisable par les calculs astraux."""

    __tablename__ = "astral_zodiacal_reference_systems"
    __table_args__ = (UniqueConstraint("key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("astral_zodiacal_reference_system_categories.id"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requires_ayanamsha: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    usage_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped["AstralZodiacalReferenceSystemCategoryModel"] = relationship()


class AstralReferenceEpochModel(Base):
    """Époque de référence stable pour les coordonnées astronomiques."""

    __tablename__ = "astral_reference_epochs"
    __table_args__ = (
        UniqueConstraint("key"),
        CheckConstraint(
            "epoch_type IN ('julian_epoch', 'besselian_epoch', 'runtime_epoch')",
            name="ck_astral_reference_epochs_epoch_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    epoch_type: Mapped[str] = mapped_column(String(32), nullable=False)
    julian_year: Mapped[float | None] = mapped_column(Float, nullable=True)
    iso_datetime: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_standard: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    usage_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class AstralReferenceSourceModel(Base):
    """Source documentaire ou technique d'un référentiel astral."""

    __tablename__ = "astral_reference_sources"
    __table_args__ = (
        UniqueConstraint("key"),
        CheckConstraint(
            (
                "category IN ('internal', 'astronomical_engine', 'astronomical_catalog', "
                "'astronomical_reference', 'astrological_interpretation', "
                "'historical_astrological_source', 'astrological_platform')"
            ),
            name="ck_astral_reference_sources_category",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    publisher: Mapped[str | None] = mapped_column(String(128), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_canonical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    usage_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class AstralFixedStarModel(Base):
    """Étoile fixe stable identifiée par son nom propre canonique."""

    __tablename__ = "astral_fixed_stars"
    __table_args__ = (UniqueConstraint("key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)


class AstralFixedStarKeywordModel(Base):
    """Groupe stable de mots-clés interprétatifs pour une étoile fixe."""

    __tablename__ = "astral_fixed_star_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keywords_json: Mapped[str] = mapped_column(Text, nullable=False)


class AstralFixedStarDefinitionModel(Base):
    """Définition astronomique et astrologique stable d'une étoile fixe."""

    __tablename__ = "astral_fixed_star_definitions"
    __table_args__ = (UniqueConstraint("fixed_star_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fixed_star_id: Mapped[int] = mapped_column(
        ForeignKey("astral_fixed_stars.id"), nullable=False, index=True
    )
    constellation_id: Mapped[int] = mapped_column(
        ForeignKey("astral_constellations.id"), nullable=False, index=True
    )
    zodiacal_reference_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_zodiacal_reference_systems.id"), nullable=False, index=True
    )
    reference_epoch_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_epochs.id"), nullable=False, index=True
    )
    ecliptic_longitude_deg: Mapped[float] = mapped_column(Float, nullable=False)
    zodiac_sign_id: Mapped[int] = mapped_column(
        ForeignKey("astral_signs.id"), nullable=False, index=True
    )
    zodiac_degree: Mapped[float] = mapped_column(Float, nullable=False)
    declination_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    right_ascension_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    visual_magnitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    astral_fixed_star_keywords_id: Mapped[int] = mapped_column(
        ForeignKey("astral_fixed_star_keywords.id"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_sources.id"), nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    fixed_star: Mapped["AstralFixedStarModel"] = relationship()
    constellation: Mapped["AstralConstellationModel"] = relationship()
    zodiacal_reference_system: Mapped["AstralZodiacalReferenceSystemModel"] = relationship()
    reference_epoch: Mapped["AstralReferenceEpochModel"] = relationship()
    zodiac_sign: Mapped["AstralSignModel"] = relationship()
    keywords: Mapped["AstralFixedStarKeywordModel"] = relationship()
    source: Mapped["AstralReferenceSourceModel"] = relationship()


class AstralPointFamilyModel(Base):
    """Famille stable de points astrologiques calculés."""

    __tablename__ = "astral_point_families"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class AstralPointModel(Base):
    """Point astrologique calculé canonique, distinct des variantes de calcul."""

    __tablename__ = "astral_points"
    __table_args__ = (
        UniqueConstraint("code"),
        ForeignKeyConstraint(["point_family"], ["astral_point_families.code"]),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    point_family: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    astronomical_type: Mapped[str] = mapped_column(String(64), nullable=False)
    is_physical_body: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    family: Mapped["AstralPointFamilyModel"] = relationship()


class AstralPointCalculationVariantModel(Base):
    """Variante de calcul d'un point astrologique canonique."""

    __tablename__ = "astral_point_calculation_variants"
    __table_args__ = (
        UniqueConstraint(
            "astral_point_code",
            "variant_code",
            name="uq_astral_point_calculation_variants_scope",
        ),
        ForeignKeyConstraint(["astral_point_code"], ["astral_points.code"]),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    astral_point_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    variant_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    calculation_mode: Mapped[str] = mapped_column(String(64), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    astral_point: Mapped["AstralPointModel"] = relationship()


class AstralPointAliasModel(Base):
    """Alias localisé ou clé moteur pour un point astrologique calculé."""

    __tablename__ = "astral_point_aliases"
    __table_args__ = (
        UniqueConstraint(
            "astral_point_code",
            "variant_code",
            "alias",
            "language_id",
            "source",
            name="uq_astral_point_aliases_scope",
        ),
        ForeignKeyConstraint(["astral_point_code"], ["astral_points.code"]),
        ForeignKeyConstraint(
            ["astral_point_code", "variant_code"],
            [
                "astral_point_calculation_variants.astral_point_code",
                "astral_point_calculation_variants.variant_code",
            ],
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    astral_point_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    variant_code: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    alias: Mapped[str] = mapped_column(String(128), nullable=False)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    engine_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    astral_point: Mapped["AstralPointModel"] = relationship()
    language: Mapped["LanguageModel"] = relationship()


class AstralPointInterpretationKeywordModel(Base):
    """Groupe stable de mots-clés interprétatifs pour un point astrologique."""

    __tablename__ = "astral_point_interpretation_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    core_keywords_json: Mapped[str] = mapped_column(Text, nullable=False)
    shadow_keywords_json: Mapped[str] = mapped_column(Text, nullable=False)
    psychological_keywords_json: Mapped[str] = mapped_column(Text, nullable=False)
    spiritual_keywords_json: Mapped[str] = mapped_column(Text, nullable=False)
    relationship_keywords_json: Mapped[str] = mapped_column(Text, nullable=False)
    career_keywords_json: Mapped[str] = mapped_column(Text, nullable=False)


class AstralElementModel(Base):
    """Taxonomie stable des éléments astrologiques."""

    __tablename__ = "astral_elements"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class AstralModalityModel(Base):
    """Taxonomie stable des modalités astrologiques."""

    __tablename__ = "astral_modalities"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class AstralPolarityModel(Base):
    """Taxonomie stable des polarités astrologiques."""

    __tablename__ = "astral_polarities"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class AstralTypicalPolarityModel(Base):
    """Polarité usuelle utilisée par les profils interprétatifs planétaires."""

    __tablename__ = "astral_typical_polarities"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)


class AstralSpeedModel(Base):
    """Classe de vitesse relative utilisée pour qualifier les planètes."""

    __tablename__ = "astral_speed"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    speed_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AstralPlanetDefinitionModel(Base):
    """Définition structurelle d'une planète astrologique canonique."""

    __tablename__ = "astral_planet_definitions"
    __table_args__ = (UniqueConstraint("planet_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    object_type_id: Mapped[int] = mapped_column(
        ForeignKey("astral_object_types.id"), nullable=False, index=True
    )
    astrological_role_id: Mapped[int] = mapped_column(
        ForeignKey("astral_astrological_roles.id"), nullable=False, index=True
    )
    calculation_type_id: Mapped[int] = mapped_column(
        ForeignKey("astral_calculation_types.id"), nullable=False, index=True
    )
    speed_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    speed_class_id: Mapped[int] = mapped_column(
        ForeignKey("astral_speed.id"), nullable=False, index=True
    )
    typical_polarity_id: Mapped[int] = mapped_column(
        ForeignKey("astral_typical_polarities.id"), nullable=False, index=True
    )
    is_physical_body: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_luminary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_planet: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_visible_to_naked_eye: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    planet: Mapped["PlanetModel"] = relationship()
    object_type: Mapped["AstralObjectTypeModel"] = relationship()
    astrological_role: Mapped["AstralAstrologicalRoleModel"] = relationship()
    calculation_type: Mapped["AstralCalculationTypeModel"] = relationship()
    speed_class: Mapped["AstralSpeedModel"] = relationship()
    typical_polarity: Mapped["AstralTypicalPolarityModel"] = relationship()


class AstralDignityTypeModel(Base):
    """Taxonomie stable des types de dignités astrologiques."""

    __tablename__ = "astral_dignity_type"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)


class AstralSystemModel(Base):
    """Taxonomie stable des systèmes astrologiques et de leur héritage."""

    __tablename__ = "astral_systems"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    inherits_from_system_id: Mapped[int | None] = mapped_column(
        ForeignKey("astral_systems.id"), nullable=True, index=True
    )

    inherits_from: Mapped["AstralSystemModel | None"] = relationship(
        remote_side=[id], back_populates="inherited_by"
    )
    inherited_by: Mapped[list["AstralSystemModel"]] = relationship(back_populates="inherits_from")


class AstralAspectFamilyModel(Base):
    """Famille stable regroupant les aspects par usage astrologique."""

    __tablename__ = "astral_aspect_families"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class AstralHouseSystemModel(Base):
    """Référentiel canonique des systèmes de maisons disponibles."""

    __tablename__ = "astral_house_systems"
    __table_args__ = (
        UniqueConstraint("code"),
        CheckConstraint(
            "astronomical_family IN ('quadrant', 'sign_based', 'ascendant_based')",
            name="chk_astral_house_systems_astronomical_family",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    astronomical_family: Mapped[str] = mapped_column(String(50), nullable=False)
    supports_polar_regions: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_quadrant_based: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_precise_birth_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)


class AstralAnglePointModel(Base):
    """Angle astrologique majeur utilisé comme point structurel du thème."""

    __tablename__ = "astral_angle_points"
    __table_args__ = (
        UniqueConstraint("code"),
        CheckConstraint(
            "axis IN ('horizontal', 'vertical')",
            name="ck_astral_angle_points_axis",
        ),
        CheckConstraint(
            "associated_house BETWEEN 1 AND 12",
            name="ck_astral_angle_points_associated_house",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    short_label: Mapped[str] = mapped_column(String(16), nullable=False)
    full_name: Mapped[str] = mapped_column(String(64), nullable=False)
    axis: Mapped[str] = mapped_column(String(16), nullable=False)
    opposite_angle_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    associated_house: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class AstralAstrologicalRoleModel(Base):
    """Rôle interprétatif stable d'un objet astrologique."""

    __tablename__ = "astral_astrological_roles"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class AstralCalculationTypeModel(Base):
    """Mode d'obtention d'un objet astrologique par le moteur."""

    __tablename__ = "astral_calculation_types"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class AstralHouseModalityModel(Base):
    """Modalité structurelle d'une maison astrologique."""

    __tablename__ = "astral_house_modalities"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)


class AstralObjectTypeModel(Base):
    """Nature physique ou géométrique d'un objet astrologique."""

    __tablename__ = "astral_object_types"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class LanguageModel(Base):
    """Langue disponible pour les contenus localisés de l'application."""

    __tablename__ = "languages"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)


class AstralSignProfileModel(Base):
    """Profil structurel canonique d'un signe astrologique."""

    __tablename__ = "astral_sign_profiles"
    __table_args__ = (UniqueConstraint("astral_sign_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    astral_sign_id: Mapped[int] = mapped_column(
        ForeignKey("astral_signs.id"), nullable=False, index=True
    )
    astral_element_id: Mapped[int] = mapped_column(
        ForeignKey("astral_elements.id"), nullable=False, index=True
    )
    astral_modality_id: Mapped[int] = mapped_column(
        ForeignKey("astral_modalities.id"), nullable=False, index=True
    )
    astral_polarity_id: Mapped[int] = mapped_column(
        ForeignKey("astral_polarities.id"), nullable=False, index=True
    )
    keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    shadow_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    sign: Mapped["AstralSignModel"] = relationship()
    element: Mapped["AstralElementModel"] = relationship()
    modality: Mapped["AstralModalityModel"] = relationship()
    polarity: Mapped["AstralPolarityModel"] = relationship()


class HouseModel(Base):
    __tablename__ = "astral_houses"
    __table_args__ = (UniqueConstraint("number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(64))


class AspectModel(Base):
    """Aspect astrologique stable, relié à sa famille canonique."""

    __tablename__ = "astral_aspects"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))
    angle: Mapped[float] = mapped_column(Float)
    family: Mapped[int] = mapped_column(ForeignKey("astral_aspect_families.id"), nullable=False)

    aspect_family: Mapped["AstralAspectFamilyModel"] = relationship()


def _ensure_reference_version_is_mutable(target: object) -> None:
    session = object_session(target)
    if session is None or not isinstance(session, Session):
        return
    reference_version_id = getattr(target, "reference_version_id", None)
    if reference_version_id is None:
        return
    version = session.get(ReferenceVersionModel, reference_version_id)
    if version is not None and version.is_locked:
        raise ValueError("reference version is immutable")
