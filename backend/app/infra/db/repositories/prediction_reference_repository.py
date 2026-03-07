from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.prediction_reference import (
    AspectProfileModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
    SignRulershipModel,
)
from app.infra.db.models.reference import AspectModel, HouseModel, PlanetModel, SignModel
from app.infra.db.repositories.prediction_schemas import (
    AspectProfileData,
    AstroPointData,
    CategoryData,
    HouseCategoryWeightData,
    HouseProfileData,
    PlanetCategoryWeightData,
    PlanetProfileData,
    PointCategoryWeightData,
    PredictionContext,
)


class PredictionReferenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_categories(self, reference_version_id: int) -> list[CategoryData]:
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

        return [
            CategoryData(
                id=row.id,
                code=row.code,
                name=row.name,
                display_name=row.display_name,
                sort_order=row.sort_order,
                is_enabled=row.is_enabled,
            )
            for row in rows
        ]

    def get_planet_profiles(self, reference_version_id: int) -> dict[str, PlanetProfileData]:
        rows = self.db.execute(
            select(PlanetModel, PlanetProfileModel)
            .join(PlanetProfileModel, PlanetModel.id == PlanetProfileModel.planet_id)
            .where(PlanetModel.reference_version_id == reference_version_id)
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

    def get_house_profiles(self, reference_version_id: int) -> dict[int, HouseProfileData]:
        rows = self.db.execute(
            select(HouseModel, HouseProfileModel)
            .join(HouseProfileModel, HouseModel.id == HouseProfileModel.house_id)
            .where(HouseModel.reference_version_id == reference_version_id)
        ).all()

        result = {}
        for house_row, profile_row in rows:
            result[house_row.number] = HouseProfileData(
                house_id=house_row.id,
                number=house_row.number,
                name=house_row.name,
                house_kind=profile_row.house_kind,
                visibility_weight=profile_row.visibility_weight,
                base_priority=profile_row.base_priority,
                keywords=self._parse_keywords(profile_row.keywords_json),
            )
        return result

    def get_planet_category_weights(
        self, reference_version_id: int
    ) -> list[PlanetCategoryWeightData]:
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
            .where(PlanetModel.reference_version_id == reference_version_id)
            .order_by(PlanetModel.code, PredictionCategoryModel.code)
        ).all()

        return [
            PlanetCategoryWeightData(
                planet_id=row.planet_id,
                planet_code=row.planet_code,
                category_id=row.category_id,
                category_code=row.category_code,
                weight=row.weight,
                influence_role=row.influence_role,
            )
            for row in rows
        ]

    def get_house_category_weights(
        self, reference_version_id: int
    ) -> list[HouseCategoryWeightData]:
        rows = self.db.execute(
            select(
                HouseCategoryWeightModel.house_id,
                HouseModel.number.label("house_number"),
                HouseCategoryWeightModel.category_id,
                PredictionCategoryModel.code.label("category_code"),
                HouseCategoryWeightModel.weight,
                HouseCategoryWeightModel.routing_role.label(
                    "influence_role"
                ),  # DB col named routing_role; aliased to match planet_category_weights interface
            )
            .join(HouseModel, HouseCategoryWeightModel.house_id == HouseModel.id)
            .join(
                PredictionCategoryModel,
                HouseCategoryWeightModel.category_id == PredictionCategoryModel.id,
            )
            .where(HouseModel.reference_version_id == reference_version_id)
            .order_by(HouseModel.number, PredictionCategoryModel.code)
        ).all()

        return [
            HouseCategoryWeightData(
                house_id=row.house_id,
                house_number=row.house_number,
                category_id=row.category_id,
                category_code=row.category_code,
                weight=row.weight,
                influence_role=row.influence_role,
            )
            for row in rows
        ]

    def get_sign_rulerships(self, reference_version_id: int) -> dict[str, str]:
        rows = self.db.execute(
            select(SignModel.code.label("sign_code"), PlanetModel.code.label("planet_code"))
            .join(SignRulershipModel, SignModel.id == SignRulershipModel.sign_id)
            .join(PlanetModel, SignRulershipModel.planet_id == PlanetModel.id)
            .where(
                SignRulershipModel.reference_version_id == reference_version_id,
                SignRulershipModel.rulership_type == "domicile",
                SignRulershipModel.is_primary.is_(True),
            )
        ).all()

        return {row.sign_code: row.planet_code for row in rows}

    def get_aspect_profiles(self, reference_version_id: int) -> dict[str, AspectProfileData]:
        rows = self.db.execute(
            select(AspectModel, AspectProfileModel)
            .join(AspectProfileModel, AspectModel.id == AspectProfileModel.aspect_id)
            .where(AspectModel.reference_version_id == reference_version_id)
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
                    AstroPointModel.reference_version_id == reference_version_id,
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
    ) -> list[PointCategoryWeightData]:
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
            .where(AstroPointModel.reference_version_id == reference_version_id)
            .order_by(AstroPointModel.code, PredictionCategoryModel.code)
        ).all()

        return [
            PointCategoryWeightData(
                point_id=row.point_id,
                point_code=row.point_code,
                category_id=row.category_id,
                category_code=row.category_code,
                weight=row.weight,
            )
            for row in rows
        ]

    def load_prediction_context(self, reference_version_id: int) -> PredictionContext:
        return PredictionContext(
            categories=self.get_categories(reference_version_id),
            planet_profiles=self.get_planet_profiles(reference_version_id),
            house_profiles=self.get_house_profiles(reference_version_id),
            planet_category_weights=self.get_planet_category_weights(reference_version_id),
            house_category_weights=self.get_house_category_weights(reference_version_id),
            sign_rulerships=self.get_sign_rulerships(reference_version_id),
            aspect_profiles=self.get_aspect_profiles(reference_version_id),
            astro_points=self.get_astro_points(reference_version_id),
            point_category_weights=self.get_point_category_weights(reference_version_id),
        )

    def _parse_keywords(self, raw: str | None) -> list[str]:
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(k) for k in parsed]
        except (json.JSONDecodeError, TypeError):
            pass
        return []
