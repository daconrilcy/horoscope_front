"""Repository SQLAlchemy pour le contexte de prédiction astrologique."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.infra.db.models.prediction_reference import (
    AspectProfileModel,
    AstralAspectDefinitionModel,
    AstralAspectOrbRuleModel,
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
    AstralAnglePointModel,
    AstralAspectFamilyModel,
    AstralAstrologicalRoleModel,
    AstralDignityTypeModel,
    AstralFixedStarDefinitionModel,
    AstralFixedStarModel,
    AstralPlanetDefinitionModel,
    AstralSignModel,
    AstralSpeedModel,
    AstralSystemModel,
    AstralTypicalPolarityModel,
    HouseModel,
    PlanetModel,
)
from app.infra.db.repositories.prediction_schemas import (
    AnglePointData,
    AspectOrbRuleData,
    AspectProfileData,
    AstroPointData,
    CategoryData,
    FixedStarData,
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
            select(
                PlanetModel,
                PlanetProfileModel,
                AstralPlanetDefinitionModel,
                AstralAstrologicalRoleModel,
                AstralSpeedModel,
                AstralTypicalPolarityModel,
            )
            .join(PlanetProfileModel, PlanetModel.id == PlanetProfileModel.planet_id)
            .outerjoin(
                AstralPlanetDefinitionModel,
                PlanetModel.id == AstralPlanetDefinitionModel.planet_id,
            )
            .outerjoin(
                AstralAstrologicalRoleModel,
                AstralPlanetDefinitionModel.astrological_role_id == AstralAstrologicalRoleModel.id,
            )
            .outerjoin(
                AstralSpeedModel,
                AstralPlanetDefinitionModel.speed_class_id == AstralSpeedModel.id,
            )
            .outerjoin(
                AstralTypicalPolarityModel,
                AstralPlanetDefinitionModel.typical_polarity_id == AstralTypicalPolarityModel.id,
            )
            .where(
                PlanetProfileModel.reference_version_id == reference_version_id,
                PlanetProfileModel.is_enabled.is_(True),
            )
        ).all()

        result = {}
        for planet_row, profile_row, definition_row, role_row, speed_row, polarity_row in rows:
            if (
                definition_row is None
                or role_row is None
                or speed_row is None
                or polarity_row is None
            ):
                raise ValueError(
                    "incomplete planet reference definition for "
                    f"{planet_row.code} in reference version {reference_version_id}"
                )
            result[planet_row.code] = PlanetProfileData(
                planet_id=planet_row.id,
                code=planet_row.code,
                name=planet_row.name,
                class_code=self._runtime_planet_class(role_row.code),
                speed_rank=definition_row.speed_rank,
                speed_class=speed_row.name,
                weight_intraday=profile_row.weight_intraday,
                weight_day_climate=profile_row.weight_day_climate,
                daily_visibility_score=profile_row.daily_visibility_score,
                daily_emotional_impact_score=profile_row.daily_emotional_impact_score,
                daily_conscious_activation_score=profile_row.daily_conscious_activation_score,
                is_enabled=profile_row.is_enabled,
                is_planet=bool(definition_row.is_planet),
                micro_note=profile_row.micro_note,
                typical_polarity=polarity_row.name,
                orb_active_deg=None,
                orb_peak_deg=None,
                keywords=(),
            )
        return result

    def get_aspect_orb_rules(self, reference_version_id: int) -> tuple[AspectOrbRuleData, ...]:
        """Charge les règles d'orbes versionnées utilisées par le moteur daily."""
        SourcePlanetModel = aliased(PlanetModel)
        TargetPlanetModel = aliased(PlanetModel)
        rows = self.db.execute(
            select(
                AstralAspectOrbRuleModel,
                AspectModel.code.label("aspect_code"),
                AstralSystemModel.name.label("system_code"),
                SourcePlanetModel.code.label("source_planet_code"),
                TargetPlanetModel.code.label("target_planet_code"),
            )
            .join(AspectModel, AstralAspectOrbRuleModel.aspect_id == AspectModel.id)
            .join(
                AstralSystemModel,
                AstralAspectOrbRuleModel.astral_system_id == AstralSystemModel.id,
            )
            .outerjoin(
                SourcePlanetModel,
                AstralAspectOrbRuleModel.source_planet_id == SourcePlanetModel.id,
            )
            .outerjoin(
                TargetPlanetModel,
                AstralAspectOrbRuleModel.target_planet_id == TargetPlanetModel.id,
            )
            .where(
                AstralAspectOrbRuleModel.reference_version_id == reference_version_id,
                AstralAspectOrbRuleModel.is_enabled.is_(True),
            )
            .order_by(AstralAspectOrbRuleModel.priority.desc(), AspectModel.code)
        ).all()
        return tuple(
            AspectOrbRuleData(
                aspect_code=aspect_code,
                system_code=system_code,
                calculation_context=rule.calculation_context,
                source_body_type=rule.source_body_type,
                source_planet_code=source_planet_code,
                source_point_code=rule.source_point_code,
                target_body_type=rule.target_body_type,
                target_planet_code=target_planet_code,
                target_point_code=rule.target_point_code,
                orb_deg=rule.orb_deg,
                priority=rule.priority,
                is_enabled=rule.is_enabled,
            )
            for rule, aspect_code, system_code, source_planet_code, target_planet_code in rows
        )

    def get_aspect_system_inheritance(self) -> dict[str, str | None]:
        """Charge la chaîne d'héritage des systèmes astrologiques depuis la référence SQL."""
        ParentSystemModel = aliased(AstralSystemModel)
        rows = self.db.execute(
            select(
                AstralSystemModel.name.label("system_code"),
                ParentSystemModel.name.label("parent_system_code"),
            ).outerjoin(
                ParentSystemModel,
                AstralSystemModel.inherits_from_system_id == ParentSystemModel.id,
            )
        ).all()
        return {
            str(system_code).lower(): (
                None if parent_system_code is None else str(parent_system_code).lower()
            )
            for system_code, parent_system_code in rows
        }

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
            select(
                AspectModel,
                AspectProfileModel,
                AstralAspectFamilyModel.name.label("family"),
                AstralAspectDefinitionModel.default_orb_deg.label("default_orb_deg"),
            )
            .join(AspectProfileModel, AspectModel.id == AspectProfileModel.aspect_id)
            .join(AstralAspectFamilyModel, AspectModel.family == AstralAspectFamilyModel.id)
            .outerjoin(AstralSystemModel, AstralSystemModel.name == "modern")
            .outerjoin(
                AstralAspectDefinitionModel,
                (AstralAspectDefinitionModel.aspect_id == AspectModel.id)
                & (AstralAspectDefinitionModel.reference_version_id == reference_version_id)
                & (AstralAspectDefinitionModel.astral_system_id == AstralSystemModel.id),
            )
            .where(AspectProfileModel.reference_version_id == reference_version_id)
        ).all()

        result = {}
        for aspect_row, profile_row, family, default_orb_deg in rows:
            result[aspect_row.code] = AspectProfileData(
                aspect_id=aspect_row.id,
                code=aspect_row.code,
                intensity_weight=profile_row.intensity_weight,
                default_valence=profile_row.default_valence,
                interpretive_valence=profile_row.interpretive_valence,
                polarity_score=profile_row.polarity_score,
                energy_type=profile_row.energy_type,
                orb_multiplier=profile_row.orb_multiplier,
                phase_sensitive=profile_row.phase_sensitive,
                phase_behavior=self._parse_json_object(profile_row.phase_behavior_json),
                strength_thresholds=self._parse_json_object(profile_row.strength_thresholds_json),
                angle=float(aspect_row.angle),
                family_code=str(family),
                default_orb_deg=(None if default_orb_deg is None else float(default_orb_deg)),
            )
        return result

    def get_fixed_stars(self) -> tuple[FixedStarData, ...]:
        """Charge les étoiles fixes actives depuis les tables de référence."""
        rows = self.db.execute(
            select(AstralFixedStarModel, AstralFixedStarDefinitionModel)
            .join(
                AstralFixedStarDefinitionModel,
                AstralFixedStarModel.id == AstralFixedStarDefinitionModel.fixed_star_id,
            )
            .where(AstralFixedStarDefinitionModel.is_active.is_(True))
            .order_by(AstralFixedStarModel.key)
        ).all()
        return tuple(
            FixedStarData(
                key=star.key,
                display_name=star.display_name,
                ecliptic_longitude_deg=float(definition.ecliptic_longitude_deg),
            )
            for star, definition in rows
        )

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

    def get_angle_points(self) -> dict[str, AnglePointData]:
        """Charge les points angulaires stables depuis le référentiel astrologique."""
        rows = (
            self.db.execute(select(AstralAnglePointModel).order_by(AstralAnglePointModel.code))
            .scalars()
            .all()
        )
        return {
            row.code: AnglePointData(
                point_id=row.id,
                code=row.code,
                short_label=row.short_label,
                full_name=row.full_name,
                axis=row.axis,
                associated_house=row.associated_house,
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
            aspect_orb_rules=self.get_aspect_orb_rules(reference_version_id),
            aspect_system_inheritance=self.get_aspect_system_inheritance(),
            astro_points=self.get_astro_points(reference_version_id),
            point_category_weights=self.get_point_category_weights(reference_version_id),
            fixed_stars=self.get_fixed_stars(),
            angle_points=self.get_angle_points(),
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

    def _runtime_planet_class(self, role_code: str | None) -> str:
        """Convertit le rôle canonique en famille historique attendue par le moteur daily."""
        if role_code is None:
            return ""
        return role_code.removesuffix("_planet")

    def _parse_json_object(self, raw: str | None) -> dict[str, object]:
        """Convertit un objet JSON stocké en texte pour les profils d'aspects."""
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return {str(key): value for key, value in parsed.items()}
        except (json.JSONDecodeError, TypeError):
            pass
        return {}
