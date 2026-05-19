"""Repository du referentiel astrologique runtime.

Le repository lit les models SQLAlchemy existants, appelle le mapper infra et
retourne un contrat domaine immutable complet pour le calcul natal.
"""

from __future__ import annotations

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.astrology.planet_catalog import planet_codes
from app.domain.astrology.runtime.runtime_reference import (
    AstralPointReferenceSet,
    AstrologyRuntimeReference,
)
from app.infra.db.models.dignity_reference import (
    AstralAccidentalDignityConditionSchemaModel,
    AstralAccidentalDignityRuleModel,
    AstralAccidentalDignityScoreWeightModel,
    AstralAccidentalDignityTypeModel,
    AstralConditionOperatorModel,
    AstralDecanSystemCodeModel,
    AstralDominanceFactorTypeModel,
    AstralDominanceScoreProfileModel,
    AstralDominanceScoreWeightModel,
    AstralEssentialDignityRuleModel,
    AstralEssentialDignityScoreWeightModel,
    AstralEssentialDignityTypeModel,
    AstralFaceDecanModel,
    AstralHeliacalConditionModel,
    AstralHorizonPositionModel,
    AstralPlanetConditionSignalProfileModel,
    AstralPlanetMotionStateModel,
    AstralPlanetNatureModel,
    AstralRulerAssignmentsRoleModel,
    AstralSectModel,
    AstralSignGenderModel,
    AstralSpeedRelationModel,
    AstralTermBoundModel,
    AstralTermSystemCodeModel,
    AstralTriplicityRulerAssignmentModel,
)
from app.infra.db.models.prediction_reference import AstralPlanetSignDignityModel
from app.infra.db.models.reference import (
    AstralAnglePointModel,
    AstralAstrologicalRoleModel,
    AstralElementModel,
    AstralHouseModalityModel,
    AstralHouseSystemModel,
    AstralModalityModel,
    AstralPlanetDefinitionModel,
    AstralPointAliasModel,
    AstralPointCalculationVariantModel,
    AstralPointModel,
    AstralPolarityModel,
    AstralSignModel,
    AstralSignProfileModel,
    AstralSystemModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.repositories.astrology_runtime_reference_mapper import (
    AstrologyRuntimeReferenceMapper,
)
from app.infra.db.repositories.dignity_reference_repository import DignityReferenceRepository
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
from app.infra.db.repositories.reference_repository import ReferenceRepository


class AstrologyRuntimeReferenceError(Exception):
    """Erreur bloquante de chargement ou d'integrite du referentiel runtime."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AstrologyRuntimeReferenceRepository:
    """Charge et valide la photographie runtime astrologique depuis la DB."""

    _REQUIRED_PLANETS = frozenset(planet_codes())
    _REQUIRED_ANGLE_POINTS = frozenset({"asc", "dsc", "mc", "ic"})
    _REQUIRED_HOUSE_SYSTEMS = frozenset({"placidus", "whole_sign", "equal", "porphyry"})
    _CONDITION_SIGNAL_AXES = frozenset(
        {
            "functional_strength",
            "intensity",
            "visibility",
            "stability",
            "coherence",
            "support",
            "constraint",
        }
    )
    _REQUIRED_FACTOR_CODES = frozenset(
        {
            "chart_ruler",
            "angularity",
            "condition_strength",
            "visibility",
            "most_elevated",
            "luminary_emphasis",
            "house_rulership_load",
            "aspect_centrality",
        }
    )

    def __init__(
        self,
        db: Session,
        mapper: AstrologyRuntimeReferenceMapper | None = None,
    ) -> None:
        self.db = db
        self.mapper = mapper or AstrologyRuntimeReferenceMapper()

    def load(self, version: str) -> AstrologyRuntimeReference:
        """Charge le referentiel complet pour la version demandee."""
        version_model = self.db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == version)
        )
        if version_model is None:
            raise AstrologyRuntimeReferenceError(
                code="reference_version_not_found",
                message="reference version not found",
                details={"version": version},
            )

        payload = ReferenceRepository(self.db).get_reference_data(version)
        payload["signs"] = list(self._load_sign_profiles())
        prediction_repo = PredictionReferenceRepository(self.db)
        try:
            runtime_reference = self.mapper.map_payload(
                reference_version_id=version_model.id,
                reference_version=version_model.version,
                payload=payload,
                dignities=self._load_dignities(),
                sign_rulerships=prediction_repo.get_sign_rulerships(),
                dignity_reference=self._load_dignity_reference(version_model.id),
                condition_signal_profiles=self._load_condition_signal_profiles(version_model.id),
                dominance_factor_types=self._load_dominance_factor_types(version_model.id),
                dominance_score_profiles=self._load_dominance_score_profiles(version_model.id),
                dominance_score_weights=self._load_dominance_score_weights(version_model.id),
                planet_definitions=self._load_planet_definitions(),
                angle_points=self._load_angle_points(),
                astral_points=self._load_astral_point_payload(),
                house_systems=self._load_house_systems(),
            )
        except ValueError as error:
            raise AstrologyRuntimeReferenceError(
                code="invalid_astrology_runtime_reference",
                message="astrology runtime reference is invalid",
                details={"field": "sign_profiles", "reason": str(error)},
            ) from error
        self._validate(runtime_reference)
        return runtime_reference

    def load_astral_points(self) -> AstralPointReferenceSet:
        """Charge uniquement les points astraux sous forme de contrats runtime typés."""
        try:
            return self.mapper.map_astral_points(self._load_astral_point_payload())
        except ValueError as error:
            raise AstrologyRuntimeReferenceError(
                code="invalid_astral_points_runtime_reference",
                message="astral point runtime reference is invalid",
                details={"field": "astral_points", "reason": str(error)},
            ) from error

    def _load_planet_definitions(self) -> dict[str, dict[str, object]]:
        """Charge les definitions structurelles des planetes."""
        rows = self.db.execute(
            select(
                PlanetModel.code,
                AstralAstrologicalRoleModel.code.label("body_class"),
                AstralPlanetDefinitionModel.is_luminary,
            )
            .join(
                AstralPlanetDefinitionModel,
                PlanetModel.id == AstralPlanetDefinitionModel.planet_id,
            )
            .join(
                AstralAstrologicalRoleModel,
                AstralPlanetDefinitionModel.astrological_role_id == AstralAstrologicalRoleModel.id,
            )
        ).all()
        return {
            row.code: {"body_class": row.body_class, "is_luminary": row.is_luminary} for row in rows
        }

    def _load_sign_profiles(self) -> tuple[dict[str, object], ...]:
        """Charge les signes avec profils structurels sans modifier le payload public."""
        rows = self.db.execute(
            select(
                AstralSignModel.code,
                AstralSignModel.name,
                AstralElementModel.code.label("element_code"),
                AstralModalityModel.code.label("modality_code"),
                AstralPolarityModel.code.label("polarity_code"),
            )
            .outerjoin(
                AstralSignProfileModel,
                AstralSignProfileModel.astral_sign_id == AstralSignModel.id,
            )
            .outerjoin(
                AstralElementModel,
                AstralSignProfileModel.astral_element_id == AstralElementModel.id,
            )
            .outerjoin(
                AstralModalityModel,
                AstralSignProfileModel.astral_modality_id == AstralModalityModel.id,
            )
            .outerjoin(
                AstralPolarityModel,
                AstralSignProfileModel.astral_polarity_id == AstralPolarityModel.id,
            )
            .order_by(AstralSignModel.id)
        ).all()
        return tuple(
            {
                "code": row.code,
                "name": row.name,
                "element": row.element_code,
                "modality": row.modality_code,
                "polarity": row.polarity_code,
            }
            for row in rows
        )

    def _load_dignities(self) -> tuple[dict[str, object], ...]:
        """Charge les dignites planetaires canoniques."""
        rows = self.db.execute(
            select(
                AstralPlanetSignDignityModel,
                PlanetModel.code.label("planet_code"),
                AstralSystemModel.name.label("system"),
            )
            .join(PlanetModel, AstralPlanetSignDignityModel.astral_planet_id == PlanetModel.id)
            .join(
                AstralSystemModel,
                AstralPlanetSignDignityModel.astral_system_id == AstralSystemModel.id,
            )
        ).all()
        result: list[Mapping[str, object]] = []
        for dignity, planet_code, system in rows:
            result.append(
                {
                    "sign_code": dignity.sign.code,
                    "planet_code": planet_code,
                    "dignity_type": dignity.dignity_type.code,
                    "system": system,
                    "weight": dignity.weight,
                    "is_primary": dignity.is_primary,
                }
            )
        return tuple(result)

    def _load_dignity_reference(self, reference_version_id: int) -> dict[str, object]:
        """Charge les referentiels avances de dignites sous forme normalisee."""
        return {
            "essential_types": self._load_dignity_types(AstralEssentialDignityTypeModel),
            "accidental_types": self._load_dignity_types(AstralAccidentalDignityTypeModel),
            "term_systems": self._load_dignity_systems(AstralTermSystemCodeModel),
            "decan_systems": self._load_dignity_systems(AstralDecanSystemCodeModel),
            "score_profiles": self._load_dignity_score_profiles(),
            "essential_weights": self._load_dignity_score_weights(
                AstralEssentialDignityScoreWeightModel,
                AstralEssentialDignityTypeModel,
                "essential_dignity_types_id",
            ),
            "accidental_weights": self._load_dignity_score_weights(
                AstralAccidentalDignityScoreWeightModel,
                AstralAccidentalDignityTypeModel,
                "accidental_dignity_type_id",
            ),
            "essential_rules": self._load_essential_dignity_rules(reference_version_id),
            "triplicity_rulers": self._load_triplicity_rulers(reference_version_id),
            "term_bounds": self._load_term_bounds(reference_version_id),
            "face_decans": self._load_face_decans(reference_version_id),
            "accidental_rules": self._load_accidental_dignity_rules(reference_version_id),
        }

    def _load_condition_signal_profiles(
        self, reference_version_id: int
    ) -> tuple[dict[str, object], ...]:
        """Charge les profils de signaux conditionnels versionnes."""
        rows = self.db.execute(
            select(
                AstralPlanetConditionSignalProfileModel.condition_axis,
                AstralPlanetConditionSignalProfileModel.level_min,
                AstralPlanetConditionSignalProfileModel.level_max,
                AstralPlanetConditionSignalProfileModel.signal_code,
                AstralPlanetConditionSignalProfileModel.signal_label,
                AstralPlanetConditionSignalProfileModel.signal_level,
                AstralPlanetConditionSignalProfileModel.interpretation_use,
                AstralPlanetConditionSignalProfileModel.priority_weight,
                AstralPlanetConditionSignalProfileModel.prompt_hint,
                ReferenceVersionModel.version.label("reference_version"),
            )
            .join(
                ReferenceVersionModel,
                AstralPlanetConditionSignalProfileModel.reference_version_id
                == ReferenceVersionModel.id,
            )
            .where(
                AstralPlanetConditionSignalProfileModel.reference_version_id == reference_version_id
            )
            .order_by(
                AstralPlanetConditionSignalProfileModel.priority_weight,
                AstralPlanetConditionSignalProfileModel.condition_axis,
                AstralPlanetConditionSignalProfileModel.signal_code,
            )
        ).all()
        return tuple(dict(row._mapping) for row in rows)

    def _load_dominance_factor_types(
        self, reference_version_id: int
    ) -> tuple[dict[str, object], ...]:
        """Charge les types de facteurs de dominance actifs et versionnes."""
        rows = self.db.execute(
            select(
                AstralDominanceFactorTypeModel.code,
                AstralDominanceFactorTypeModel.label,
                AstralDominanceFactorTypeModel.category,
                AstralDominanceFactorTypeModel.default_weight,
                AstralDominanceFactorTypeModel.sort_order,
                AstralDominanceFactorTypeModel.is_active,
                AstralDominanceFactorTypeModel.description,
                ReferenceVersionModel.version.label("reference_version"),
            )
            .join(
                ReferenceVersionModel,
                AstralDominanceFactorTypeModel.reference_version_id == ReferenceVersionModel.id,
            )
            .where(AstralDominanceFactorTypeModel.reference_version_id == reference_version_id)
            .where(AstralDominanceFactorTypeModel.is_active.is_(True))
            .order_by(AstralDominanceFactorTypeModel.sort_order)
        ).all()
        return tuple(dict(row._mapping) for row in rows)

    def _load_dominance_score_profiles(
        self, reference_version_id: int
    ) -> tuple[dict[str, object], ...]:
        """Charge les profils actifs de scoring de dominance."""
        rows = self.db.execute(
            select(
                AstralDominanceScoreProfileModel.code,
                AstralDominanceScoreProfileModel.label,
                AstralDominanceScoreProfileModel.tradition_code,
                AstralDominanceScoreProfileModel.description,
                AstralDominanceScoreProfileModel.reference_version_code,
                AstralDominanceScoreProfileModel.is_active,
            )
            .where(AstralDominanceScoreProfileModel.reference_version_id == reference_version_id)
            .where(AstralDominanceScoreProfileModel.is_active.is_(True))
            .order_by(AstralDominanceScoreProfileModel.code)
        ).all()
        return tuple(dict(row._mapping) for row in rows)

    def _load_dominance_score_weights(
        self, reference_version_id: int
    ) -> tuple[dict[str, object], ...]:
        """Charge les poids de dominance par profil et facteur."""
        rows = self.db.execute(
            select(
                AstralDominanceScoreProfileModel.code.label("score_profile_code"),
                AstralDominanceFactorTypeModel.code.label("factor_type_code"),
                AstralDominanceScoreWeightModel.weight,
                AstralDominanceScoreWeightModel.min_value,
                AstralDominanceScoreWeightModel.max_value,
                AstralDominanceScoreWeightModel.normalization_method,
                AstralDominanceScoreWeightModel.notes,
            )
            .join(
                AstralDominanceScoreProfileModel,
                AstralDominanceScoreWeightModel.score_profile_id
                == AstralDominanceScoreProfileModel.id,
            )
            .join(
                AstralDominanceFactorTypeModel,
                AstralDominanceScoreWeightModel.factor_type_id == AstralDominanceFactorTypeModel.id,
            )
            .where(AstralDominanceScoreProfileModel.reference_version_id == reference_version_id)
            .where(AstralDominanceFactorTypeModel.reference_version_id == reference_version_id)
            .order_by(
                AstralDominanceScoreProfileModel.code,
                AstralDominanceFactorTypeModel.sort_order,
            )
        ).all()
        return tuple(dict(row._mapping) for row in rows)

    def _load_dignity_types(
        self,
        model: type[AstralEssentialDignityTypeModel] | type[AstralAccidentalDignityTypeModel],
    ) -> tuple[dict[str, object], ...]:
        """Charge les types de dignites exposes au runtime."""
        rows = self.db.scalars(select(model).order_by(model.sort_order)).all()
        return tuple(
            {
                "code": row.code,
                "label": row.label,
                "description": row.description,
                "sort_order": row.sort_order,
            }
            for row in rows
        )

    def _load_dignity_systems(
        self,
        model: type[AstralTermSystemCodeModel] | type[AstralDecanSystemCodeModel],
    ) -> tuple[dict[str, object], ...]:
        """Charge les systemes de termes et de decans exposes au runtime."""
        rows = self.db.scalars(select(model).order_by(model.sort_order)).all()
        return tuple(
            {
                "code": row.code,
                "label": row.label,
                "description": row.description,
                "sort_order": row.sort_order,
            }
            for row in rows
        )

    def _load_dignity_score_profiles(self) -> tuple[dict[str, object], ...]:
        """Charge les profils de scoring et leur tradition."""
        return tuple(
            {
                "code": profile.code,
                "tradition": profile.astral_system.name,
                "is_default": profile.is_default,
            }
            for profile in DignityReferenceRepository(self.db).list_score_profiles()
        )

    def _load_dignity_score_weights(
        self,
        model: type[AstralEssentialDignityScoreWeightModel]
        | type[AstralAccidentalDignityScoreWeightModel],
        type_model: type[AstralEssentialDignityTypeModel] | type[AstralAccidentalDignityTypeModel],
        type_fk_name: str,
    ) -> dict[str, tuple[dict[str, object], ...]]:
        """Charge les poids de dignites groupes par profil de scoring."""
        repository = DignityReferenceRepository(self.db)
        grouped: dict[str, list[dict[str, object]]] = {}
        for profile in repository.list_score_profiles():
            rows = (
                repository.list_essential_score_weights(profile.code)
                if type_fk_name == "essential_dignity_types_id"
                else repository.list_accidental_score_weights(profile.code)
            )
            grouped[profile.code] = [
                {
                    "dignity_type_code": row.dignity_type_code,
                    "score_value": row.score_value,
                    "functional_weight": row.functional_weight,
                    "expression_weight": row.expression_weight,
                    "intensity_weight": row.intensity_weight,
                    "visibility_weight": row.visibility_weight,
                    "stability_weight": row.stability_weight,
                    "coherence_weight": row.coherence_weight,
                    "support_weight": row.support_weight,
                    "constraint_weight": row.constraint_weight,
                }
                for row in rows
            ]
        return {profile: tuple(weights) for profile, weights in grouped.items()}

    def _load_essential_dignity_rules(
        self, reference_version_id: int
    ) -> tuple[dict[str, object], ...]:
        """Charge les regles essentielles planetaire-signe."""
        rows = self.db.execute(
            select(
                PlanetModel.code.label("planet_code"),
                AstralSignModel.code.label("sign_code"),
                AstralEssentialDignityTypeModel.code.label("dignity_type_code"),
                AstralEssentialDignityRuleModel.degree_start,
                AstralEssentialDignityRuleModel.degree_end,
                AstralSystemModel.name.label("system_code"),
            )
            .select_from(AstralEssentialDignityRuleModel)
            .join(PlanetModel, AstralEssentialDignityRuleModel.planet_id == PlanetModel.id)
            .join(AstralSignModel, AstralEssentialDignityRuleModel.sign_id == AstralSignModel.id)
            .join(
                AstralEssentialDignityTypeModel,
                AstralEssentialDignityRuleModel.essential_dignity_types_id
                == AstralEssentialDignityTypeModel.id,
            )
            .join(
                AstralSystemModel,
                AstralEssentialDignityRuleModel.astral_system_id == AstralSystemModel.id,
            )
            .where(AstralEssentialDignityRuleModel.reference_version_id == reference_version_id)
            .order_by(AstralEssentialDignityTypeModel.sort_order)
        ).all()
        return tuple(dict(row._mapping) for row in rows)

    def _load_triplicity_rulers(self, reference_version_id: int) -> tuple[dict[str, object], ...]:
        """Charge les maitres de triplicite par element et secte."""
        rows = self.db.execute(
            select(
                AstralElementModel.code.label("element_code"),
                AstralSectModel.code.label("sect_code"),
                PlanetModel.code.label("planet_code"),
                AstralRulerAssignmentsRoleModel.code.label("role_code"),
                AstralSystemModel.name.label("system_code"),
            )
            .select_from(AstralTriplicityRulerAssignmentModel)
            .join(
                AstralElementModel,
                AstralTriplicityRulerAssignmentModel.element_id == AstralElementModel.id,
            )
            .join(
                AstralSectModel, AstralTriplicityRulerAssignmentModel.sect_id == AstralSectModel.id
            )
            .join(PlanetModel, AstralTriplicityRulerAssignmentModel.planet_id == PlanetModel.id)
            .join(
                AstralRulerAssignmentsRoleModel,
                AstralTriplicityRulerAssignmentModel.role_id == AstralRulerAssignmentsRoleModel.id,
            )
            .join(
                AstralSystemModel,
                AstralTriplicityRulerAssignmentModel.astral_system_id == AstralSystemModel.id,
            )
            .where(
                AstralTriplicityRulerAssignmentModel.reference_version_id == reference_version_id
            )
        ).all()
        return tuple(dict(row._mapping) for row in rows)

    def _load_term_bounds(self, reference_version_id: int) -> tuple[dict[str, object], ...]:
        """Charge les bornes de termes par signe."""
        rows = self.db.execute(
            select(
                AstralTermSystemCodeModel.code.label("term_system_code"),
                AstralSignModel.code.label("sign_code"),
                PlanetModel.code.label("planet_code"),
                AstralTermBoundModel.degree_start,
                AstralTermBoundModel.degree_end,
                AstralTermBoundModel.order_index,
            )
            .select_from(AstralTermBoundModel)
            .join(
                AstralTermSystemCodeModel,
                AstralTermBoundModel.term_system_id == AstralTermSystemCodeModel.id,
            )
            .join(AstralSignModel, AstralTermBoundModel.sign_id == AstralSignModel.id)
            .join(PlanetModel, AstralTermBoundModel.planet_id == PlanetModel.id)
            .where(AstralTermBoundModel.reference_version_id == reference_version_id)
            .order_by(AstralSignModel.id, AstralTermBoundModel.order_index)
        ).all()
        return tuple(dict(row._mapping) for row in rows)

    def _load_face_decans(self, reference_version_id: int) -> tuple[dict[str, object], ...]:
        """Charge les faces et decans par signe."""
        rows = self.db.execute(
            select(
                AstralDecanSystemCodeModel.code.label("decan_system_code"),
                AstralSignModel.code.label("sign_code"),
                PlanetModel.code.label("planet_code"),
                AstralFaceDecanModel.decan_index,
                AstralFaceDecanModel.degree_start,
                AstralFaceDecanModel.degree_end,
            )
            .select_from(AstralFaceDecanModel)
            .join(
                AstralDecanSystemCodeModel,
                AstralFaceDecanModel.decan_system_id == AstralDecanSystemCodeModel.id,
            )
            .join(AstralSignModel, AstralFaceDecanModel.sign_id == AstralSignModel.id)
            .join(PlanetModel, AstralFaceDecanModel.planet_id == PlanetModel.id)
            .where(AstralFaceDecanModel.reference_version_id == reference_version_id)
            .order_by(AstralSignModel.id, AstralFaceDecanModel.decan_index)
        ).all()
        return tuple(dict(row._mapping) for row in rows)

    def _load_accidental_dignity_rules(
        self, reference_version_id: int
    ) -> tuple[dict[str, object], ...]:
        """Charge les regles accidentelles avec conditions normalisees."""
        rows = self.db.execute(
            select(
                AstralAccidentalDignityRuleModel,
                AstralAccidentalDignityTypeModel.code.label("dignity_type_code"),
                PlanetModel.code.label("planet_code"),
                AstralAccidentalDignityConditionSchemaModel.code.label("condition_schema_code"),
                AstralSystemModel.name.label("system_code"),
            )
            .select_from(AstralAccidentalDignityRuleModel)
            .join(
                AstralAccidentalDignityTypeModel,
                AstralAccidentalDignityRuleModel.accidental_dignity_type_id
                == AstralAccidentalDignityTypeModel.id,
            )
            .outerjoin(PlanetModel, AstralAccidentalDignityRuleModel.planet_id == PlanetModel.id)
            .join(
                AstralAccidentalDignityConditionSchemaModel,
                AstralAccidentalDignityRuleModel.condition_schema_id
                == AstralAccidentalDignityConditionSchemaModel.id,
            )
            .join(
                AstralSystemModel,
                AstralAccidentalDignityRuleModel.astral_system_id == AstralSystemModel.id,
            )
            .where(AstralAccidentalDignityRuleModel.reference_version_id == reference_version_id)
            .order_by(AstralAccidentalDignityTypeModel.sort_order)
        ).all()
        id_maps = self._dignity_condition_id_maps()
        return tuple(
            {
                "dignity_type_code": dignity_type_code,
                "planet_code": planet_code,
                "condition_schema_code": condition_schema_code,
                "conditions": self._normalize_condition_json(rule.condition_json, id_maps),
                "system_code": system_code,
            }
            for rule, dignity_type_code, planet_code, condition_schema_code, system_code in rows
        )

    def _dignity_condition_id_maps(self) -> dict[str, dict[int, str | int]]:
        """Construit les correspondances d'ids DB vers codes stables de condition."""
        return {
            "planet_id": {row.id: row.code for row in self.db.scalars(select(PlanetModel)).all()},
            "relative_planet_id": {
                row.id: row.code for row in self.db.scalars(select(PlanetModel)).all()
            },
            "house_id": {row.id: row.number for row in self.db.scalars(select(HouseModel)).all()},
            "house_modality_id": {
                row.id: row.name for row in self.db.scalars(select(AstralHouseModalityModel)).all()
            },
            "motion_state_id": {
                row.id: row.code
                for row in self.db.scalars(select(AstralPlanetMotionStateModel)).all()
            },
            "speed_relation_id": {
                row.id: row.code for row in self.db.scalars(select(AstralSpeedRelationModel)).all()
            },
            "heliacal_condition_id": {
                row.id: row.code
                for row in self.db.scalars(select(AstralHeliacalConditionModel)).all()
            },
            "horizon_position_id": {
                row.id: row.code
                for row in self.db.scalars(select(AstralHorizonPositionModel)).all()
            },
            "chart_sect_id": {
                row.id: row.code for row in self.db.scalars(select(AstralSectModel)).all()
            },
            "sign_gender_id": {
                row.id: row.code for row in self.db.scalars(select(AstralSignGenderModel)).all()
            },
            "aspect_from_planet_nature_id": {
                row.id: row.code for row in self.db.scalars(select(AstralPlanetNatureModel)).all()
            },
            "bounding_planet_nature_id": {
                row.id: row.code for row in self.db.scalars(select(AstralPlanetNatureModel)).all()
            },
            "condition_operator_id": {
                row.id: row.code
                for row in self.db.scalars(select(AstralConditionOperatorModel)).all()
            },
        }

    def _normalize_condition_json(
        self,
        condition_json: Mapping[str, object],
        id_maps: dict[str, dict[int, str | int]],
    ) -> tuple[dict[str, object], ...]:
        """Remplace les ids techniques par des codes ou numeros runtime."""
        conditions: list[dict[str, object]] = []
        for key, value in condition_json.items():
            normalized_key = key
            normalized_value: object = value
            if key in id_maps and isinstance(value, int):
                normalized_key = key.removesuffix("_id") + "_code"
                normalized_value = id_maps[key].get(value, value)
            elif key.endswith("_ids") and isinstance(value, list):
                singular = f"{key[:-1]}"
                id_map = id_maps.get(singular)
                if id_map is not None:
                    normalized_key = key[:-4] + "_codes"
                    normalized_value = [id_map.get(int(item), int(item)) for item in value]
            conditions.append({"key": normalized_key, "value": normalized_value})
        return tuple(conditions)

    def _load_angle_points(self) -> tuple[dict[str, object], ...]:
        """Charge les points d'angle structurels."""
        rows = self.db.scalars(select(AstralAnglePointModel).order_by(AstralAnglePointModel.code))
        return tuple(
            {
                "code": row.code,
                "short_label": row.short_label,
                "full_name": row.full_name,
                "axis": row.axis,
                "associated_house": row.associated_house,
            }
            for row in rows
        )

    def _load_astral_point_payload(self) -> tuple[dict[str, object], ...]:
        """Charge les points astraux, variantes et aliases depuis les tables canoniques."""
        point_rows = self.db.scalars(select(AstralPointModel).order_by(AstralPointModel.id)).all()
        variant_rows = self.db.scalars(
            select(AstralPointCalculationVariantModel).order_by(
                AstralPointCalculationVariantModel.astral_point_code,
                AstralPointCalculationVariantModel.id,
            )
        ).all()
        alias_rows = self.db.execute(
            select(AstralPointAliasModel, LanguageModel.code.label("language_code"))
            .join(LanguageModel, AstralPointAliasModel.language_id == LanguageModel.id)
            .order_by(
                AstralPointAliasModel.astral_point_code,
                AstralPointAliasModel.variant_code,
                AstralPointAliasModel.id,
            )
        ).all()
        engine_keys_by_variant = {
            (alias.astral_point_code, alias.variant_code): alias.engine_key
            for alias, _language_code in alias_rows
            if alias.variant_code is not None and alias.engine_key is not None
        }
        variants_by_point: dict[str, list[Mapping[str, object]]] = {}
        for variant in variant_rows:
            variants_by_point.setdefault(variant.astral_point_code, []).append(
                {
                    "variant_code": variant.variant_code,
                    "display_name": variant.display_name,
                    "calculation_mode": variant.calculation_mode,
                    "engine_key": engine_keys_by_variant.get(
                        (variant.astral_point_code, variant.variant_code)
                    ),
                    "is_default": variant.is_default,
                }
            )
        aliases_by_point: dict[str, list[Mapping[str, object]]] = {}
        for alias, language_code in alias_rows:
            aliases_by_point.setdefault(alias.astral_point_code, []).append(
                {
                    "alias": alias.alias,
                    "language_code": language_code,
                    "source": alias.source,
                    "variant_code": alias.variant_code,
                    "engine_key": alias.engine_key,
                    "is_primary": alias.is_primary,
                }
            )
        return tuple(
            {
                "code": row.code,
                "display_name": row.display_name,
                "family_code": row.point_family,
                "astronomical_type": row.astronomical_type,
                "is_physical_body": row.is_physical_body,
                "variants": variants_by_point.get(row.code, []),
                "aliases": aliases_by_point.get(row.code, []),
            }
            for row in point_rows
        )

    def _load_house_systems(self) -> tuple[dict[str, object], ...]:
        """Charge les systemes de maisons actifs ou supportes."""
        rows = self.db.scalars(
            select(AstralHouseSystemModel).order_by(AstralHouseSystemModel.sort_order)
        )
        return tuple(
            {"code": row.code, "name": row.name, "is_active": row.is_active} for row in rows
        )

    def _validate(self, reference: AstrologyRuntimeReference) -> None:
        """Valide l'integrite bloquante du referentiel runtime."""
        self._expect_count("signs", len(reference.signs.items), 12)
        self._expect_count("houses", len(reference.houses.items), 12)
        planet_codes = set(reference.planets.codes)
        sign_codes = set(reference.signs.codes)
        house_numbers = set(reference.houses.numbers)
        aspect_codes = {item.code for item in reference.aspects.items}
        system_codes = {item.code for item in reference.systems.items}
        point_codes = {item.code for item in reference.astral_points.items}
        angle_point_codes = {item.code for item in reference.angle_points.items}
        missing_planets = self._REQUIRED_PLANETS - set(reference.planets.codes)
        if missing_planets:
            self._raise_integrity("planets", f"missing:{','.join(sorted(missing_planets))}")
        self._reject_unknown_codes(
            ("planets", planet_codes),
            ("signs", sign_codes),
            ("aspects", aspect_codes),
            ("systems", system_codes),
        )
        self._validate_sign_profiles(reference)
        missing_angles = self._REQUIRED_ANGLE_POINTS - {
            item.code for item in reference.angle_points.items
        }
        if missing_angles:
            self._raise_integrity("angle_points", f"missing:{','.join(sorted(missing_angles))}")
        for angle_point in reference.angle_points.items:
            if angle_point.associated_house not in house_numbers:
                self._raise_integrity("angle_points", "orphan_house")
        active_house_systems = {
            item.code for item in reference.house_systems.items if item.is_active
        }
        missing_house_systems = self._REQUIRED_HOUSE_SYSTEMS - active_house_systems
        if missing_house_systems:
            self._raise_integrity(
                "house_systems",
                f"missing:{','.join(sorted(missing_house_systems))}",
            )
        if not reference.aspects.items:
            self._raise_integrity("aspects", "missing")
        if not reference.astral_points.items:
            self._raise_integrity("astral_points", "missing")
        for point in reference.astral_points.items:
            if not point.variants:
                self._raise_integrity("astral_points", f"missing_variant:{point.code}")
            if point.default_variant_code is None:
                self._raise_integrity("astral_points", f"missing_default_variant:{point.code}")
        if not reference.aspects.orb_rules:
            self._raise_integrity("aspect_orb_rules", "missing")
        for rule in reference.aspects.orb_rules:
            if rule.aspect_code not in aspect_codes:
                self._raise_integrity("aspect_orb_rules", f"orphan_aspect:{rule.aspect_code}")
            if rule.system_code not in system_codes:
                self._raise_integrity("aspect_orb_rules", f"orphan_system:{rule.system_code}")
            for field, code in (
                ("source_planet_code", rule.source_planet_code),
                ("target_planet_code", rule.target_planet_code),
            ):
                if code is not None and code not in planet_codes:
                    self._raise_integrity("aspect_orb_rules", f"orphan_{field}:{code}")
            for field, code in (
                ("source_point_code", rule.source_point_code),
                ("target_point_code", rule.target_point_code),
            ):
                if code is not None and code not in point_codes and code not in angle_point_codes:
                    self._raise_integrity("aspect_orb_rules", f"orphan_{field}:{code}")
        if not reference.dignities.sign_rulerships:
            self._raise_integrity("sign_rulerships", "missing")
        self._validate_dignity_reference(reference)
        if not reference.condition_signal_profiles:
            self._raise_integrity("condition_signal_profiles", "missing")
        for signal_profile in reference.condition_signal_profiles:
            if signal_profile.condition_axis not in self._CONDITION_SIGNAL_AXES:
                self._raise_integrity(
                    "condition_signal_profiles",
                    f"unknown_axis:{signal_profile.condition_axis}",
                )
        dominance_factor_codes = {item.code for item in reference.dominance_factor_types}
        if dominance_factor_codes != self._REQUIRED_FACTOR_CODES:
            missing = self._REQUIRED_FACTOR_CODES - dominance_factor_codes
            extra = dominance_factor_codes - self._REQUIRED_FACTOR_CODES
            reason = f"missing:{','.join(sorted(missing))};extra:{','.join(sorted(extra))}"
            self._raise_integrity("dominance_factor_types", reason)
        sort_orders = [item.sort_order for item in reference.dominance_factor_types]
        if sort_orders != sorted(sort_orders) or len(sort_orders) != len(set(sort_orders)):
            self._raise_integrity("dominance_factor_types", "invalid_sort_order")
        if not reference.dominance_reference.score_profiles:
            self._raise_integrity("dominance_score_profiles", "missing")
        default_profile = reference.dominance_reference.default_score_profile
        if default_profile.code != "natal_standard_v1":
            self._raise_integrity("dominance_score_profiles", "missing_natal_standard_v1")
        profile_weights = reference.dominance_reference.weights_for_profile(default_profile.code)
        weight_factor_codes = {item.factor_type_code for item in profile_weights}
        if weight_factor_codes != self._REQUIRED_FACTOR_CODES:
            missing = self._REQUIRED_FACTOR_CODES - weight_factor_codes
            extra = weight_factor_codes - self._REQUIRED_FACTOR_CODES
            reason = f"missing:{','.join(sorted(missing))};extra:{','.join(sorted(extra))}"
            self._raise_integrity("dominance_score_weights", reason)
        if len(reference.dignities.sign_rulerships) != 12:
            self._raise_integrity("sign_rulerships", "expected_12")
        for sign_code, planet_code in reference.dignities.sign_rulerships.items():
            if sign_code not in sign_codes:
                self._raise_integrity("sign_rulerships", f"orphan_sign:{sign_code}")
            if planet_code not in planet_codes:
                self._raise_integrity("sign_rulerships", f"orphan_planet:{planet_code}")
        for dignity in reference.dignities.items:
            if dignity.sign_code not in sign_codes:
                self._raise_integrity("dignities", f"orphan_sign:{dignity.sign_code}")
            if dignity.planet_code not in planet_codes:
                self._raise_integrity("dignities", f"orphan_planet:{dignity.planet_code}")
            if dignity.system not in system_codes:
                self._raise_integrity("dignities", f"orphan_system:{dignity.system}")
        for axis in reference.house_axes:
            if axis.house_number not in house_numbers or axis.opposite_house not in house_numbers:
                self._raise_integrity("house_axes", "orphan_house")

    def _validate_sign_profiles(self, reference: AstrologyRuntimeReference) -> None:
        """Verifie que chaque signe porte un profil structurel DB-backed."""
        for sign in reference.signs.items:
            for field_name in ("element", "modality", "polarity"):
                value = getattr(sign, field_name)
                if not value.strip():
                    self._raise_integrity("sign_profiles", f"missing_{field_name}:{sign.code}")
                if value.strip().lower() == "unknown":
                    self._raise_integrity("sign_profiles", f"unknown_{field_name}:{sign.code}")

    def _validate_dignity_reference(self, reference: AstrologyRuntimeReference) -> None:
        """Verifie que le referentiel avance des dignites est calculable."""
        dignity_reference = reference.dignity_reference
        for field, rows in (
            ("essential_types", dignity_reference.essential_types),
            ("accidental_types", dignity_reference.accidental_types),
            ("term_systems", dignity_reference.term_systems),
            ("decan_systems", dignity_reference.decan_systems),
        ):
            if not rows:
                self._raise_integrity("dignity_reference", f"missing_{field}")
        if not dignity_reference.score_profiles:
            self._raise_integrity("dignity_reference", "missing_score_profiles")
        try:
            default_profile = dignity_reference.default_score_profile
        except ValueError:
            self._raise_integrity("dignity_reference", "missing_default_score_profile")
        if not dignity_reference.essential_weights.get(default_profile):
            self._raise_integrity("dignity_reference", "missing_essential_weights")
        if not dignity_reference.accidental_weights.get(default_profile):
            self._raise_integrity("dignity_reference", "missing_accidental_weights")
        for field, rows in (
            ("essential_rules", dignity_reference.essential_rules),
            ("triplicity_rulers", dignity_reference.triplicity_rulers),
            ("term_bounds", dignity_reference.term_bounds),
            ("face_decans", dignity_reference.face_decans),
            ("accidental_rules", dignity_reference.accidental_rules),
        ):
            if not rows:
                self._raise_integrity("dignity_reference", f"missing_{field}")

    def _reject_unknown_codes(self, *groups: tuple[str, set[str]]) -> None:
        """Refuse les sentinelles `unknown` dans les codes runtime canoniques."""
        for field, codes in groups:
            if any(code.strip().lower() == "unknown" for code in codes):
                self._raise_integrity(field, "unknown_forbidden")

    def _expect_count(self, field: str, actual: int, expected: int) -> None:
        if actual != expected:
            self._raise_integrity(field, f"expected_{expected}_actual_{actual}")

    def _raise_integrity(self, field: str, reason: str) -> None:
        raise AstrologyRuntimeReferenceError(
            code="invalid_astrology_runtime_reference",
            message="astrology runtime reference is invalid",
            details={"field": field, "reason": reason},
        )
