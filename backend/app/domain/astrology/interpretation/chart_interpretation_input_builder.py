# Assemblage de l'entree interpretative depuis le resultat natal runtime.
"""Builder centralise autour de `NatalResult.chart_objects`."""

from __future__ import annotations

from typing import Any

from app.domain.astrology.advanced_conditions import AdvancedPlanetaryCondition
from app.domain.astrology.dominance.contracts import DominantPlanetsResult
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    AdvancedConditionInterpretationRuntimeData,
    AspectInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    ChartInterpretationMetadataRuntimeData,
    DominanceInterpretationRuntimeData,
    SignProfileBalancesInterpretationRuntimeData,
)
from app.domain.astrology.interpretation.chart_object_interpretation_projector import (
    ChartObjectInterpretationProjector,
)
from app.domain.astrology.interpretation.chart_object_interpretation_selector import (
    ChartObjectInterpretationSelector,
)


class ChartInterpretationInputBuilder:
    """Construit l'input interpretatif interne depuis les objets du theme."""

    def __init__(
        self,
        selector: ChartObjectInterpretationSelector | None = None,
        projector: ChartObjectInterpretationProjector | None = None,
    ) -> None:
        """Initialise les collaborateurs de selection et projection."""
        self.selector = selector or ChartObjectInterpretationSelector()
        self.projector = projector or ChartObjectInterpretationProjector()

    def build(
        self,
        natal_result: Any,
        *,
        chart_id: str | None = None,
        locale: str | None = None,
    ) -> ChartInterpretationInputRuntimeData:
        """Assemble un input natal sans changer les collections historiques."""
        objects = tuple(
            self.projector.project(chart_object)
            for chart_object in self.selector.select(tuple(natal_result.chart_objects))
        )
        aspects = _project_aspects(tuple(natal_result.aspects))
        dignity_items = tuple(item.dignity for item in objects if item.dignity is not None)
        house_positions = tuple(
            self.projector.project_house_position(chart_object)
            for chart_object in self.selector.select(tuple(natal_result.chart_objects))
        )
        rulerships = tuple(item.rulership for item in objects if item.rulership is not None)
        fixed_star_contacts = tuple(
            contact for item in objects for contact in item.fixed_star_contacts
        )
        dominance = _project_chart_dominance(getattr(natal_result, "dominant_planets", None))
        advanced_condition_facts = _project_advanced_condition_facts(
            tuple(getattr(natal_result, "advanced_condition_facts", ()))
        )
        source_codes = tuple(dict.fromkeys(code for item in objects for code in item.source_codes))
        sign_profile_balances = _project_sign_profile_balances(
            getattr(natal_result, "chart_balance", None)
        )
        return ChartInterpretationInputRuntimeData(
            chart_id=chart_id,
            chart_type="natal",
            locale=locale,
            objects=objects,
            aspects=aspects,
            dignities=dignity_items,
            house_positions=tuple(item for item in house_positions if item is not None),
            rulerships=rulerships,
            dominance=dominance,
            sign_profile_balances=sign_profile_balances,
            advanced_condition_facts=advanced_condition_facts,
            fixed_star_contacts=fixed_star_contacts,
            metadata=ChartInterpretationMetadataRuntimeData(
                source_codes=source_codes,
                object_count=len(objects),
                aspect_count=len(aspects),
            ),
        )


def _project_aspects(aspects: tuple[Any, ...]) -> tuple[AspectInterpretationRuntimeData, ...]:
    """Projette les aspects depuis leur runtime deja calcule."""
    projected: list[AspectInterpretationRuntimeData] = []
    for aspect_result in aspects:
        runtime = getattr(aspect_result, "aspect_runtime", None)
        if runtime is not None:
            hints = getattr(aspect_result, "aspect_interpretive_hints", None)
            projected.append(
                AspectInterpretationRuntimeData(
                    code=runtime.aspect.code,
                    participant_codes=(
                        runtime.participants.planet_a,
                        runtime.participants.planet_b,
                    ),
                    family=runtime.aspect.family,
                    angle=runtime.aspect.angle,
                    orb=runtime.orb.exact,
                    orb_max=runtime.orb.max,
                    strength_level=runtime.orb.strength_level,
                    is_major=runtime.metadata.is_major,
                    source="aspect_interpretive_hints" if hints is not None else "aspect_runtime",
                )
            )
            continue
        projected.append(
            AspectInterpretationRuntimeData(
                code=str(aspect_result.aspect_code),
                participant_codes=(str(aspect_result.planet_a), str(aspect_result.planet_b)),
                family=str(aspect_result.family),
                angle=float(aspect_result.angle),
                orb=float(aspect_result.orb),
                orb_max=float(aspect_result.orb_max),
                strength_level="runtime_unavailable",
                is_major=bool(aspect_result.is_major),
                source="aspect_result",
            )
        )
    return tuple(projected)


def _project_advanced_condition_facts(
    conditions: tuple[AdvancedPlanetaryCondition, ...],
) -> tuple[AdvancedConditionInterpretationRuntimeData, ...]:
    """Projette les conditions avancees deja calculees dans l'input central."""
    return tuple(
        AdvancedConditionInterpretationRuntimeData(
            condition_code=condition.condition_code,
            condition_type_code=condition.condition_type_code,
            source_planet_code=condition.source_planet_code,
            target_planet_code=condition.target_planet_code,
            score_profile=condition.score_profile,
            reference_version=condition.reference_version,
            score_impact=condition.score_impact,
            ranking_weight=condition.ranking_weight,
        )
        for condition in conditions
    )


def _project_balance_family(
    items: tuple[Any, ...],
) -> tuple[DominanceInterpretationRuntimeData, ...]:
    """Projette une famille de balance sans recalculer les profils par signe."""
    return tuple(
        DominanceInterpretationRuntimeData(
            code=item.code,
            score=item.score,
            source="chart_balance",
            rank=item.rank,
        )
        for item in items
    )


def _project_sign_profile_balances(
    chart_balance: Any,
) -> SignProfileBalancesInterpretationRuntimeData | None:
    """Lit les profils enrichis depuis la balance canonique du theme."""
    if chart_balance is None:
        return None
    return SignProfileBalancesInterpretationRuntimeData(
        elements=_project_balance_family(tuple(chart_balance.elements)),
        modalities=_project_balance_family(tuple(chart_balance.modalities)),
        polarities=_project_balance_family(tuple(chart_balance.polarities)),
        seasonal_quadrants=_project_balance_family(tuple(chart_balance.seasonal_quadrants)),
        fertility=_project_balance_family(tuple(chart_balance.fertility)),
        voices=_project_balance_family(tuple(chart_balance.voices)),
        forms=_project_balance_family(tuple(chart_balance.forms)),
    )


def _project_chart_dominance(
    dominant_planets: DominantPlanetsResult | None,
) -> tuple[DominanceInterpretationRuntimeData, ...]:
    """Projette la dominance chart-level deja calculee."""
    if dominant_planets is None:
        return ()
    return tuple(
        DominanceInterpretationRuntimeData(
            code=planet.planet_code,
            score=planet.total_score,
            source=dominant_planets.score_profile_code,
            rank=planet.rank,
            dominance_level=planet.dominance_level,
            factors=tuple(factor.factor_code for factor in planet.factors),
        )
        for planet in dominant_planets.planets
    )
