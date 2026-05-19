"""Repository des référentiels de dignités et résultats calculés."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AstralAccidentalDignityScoreWeightModel,
    AstralAccidentalDignityTypeModel,
    AstralChartPlanetDignityResultModel,
    AstralDiginityScoreProfileModel,
    AstralEssentialDignityScoreWeightModel,
    AstralEssentialDignityTypeModel,
    AstralSystemModel,
    PlanetModel,
    ReferenceVersionModel,
)


@dataclass(frozen=True)
class DignityScoreWeightData:
    """Projection de lecture d'un poids de scoring de dignité."""

    dignity_type_code: str
    score_value: float
    functional_weight: float
    expression_weight: float
    intensity_weight: float
    visibility_weight: float
    stability_weight: float
    coherence_weight: float
    support_weight: float
    constraint_weight: float
    notes: str


@dataclass(frozen=True)
class ChartPlanetDignityResultInput:
    """Données nécessaires pour persister un résultat de dignité planétaire."""

    chart_result_id: int
    planet_code: str
    score_profile_code: str
    astral_system_code: str
    reference_version: str
    essential_score: float
    accidental_score: float
    total_score: float
    functional_strength_score: float
    expression_quality_score: float
    intensity_score: float
    essential_breakdown_json: list[object]
    accidental_breakdown_json: list[object]
    condition_summary_json: dict[str, object]
    calculation_context_json: dict[str, object]


