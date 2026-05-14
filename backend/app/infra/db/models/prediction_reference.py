"""Modèles SQLAlchemy des paramètres versionnés du moteur de prédiction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base
from app.infra.db.models.reference import _ensure_reference_version_is_mutable

if TYPE_CHECKING:
    from app.infra.db.models.reference import (
        AspectModel,
        AstralDignityTypeModel,
        AstralSignModel,
        AstralSystemModel,
        HouseModel,
        PlanetModel,
        ReferenceVersionModel,
    )


class PredictionCategoryModel(Base):
    __tablename__ = "prediction_categories"
    __table_args__ = (UniqueConstraint("reference_version_id", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()


class PlanetProfileModel(Base):
    __tablename__ = "astral_prediction_daily_planet_profiles"
    __table_args__ = (UniqueConstraint("reference_version_id", "planet_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    class_code: Mapped[str] = mapped_column(String(32), nullable=False)  # luminary, personal, etc.
    speed_rank: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    speed_class: Mapped[str] = mapped_column(String(16), nullable=False)  # fast, medium, slow
    weight_intraday: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    weight_day_climate: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    typical_polarity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    orb_active_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    orb_peak_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    planet: Mapped["PlanetModel"] = relationship()


class HouseProfileModel(Base):
    __tablename__ = "astral_prediction_daily_house_profiles"
    __table_args__ = (UniqueConstraint("reference_version_id", "house_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    house_id: Mapped[int] = mapped_column(
        ForeignKey("astral_houses.id"), nullable=False, index=True
    )
    # values: angular, succedent, cadent
    house_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    visibility_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    base_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    house: Mapped["HouseModel"] = relationship()


class PlanetCategoryWeightModel(Base):
    __tablename__ = "astral_planet_category_weights"
    __table_args__ = (UniqueConstraint("reference_version_id", "planet_id", "category_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id"), nullable=False, index=True
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    influence_role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="secondary"
    )  # primary, secondary, color

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    planet: Mapped["PlanetModel"] = relationship()
    category: Mapped["PredictionCategoryModel"] = relationship()


class HouseCategoryWeightModel(Base):
    __tablename__ = "astral_house_category_weights"
    __table_args__ = (UniqueConstraint("reference_version_id", "house_id", "category_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    house_id: Mapped[int] = mapped_column(
        ForeignKey("astral_houses.id"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id"), nullable=False, index=True
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    routing_role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="secondary"
    )  # primary, secondary

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    house: Mapped["HouseModel"] = relationship()
    category: Mapped["PredictionCategoryModel"] = relationship()


class AstroPointModel(Base):
    __tablename__ = "astro_points"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)  # asc, dsc, mc, ic
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    point_type: Mapped[str] = mapped_column(String(32), nullable=False, default="angle")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class PointCategoryWeightModel(Base):
    __tablename__ = "point_category_weights"
    __table_args__ = (UniqueConstraint("reference_version_id", "point_id", "category_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    point_id: Mapped[int] = mapped_column(ForeignKey("astro_points.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id"), nullable=False, index=True
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    point: Mapped["AstroPointModel"] = relationship()
    category: Mapped["PredictionCategoryModel"] = relationship()


class AstralPlanetSignDignityModel(Base):
    """Dignité canonique d'une planète dans un signe pour un système donné."""

    __tablename__ = "astral_planet_sign_dignities"
    __table_args__ = (
        UniqueConstraint(
            "astral_sign_id",
            "astral_planet_id",
            "astral_dignity_type_id",
            "astral_system_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    astral_sign_id: Mapped[int] = mapped_column(
        ForeignKey("astral_signs.id"), nullable=False, index=True
    )
    astral_planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    astral_dignity_type_id: Mapped[int] = mapped_column(
        ForeignKey("astral_dignity_type.id"), nullable=False, index=True
    )
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"), nullable=False, index=True
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    sign: Mapped["AstralSignModel"] = relationship()
    planet: Mapped["PlanetModel"] = relationship()
    dignity_type: Mapped["AstralDignityTypeModel"] = relationship()
    system: Mapped["AstralSystemModel"] = relationship()


class AspectProfileModel(Base):
    """Profil de scoring et de polarité associé à un aspect."""

    __tablename__ = "astral_aspect_profiles"
    __table_args__ = (UniqueConstraint("reference_version_id", "aspect_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    aspect_id: Mapped[int] = mapped_column(
        ForeignKey("astral_aspects.id"), nullable=False, index=True
    )
    intensity_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    default_valence: Mapped[str] = mapped_column(String(16), nullable=False, default="contextual")
    interpretive_valence: Mapped[str] = mapped_column(String(64), nullable=False)
    polarity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    energy_type: Mapped[str] = mapped_column(String(64), nullable=False)
    orb_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    phase_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    phase_behavior_json: Mapped[str] = mapped_column(Text, nullable=False)
    strength_thresholds_json: Mapped[str] = mapped_column(Text, nullable=False)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    aspect: Mapped["AspectModel"] = relationship()


class AstralAspectDefinitionModel(Base):
    """Configuration d'activation d'un aspect pour un système astrologique."""

    __tablename__ = "astral_aspect_definitions"
    __table_args__ = (UniqueConstraint("reference_version_id", "aspect_id", "astral_system_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"),
        nullable=False,
        index=True,
    )
    aspect_id: Mapped[int] = mapped_column(
        ForeignKey("astral_aspects.id"), nullable=False, index=True
    )
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"), nullable=False, index=True
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_major: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_minor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_orb_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    display_priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interpretation_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    scoring_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    aspect: Mapped["AspectModel"] = relationship()
    astral_system: Mapped["AstralSystemModel"] = relationship()


class AstralDefaultValenceModel(Base):
    """Référentiel des valences par défaut autorisées pour les aspects."""

    __tablename__ = "astral_default_valence"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class AstralInterpretiveValenceModel(Base):
    """Référentiel des valences interprétatives principales."""

    __tablename__ = "astral_interpretive_valence"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)


# Mechanisms for version protection
@event.listens_for(PredictionCategoryModel, "before_update")
@event.listens_for(PlanetProfileModel, "before_update")
@event.listens_for(HouseProfileModel, "before_update")
@event.listens_for(PlanetCategoryWeightModel, "before_update")
@event.listens_for(HouseCategoryWeightModel, "before_update")
@event.listens_for(PointCategoryWeightModel, "before_update")
@event.listens_for(AspectProfileModel, "before_update")
@event.listens_for(AstralAspectDefinitionModel, "before_update")
def _prevent_update_on_locked_prediction_version(
    mapper: object, connection: object, target: object
) -> None:
    del mapper, connection
    _ensure_reference_version_is_mutable(target)
