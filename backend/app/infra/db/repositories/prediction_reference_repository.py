"""Repository SQLAlchemy pour le contexte de prédiction astrologique."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.prediction_reference import (
    AspectProfileModel,
    AstralPlanetSignDignityModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstralDignityTypeModel,
    AstralSignModel,
    AstralSystemModel,
    HouseModel,
    PlanetModel,
)
from app.infra.db.repositories.prediction_schemas import (
    AspectProfileData,
    AstroPointData,
    CategoryData,
    HouseAstrologyProfile,
    HouseCategoryWeightData,
    HousePredictionProfile,
    PlanetCategoryWeightData,
    PlanetProfileData,
    PlanetSignDignityData,
    PointCategoryWeightData,
    PredictionContext,
)


class PredictionReferenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_categories(self, reference_version_id: int) -> tuple[CategoryData, ...]:
        rows = (
            self.db.execute(
                select(PredictionCategoryModel)
                .where(
                    PredictionCategoryModel.reference_version_id == reference_version_id,
                    PredictionCategoryModel.is_enabled.is_(True),
                )
                .order_by(PredictionCategoryModel.sort_order)
            )
            .scalars()
            .all()
        )

        return tuple(
            CategoryData(
                id=row.id,
                code=row.code,
                name=row.name,
                display_name=row.display_name,
                sort_order=row.sort_order,
                is_enabled=row.is_enabled,
            )
            for row in rows
        )

    def get_planet_profiles(self, reference_version_id: int) -> dict[str, PlanetProfileData]:
        rows = self.db.execute(
            select(PlanetModel, PlanetProfileModel)
            .join(PlanetProfileModel, PlanetModel.id == PlanetProfileModel.planet_id)
            .where(PlanetProfileModel.reference_version_id == reference_version_id)
        ).all()

        result = {}
        for planet_row, profile_row in rows:
            result[planet_row.code] = PlanetProfileData(
                planet_id=planet_row.id,
                code=planet_row.code,
                name=planet_row.name,
                class_code=profile_row.class_code,
                speed_rank=profile_row.speed_rank,
                speed_class=profile_row.speed_class,
                weight_intraday=profile_row.weight_intraday,
                weight_day_climate=profile_row.weight_day_climate,
                typical_polarity=profile_row.typical_polarity,
                orb_active_deg=profile_row.orb_active_deg,
                orb_peak_deg=profile_row.orb_peak_deg,
                keywords=self._parse_keywords(profile_row.keywords_json),
            )
        return result

    def get_house_profiles(
        self, reference_version_id: int
    ) -> tuple[dict[int, HouseAstrologyProfile], dict[int, HousePredictionProfile]]:
        """Charge les profils maison scindes entre astrologie et produit."""
        rows = self.db.execute(
            select(HouseModel, HouseProfileModel)
            .join(HouseProfileModel, HouseModel.id == HouseProfileModel.house_id)
            .where(HouseProfileModel.reference_version_id == reference_version_id)
        ).all()

        astrology_profiles: dict[int, HouseAstrologyProfile] = {}
        prediction_profiles: dict[int, HousePredictionProfile] = {}
        for house_row, profile_row in rows:
            astrology_profiles[house_row.number] = HouseAstrologyProfile(
                house_id=house_row.id,
                house_number=house_row.number,
                name=house_row.name,
                house_kind=profile_row.house_kind,
            )
            prediction_profiles[house_row.number] = HousePredictionProfile(
                house_id=house_row.id,
                house_number=house_row.number,
                name=house_row.name,
                visibility_weight=profile_row.visibility_weight,
                base_priority=profile_row.base_priority,
                keywords=self._parse_keywords(profile_row.keywords_json),
                micro_note=profile_row.micro_note,
            )
        return astrology_profiles, prediction_profiles

    def get_planet_category_weights(
        self, reference_version_id: int
    ) -> tuple[PlanetCategoryWeightData, ...]:
        rows = self.db.execute(
            select(
                PlanetCategoryWeightModel.planet_id,
                PlanetModel.code.label("planet_code"),
                PlanetCategoryWeightModel.category_id,
                PredictionCategoryModel.code.label("category_code"),
                PlanetCategoryWeightModel.weight,
                PlanetCategoryWeightModel.influence_role,
            )
            .join(PlanetModel, PlanetCategoryWeightModel.planet_id == PlanetModel.id)
            .join(
                PredictionCategoryModel,
                PlanetCategoryWeightModel.category_id == PredictionCategoryModel.id,
            )
            .where(
                PlanetCategoryWeightModel.reference_version_id == reference_version_id,
                PredictionCategoryModel.reference_version_id == reference_version_id,
            )
            .order_by(PlanetModel.code, PredictionCategoryModel.code)
        ).all()

        return tuple(
            PlanetCategoryWeightData(
                planet_id=row.planet_id,
                planet_code=row.planet_code,
                category_id=row.category_id,
                category_code=row.category_code,
                weight=row.weight,
                influence_role=row.influence_role,
            )
            for row in rows
        )

    def get_house_category_weights(
        self, reference_version_id: int
    ) -> tuple[HouseCategoryWeightData, ...]:
        rows = self.db.execute(
            select(
                HouseCategoryWeightModel.house_id,
                HouseModel.number.label("house_number"),
                HouseCategoryWeightModel.category_id,
                PredictionCategoryModel.code.label("category_code"),
                HouseCategoryWeightModel.weight,
                HouseCategoryWeightModel.routing_role,
            )
            .join(HouseModel, HouseCategoryWeightModel.house_id == HouseModel.id)
            .join(
                PredictionCategoryModel,
                HouseCategoryWeightModel.category_id == PredictionCategoryModel.id,
            )
            .where(
                HouseCategoryWeightModel.reference_version_id == reference_version_id,
                PredictionCategoryModel.reference_version_id == reference_version_id,
            )
            .order_by(HouseModel.number, PredictionCategoryModel.code)
        ).all()

        return tuple(
            HouseCategoryWeightData(
                house_id=row.house_id,
                house_number=row.house_number,
                category_id=row.category_id,
                category_code=row.category_code,
                weight=row.weight,
                routing_role=row.routing_role,
            )
            for row in rows
        )

    def get_sign_rulerships(self, system: str = "traditional") -> dict[str, str]:
        """Retourne la vue métier signe -> maître depuis les dignités canoniques."""
        return self.get_sign_rulerships_from_dignities(system=system)

    def get_planet_sign_dignities(
        self, system: str = "traditional"
    ) -> tuple[PlanetSignDignityData, ...]:
        """Charge les dignités planétaires normalisées pour un système astrologique."""
        rows = self.db.execute(
            select(
                AstralSignModel.code.label("sign_code"),
                PlanetModel.code.label("planet_code"),
                AstralDignityTypeModel.code.label("dignity_type"),
                AstralSystemModel.name.label("system"),
                AstralPlanetSignDignityModel.weight.label("weight"),
                AstralPlanetSignDignityModel.is_primary.label("is_primary"),
            )
            .join(
                AstralPlanetSignDignityModel,
                AstralSignModel.id == AstralPlanetSignDignityModel.astral_sign_id,
            )
            .join(PlanetModel, AstralPlanetSignDignityModel.astral_planet_id == PlanetModel.id)
            .join(
                AstralDignityTypeModel,
                AstralPlanetSignDignityModel.astral_dignity_type_id == AstralDignityTypeModel.id,
            )
            .join(
                AstralSystemModel,
                AstralPlanetSignDignityModel.astral_system_id == AstralSystemModel.id,
            )
            .where(
                AstralSystemModel.name == system,
            )
            .order_by(AstralSignModel.id, PlanetModel.id, AstralDignityTypeModel.code)
        ).all()

        return tuple(
            PlanetSignDignityData(
                sign_code=row.sign_code,
                planet_code=row.planet_code,
                dignity_type=row.dignity_type,
                system=row.system,
                weight=row.weight,
                is_primary=row.is_primary,
            )
            for row in rows
        )

    def get_sign_rulerships_from_dignities(self, system: str = "traditional") -> dict[str, str]:
        """Filtre les domiciles primaires pour exposer le mapping signe -> maître."""
        return {
            row.sign_code: row.planet_code
            for row in self.get_planet_sign_dignities(system=system)
            if row.dignity_type == "domicile" and row.is_primary
        }

    def get_aspect_profiles(self, reference_version_id: int) -> dict[str, AspectProfileData]:
        rows = self.db.execute(
            select(AspectModel, AspectProfileModel)
            .join(AspectProfileModel, AspectModel.id == AspectProfileModel.aspect_id)
            .where(AspectProfileModel.reference_version_id == reference_version_id)
        ).all()

        result = {}
        for aspect_row, profile_row in rows:
            result[aspect_row.code] = AspectProfileData(
                aspect_id=aspect_row.id,
                code=aspect_row.code,
                intensity_weight=profile_row.intensity_weight,
                default_valence=profile_row.default_valence,
                orb_multiplier=profile_row.orb_multiplier,
                phase_sensitive=profile_row.phase_sensitive,
            )
        return result

    def get_astro_points(self, reference_version_id: int) -> dict[str, AstroPointData]:
        rows = (
            self.db.execute(
                select(AstroPointModel).where(
                    AstroPointModel.is_enabled.is_(True),
                )
            )
            .scalars()
            .all()
        )

        return {
            row.code: AstroPointData(
                point_id=row.id,
                code=row.code,
                name=row.name,
                point_type=row.point_type,
            )
            for row in rows
        }

    def get_point_category_weights(
        self, reference_version_id: int
    ) -> tuple[PointCategoryWeightData, ...]:
        rows = self.db.execute(
            select(
                PointCategoryWeightModel.point_id,
                AstroPointModel.code.label("point_code"),
                PointCategoryWeightModel.category_id,
                PredictionCategoryModel.code.label("category_code"),
                PointCategoryWeightModel.weight,
            )
            .join(AstroPointModel, PointCategoryWeightModel.point_id == AstroPointModel.id)
            .join(
                PredictionCategoryModel,
                PointCategoryWeightModel.category_id == PredictionCategoryModel.id,
            )
            .where(
                PointCategoryWeightModel.reference_version_id == reference_version_id,
                PredictionCategoryModel.reference_version_id == reference_version_id,
            )
            .order_by(AstroPointModel.code, PredictionCategoryModel.code)
        ).all()

        return tuple(
            PointCategoryWeightData(
                point_id=row.point_id,
                point_code=row.point_code,
                category_id=row.category_id,
                category_code=row.category_code,
                weight=row.weight,
            )
            for row in rows
        )

    def load_prediction_context(self, reference_version_id: int) -> PredictionContext:
        house_astrology_profiles, house_prediction_profiles = self.get_house_profiles(
            reference_version_id
        )
        return PredictionContext(
            categories=self.get_categories(reference_version_id),
            planet_profiles=self.get_planet_profiles(reference_version_id),
            house_astrology_profiles=house_astrology_profiles,
            house_prediction_profiles=house_prediction_profiles,
            planet_category_weights=self.get_planet_category_weights(reference_version_id),
            house_category_weights=self.get_house_category_weights(reference_version_id),
            sign_rulerships=self.get_sign_rulerships(),
            aspect_profiles=self.get_aspect_profiles(reference_version_id),
            astro_points=self.get_astro_points(reference_version_id),
            point_category_weights=self.get_point_category_weights(reference_version_id),
        )

    def _parse_keywords(self, raw: str | None) -> tuple[str, ...]:
        if not raw:
            return ()
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return tuple(str(k) for k in parsed)
        except (json.JSONDecodeError, TypeError):
            pass
        return ()
