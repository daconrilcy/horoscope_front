from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
from app.infra.db.repositories.prediction_schemas import (
    AspectProfileData,
    AstroPointData,
    CalibrationData,
    CategoryData,
    EventTypeData,
    HouseCategoryWeightData,
    HouseProfileData,
    PlanetCategoryWeightData,
    PlanetProfileData,
    PointCategoryWeightData,
    PredictionContext,
    RulesetContext,
    RulesetData,
)
from app.prediction.exceptions import PredictionContextError


@dataclass(frozen=True)
class LoadedPredictionContext:
    """Complete and validated prediction context loaded from DB."""

    prediction_context: PredictionContext
    ruleset_context: RulesetContext
    calibrations: Mapping[str, CalibrationData | None]
    is_provisional_calibration: bool


class PredictionContextLoader:
    """Service to load and validate the complete prediction reference context."""

    def load(
        self,
        db: Session,
        reference_version: str,
        ruleset_version: str,
        reference_date: date | None = None,
    ) -> LoadedPredictionContext:
        """
        Loads the complete prediction context for a given reference and ruleset version.

        Args:
            db: SQLAlchemy session.
            reference_version: Name of the reference version (e.g., 'V1').
            ruleset_version: Name of the ruleset version (e.g., 'V1').
            reference_date: Date for calibration lookup. Defaults to today.

        Returns:
            LoadedPredictionContext: The fully loaded and validated context.

        Raises:
            PredictionContextError: If a version is missing, if there's a mismatch,
                                   or if required components are empty.
        """
        if reference_date is None:
            reference_date = date.today()

        # 1. Resolve reference_version_id
        rv_model = db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == reference_version)
        )
        if rv_model is None:
            raise PredictionContextError(f"Reference version '{reference_version}' not found")
        ref_id = rv_model.id

        ref_repo = PredictionReferenceRepository(db)
        ruleset_repo = PredictionRulesetRepository(db)
        try:
            pred_ctx = ref_repo.load_prediction_context(ref_id)
            ruleset_ctx = ruleset_repo.get_active_ruleset_context(ruleset_version)
        except ValueError as exc:
            raise PredictionContextError(f"Failed to load prediction context: {exc}") from exc

        if ruleset_ctx is None:
            raise PredictionContextError(f"Ruleset version '{ruleset_version}' not found")

        if ruleset_ctx.ruleset.reference_version_id != ref_id:
            raise PredictionContextError(
                f"Version mismatch: Ruleset '{ruleset_version}' is linked to "
                f"reference_version_id {ruleset_ctx.ruleset.reference_version_id}, "
                f"but '{reference_version}' (ID {ref_id}) was requested."
            )

        self._validate_context(pred_ctx, ruleset_ctx)
        self._validate_reference_categories(pred_ctx, ref_repo, ref_id, reference_version)

        calibrations: dict[str, CalibrationData | None] = {}
        is_provisional = False
        for category in pred_ctx.categories:
            try:
                calib = ruleset_repo.get_calibrations(
                    ruleset_ctx.ruleset.id, category.id, reference_date
                )
            except ValueError as exc:
                raise PredictionContextError(
                    f"Failed to load prediction calibrations: {exc}"
                ) from exc
            calibrations[category.code] = calib
            if calib is None:
                is_provisional = True

        frozen_pred_ctx = self._freeze_prediction_context(pred_ctx)
        frozen_ruleset_ctx = self._freeze_ruleset_context(ruleset_ctx)

        return LoadedPredictionContext(
            prediction_context=frozen_pred_ctx,
            ruleset_context=frozen_ruleset_ctx,
            calibrations=MappingProxyType(dict(calibrations)),
            is_provisional_calibration=is_provisional,
        )

    def _validate_context(self, pred_ctx: PredictionContext, ruleset_ctx: RulesetContext) -> None:
        """Validates that mandatory components are present."""
        if not pred_ctx.categories:
            raise PredictionContextError("Prediction context has no enabled categories")

        if not pred_ctx.planet_profiles:
            raise PredictionContextError("Prediction context has no planet profiles")

        if not pred_ctx.house_profiles:
            raise PredictionContextError("Prediction context has no house profiles")

        if not ruleset_ctx.parameters:
            raise PredictionContextError("Ruleset context has no parameters")

    def _validate_reference_categories(
        self,
        pred_ctx: PredictionContext,
        ref_repo: PredictionReferenceRepository,
        ref_id: int,
        reference_version: str,
    ) -> None:
        expected_categories = ref_repo.get_categories(ref_id)
        expected_ids = {category.id for category in expected_categories}
        loaded_ids = {category.id for category in pred_ctx.categories}
        if loaded_ids != expected_ids:
            raise PredictionContextError(
                "Prediction context categories do not match the requested "
                f"reference version '{reference_version}'"
            )

    def _freeze_prediction_context(self, pred_ctx: PredictionContext) -> PredictionContext:
        return PredictionContext(
            categories=tuple(self._freeze_category(category) for category in pred_ctx.categories),
            planet_profiles=MappingProxyType(
                {
                    code: self._freeze_planet_profile(profile)
                    for code, profile in pred_ctx.planet_profiles.items()
                }
            ),
            house_profiles=MappingProxyType(
                {
                    number: self._freeze_house_profile(profile)
                    for number, profile in pred_ctx.house_profiles.items()
                }
            ),
            planet_category_weights=tuple(
                self._freeze_planet_category_weight(weight)
                for weight in pred_ctx.planet_category_weights
            ),
            house_category_weights=tuple(
                self._freeze_house_category_weight(weight)
                for weight in pred_ctx.house_category_weights
            ),
            sign_rulerships=MappingProxyType(dict(pred_ctx.sign_rulerships)),
            aspect_profiles=MappingProxyType(
                {
                    code: self._freeze_aspect_profile(profile)
                    for code, profile in pred_ctx.aspect_profiles.items()
                }
            ),
            astro_points=MappingProxyType(
                {
                    code: self._freeze_astro_point(point)
                    for code, point in pred_ctx.astro_points.items()
                }
            ),
            point_category_weights=tuple(
                self._freeze_point_category_weight(weight)
                for weight in pred_ctx.point_category_weights
            ),
        )

    def _freeze_ruleset_context(self, ruleset_ctx: RulesetContext) -> RulesetContext:
        return RulesetContext(
            ruleset=self._freeze_ruleset(ruleset_ctx.ruleset),
            parameters=MappingProxyType(dict(ruleset_ctx.parameters)),
            event_types=MappingProxyType(
                {
                    code: self._freeze_event_type(event_type)
                    for code, event_type in ruleset_ctx.event_types.items()
                }
            ),
        )

    def _freeze_category(self, category: CategoryData) -> CategoryData:
        return CategoryData(
            id=category.id,
            code=category.code,
            name=category.name,
            display_name=category.display_name,
            sort_order=category.sort_order,
            is_enabled=category.is_enabled,
        )

    def _freeze_planet_profile(self, profile: PlanetProfileData) -> PlanetProfileData:
        return PlanetProfileData(
            planet_id=profile.planet_id,
            code=profile.code,
            name=profile.name,
            class_code=profile.class_code,
            speed_rank=profile.speed_rank,
            speed_class=profile.speed_class,
            weight_intraday=profile.weight_intraday,
            weight_day_climate=profile.weight_day_climate,
            typical_polarity=profile.typical_polarity,
            orb_active_deg=profile.orb_active_deg,
            orb_peak_deg=profile.orb_peak_deg,
            keywords=tuple(profile.keywords),
        )

    def _freeze_house_profile(self, profile: HouseProfileData) -> HouseProfileData:
        return HouseProfileData(
            house_id=profile.house_id,
            number=profile.number,
            name=profile.name,
            house_kind=profile.house_kind,
            visibility_weight=profile.visibility_weight,
            base_priority=profile.base_priority,
            keywords=tuple(profile.keywords),
        )

    def _freeze_planet_category_weight(
        self, weight: PlanetCategoryWeightData
    ) -> PlanetCategoryWeightData:
        return PlanetCategoryWeightData(
            planet_id=weight.planet_id,
            planet_code=weight.planet_code,
            category_id=weight.category_id,
            category_code=weight.category_code,
            weight=weight.weight,
            influence_role=weight.influence_role,
        )

    def _freeze_house_category_weight(
        self, weight: HouseCategoryWeightData
    ) -> HouseCategoryWeightData:
        return HouseCategoryWeightData(
            house_id=weight.house_id,
            house_number=weight.house_number,
            category_id=weight.category_id,
            category_code=weight.category_code,
            weight=weight.weight,
            routing_role=weight.routing_role,
        )

    def _freeze_aspect_profile(self, profile: AspectProfileData) -> AspectProfileData:
        return AspectProfileData(
            aspect_id=profile.aspect_id,
            code=profile.code,
            intensity_weight=profile.intensity_weight,
            default_valence=profile.default_valence,
            orb_multiplier=profile.orb_multiplier,
            phase_sensitive=profile.phase_sensitive,
        )

    def _freeze_astro_point(self, point: AstroPointData) -> AstroPointData:
        return AstroPointData(
            point_id=point.point_id,
            code=point.code,
            name=point.name,
            point_type=point.point_type,
        )

    def _freeze_point_category_weight(
        self, weight: PointCategoryWeightData
    ) -> PointCategoryWeightData:
        return PointCategoryWeightData(
            point_id=weight.point_id,
            point_code=weight.point_code,
            category_id=weight.category_id,
            category_code=weight.category_code,
            weight=weight.weight,
        )

    def _freeze_ruleset(self, ruleset: RulesetData) -> RulesetData:
        return RulesetData(
            id=ruleset.id,
            version=ruleset.version,
            reference_version_id=ruleset.reference_version_id,
            zodiac_type=ruleset.zodiac_type,
            coordinate_mode=ruleset.coordinate_mode,
            house_system=ruleset.house_system,
            time_step_minutes=ruleset.time_step_minutes,
            is_locked=ruleset.is_locked,
        )

    def _freeze_event_type(self, event_type: EventTypeData) -> EventTypeData:
        return EventTypeData(
            id=event_type.id,
            code=event_type.code,
            name=event_type.name,
            event_group=event_type.event_group,
            priority=event_type.priority,
            base_weight=event_type.base_weight,
        )