class DignityReferenceRepository:
    """Accède aux dignités seedées et aux résultats runtime/audit."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_score_profiles(self) -> tuple[AstralDiginityScoreProfileModel, ...]:
        """Retourne les profils de scoring disponibles."""
        return tuple(
            self.db.scalars(
                select(AstralDiginityScoreProfileModel).order_by(AstralDiginityScoreProfileModel.id)
            ).all()
        )

    def list_essential_score_weights(
        self, score_profile_code: str
    ) -> tuple[DignityScoreWeightData, ...]:
        """Retourne les poids essentiels d'un profil de scoring."""
        rows = self.db.execute(
            select(AstralEssentialDignityScoreWeightModel, AstralEssentialDignityTypeModel.code)
            .join(
                AstralEssentialDignityTypeModel,
                AstralEssentialDignityScoreWeightModel.essential_dignity_types_id
                == AstralEssentialDignityTypeModel.id,
            )
            .join(
                AstralDiginityScoreProfileModel,
                AstralEssentialDignityScoreWeightModel.score_profile_id
                == AstralDiginityScoreProfileModel.id,
            )
            .where(AstralDiginityScoreProfileModel.code == score_profile_code)
            .order_by(AstralEssentialDignityTypeModel.sort_order)
        ).all()
        return tuple(
            DignityScoreWeightData(
                dignity_type_code=code,
                score_value=float(weight.score_value),
                functional_weight=float(weight.functional_weight),
                expression_weight=float(weight.expression_weight),
                intensity_weight=float(weight.intensity_weight),
                visibility_weight=float(weight.visibility_weight),
                stability_weight=float(weight.stability_weight),
                coherence_weight=float(weight.coherence_weight),
                support_weight=float(weight.support_weight),
                constraint_weight=float(weight.constraint_weight),
                notes=weight.notes,
            )
            for weight, code in rows
        )

    def list_accidental_score_weights(
        self, score_profile_code: str
    ) -> tuple[DignityScoreWeightData, ...]:
        """Retourne les poids accidentels d'un profil de scoring."""
        rows = self.db.execute(
            select(AstralAccidentalDignityScoreWeightModel, AstralAccidentalDignityTypeModel.code)
            .join(
                AstralAccidentalDignityTypeModel,
                AstralAccidentalDignityScoreWeightModel.accidental_dignity_type_id
                == AstralAccidentalDignityTypeModel.id,
            )
            .join(
                AstralDiginityScoreProfileModel,
                AstralAccidentalDignityScoreWeightModel.score_profile_id
                == AstralDiginityScoreProfileModel.id,
            )
            .where(AstralDiginityScoreProfileModel.code == score_profile_code)
            .order_by(AstralAccidentalDignityTypeModel.sort_order)
        ).all()
        return tuple(
            DignityScoreWeightData(
                dignity_type_code=code,
                score_value=float(weight.score_value),
                functional_weight=float(weight.functional_weight),
                expression_weight=float(weight.expression_weight),
                intensity_weight=float(weight.intensity_weight),
                visibility_weight=float(weight.visibility_weight),
                stability_weight=float(weight.stability_weight),
                coherence_weight=float(weight.coherence_weight),
                support_weight=float(weight.support_weight),
                constraint_weight=float(weight.constraint_weight),
                notes=weight.notes,
            )
            for weight, code in rows
        )

    def upsert_chart_planet_dignity_result(
        self, payload: ChartPlanetDignityResultInput
    ) -> AstralChartPlanetDignityResultModel:
        """Crée ou remplace le résultat calculé pour une planète d'un thème."""
        planet = self._required_code(PlanetModel, PlanetModel.code, payload.planet_code)
        score_profile = self._required_code(
            AstralDiginityScoreProfileModel,
            AstralDiginityScoreProfileModel.code,
            payload.score_profile_code,
        )
        system = self._required_code(
            AstralSystemModel, AstralSystemModel.name, payload.astral_system_code
        )
        reference_version = self._required_code(
            ReferenceVersionModel,
            ReferenceVersionModel.version,
            payload.reference_version,
        )
        result = self.db.scalar(
            select(AstralChartPlanetDignityResultModel).where(
                AstralChartPlanetDignityResultModel.chart_result_id == payload.chart_result_id,
                AstralChartPlanetDignityResultModel.planet_id == planet.id,
                AstralChartPlanetDignityResultModel.score_profile_id == score_profile.id,
                AstralChartPlanetDignityResultModel.reference_version_id == reference_version.id,
            )
        )
        values: dict[str, Any] = {
            "astral_system_id": system.id,
            "essential_score": payload.essential_score,
            "accidental_score": payload.accidental_score,
            "total_score": payload.total_score,
            "functional_strength_score": payload.functional_strength_score,
            "expression_quality_score": payload.expression_quality_score,
            "intensity_score": payload.intensity_score,
            "essential_breakdown_json": payload.essential_breakdown_json,
            "accidental_breakdown_json": payload.accidental_breakdown_json,
            "condition_summary_json": payload.condition_summary_json,
            "calculation_context_json": payload.calculation_context_json,
        }
        if result is None:
            result = AstralChartPlanetDignityResultModel(
                chart_result_id=payload.chart_result_id,
                planet_id=planet.id,
                score_profile_id=score_profile.id,
                reference_version_id=reference_version.id,
                **values,
            )
            self.db.add(result)
        else:
            for field_name, value in values.items():
                setattr(result, field_name, value)
        self.db.flush()
        return result

    def get_chart_planet_dignity_result(
        self,
        chart_result_id: int,
        planet_code: str,
        score_profile_code: str,
        reference_version: str,
    ) -> AstralChartPlanetDignityResultModel | None:
        """Charge le résultat calculé par sa contrainte fonctionnelle unique."""
        return self.db.scalar(
            select(AstralChartPlanetDignityResultModel)
            .join(PlanetModel, AstralChartPlanetDignityResultModel.planet_id == PlanetModel.id)
            .join(
                AstralDiginityScoreProfileModel,
                AstralChartPlanetDignityResultModel.score_profile_id
                == AstralDiginityScoreProfileModel.id,
            )
            .join(
                ReferenceVersionModel,
                AstralChartPlanetDignityResultModel.reference_version_id
                == ReferenceVersionModel.id,
            )
            .where(
                AstralChartPlanetDignityResultModel.chart_result_id == chart_result_id,
                PlanetModel.code == planet_code,
                AstralDiginityScoreProfileModel.code == score_profile_code,
                ReferenceVersionModel.version == reference_version,
            )
        )

    def _required_code(self, model: type[Any], field: Any, value: str) -> Any:
        """Résout une ligne par code ou version et échoue explicitement si elle manque."""
        result = self.db.scalar(select(model).where(field == value))
        if result is None:
            raise ValueError(f"unknown dignity reference value: {value}")
        return result
