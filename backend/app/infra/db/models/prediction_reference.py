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
        HouseModel,
        PlanetModel,
        ReferenceVersionModel,
        SignModel,
    )


class PredictionCategoryModel(Base):
    __tablename__ = "prediction_categories"
    __table_args__ = (UniqueConstraint("reference_version_id", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
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
    __tablename__ = "planet_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("planets.id"), unique=True, nullable=False, index=True
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

    planet: Mapped["PlanetModel"] = relationship()


class HouseProfileModel(Base):
    __tablename__ = "house_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    house_id: Mapped[int] = mapped_column(
        ForeignKey("houses.id"), unique=True, nullable=False, index=True
    )
    # values: angular, succedent, cadent
    house_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    visibility_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    base_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    house: Mapped["HouseModel"] = relationship()


class PlanetCategoryWeightModel(Base):
    __tablename__ = "planet_category_weights"
    __table_args__ = (UniqueConstraint("planet_id", "category_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id"), nullable=False, index=True
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    influence_role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="secondary"
    )  # primary, secondary, color

    planet: Mapped["PlanetModel"] = relationship()
    category: Mapped["PredictionCategoryModel"] = relationship()


class HouseCategoryWeightModel(Base):
    __tablename__ = "house_category_weights"
    __table_args__ = (UniqueConstraint("house_id", "category_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    house_id: Mapped[int] = mapped_column(ForeignKey("houses.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id"), nullable=False, index=True
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    routing_role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="secondary"
    )  # primary, secondary

    house: Mapped["HouseModel"] = relationship()
    category: Mapped["PredictionCategoryModel"] = relationship()


class AstroPointModel(Base):
    __tablename__ = "astro_points"
    __table_args__ = (UniqueConstraint("reference_version_id", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)  # asc, dsc, mc, ic
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    point_type: Mapped[str] = mapped_column(String(32), nullable=False, default="angle")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()


class PointCategoryWeightModel(Base):
    __tablename__ = "point_category_weights"
    __table_args__ = (UniqueConstraint("point_id", "category_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    point_id: Mapped[int] = mapped_column(ForeignKey("astro_points.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id"), nullable=False, index=True
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)

    point: Mapped["AstroPointModel"] = relationship()
    category: Mapped["PredictionCategoryModel"] = relationship()


class SignRulershipModel(Base):
    __tablename__ = "sign_rulerships"
    __table_args__ = (
        UniqueConstraint("reference_version_id", "sign_id", "planet_id", "rulership_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
        index=True,
    )
    sign_id: Mapped[int] = mapped_column(ForeignKey("signs.id"), nullable=False, index=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), nullable=False, index=True)
    rulership_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="domicile"
    )  # domicile, exaltation, etc.
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    sign: Mapped["SignModel"] = relationship()
    planet: Mapped["PlanetModel"] = relationship()


class AspectProfileModel(Base):
    __tablename__ = "aspect_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aspect_id: Mapped[int] = mapped_column(
        ForeignKey("aspects.id"), unique=True, nullable=False, index=True
    )
    intensity_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    default_valence: Mapped[str] = mapped_column(
        String(16), nullable=False, default="contextual"
    )  # favorable, challenging, etc.
    orb_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    phase_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    aspect: Mapped["AspectModel"] = relationship()


# Mechanisms for version protection
@event.listens_for(PredictionCategoryModel, "before_update")
@event.listens_for(AstroPointModel, "before_update")
@event.listens_for(SignRulershipModel, "before_update")
def _prevent_update_on_locked_prediction_version(
    mapper: object, connection: object, target: object
) -> None:
    del mapper, connection
    _ensure_reference_version_is_mutable(target)
