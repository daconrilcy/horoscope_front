"""Tests du builder d'input interpretatif chart-object."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.astrology.advanced_conditions.contracts import (
    AdvancedPlanetaryCondition,
    PlanetConditionAxisImpact,
)
from app.domain.astrology.dominance.contracts import DominantPlanetsResult, PlanetDominanceResult
from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object


@dataclass(frozen=True, slots=True)
class _NatalSource:
    """Source minimale equivalente aux champs runtime du resultat natal."""

    chart_objects: tuple[object, ...]
    aspects: tuple[object, ...]
    dominant_planets: DominantPlanetsResult
    advanced_condition_facts: tuple[AdvancedPlanetaryCondition, ...] = ()


def test_builder_constructs_sections_from_chart_objects() -> None:
    """Le builder expose les sections attendues depuis les payloads chart-object."""
    source = _NatalSource(
        chart_objects=(
            interpretable_chart_object("mars"),
            interpretable_chart_object("regulus", supports_interpretation=False),
        ),
        aspects=(),
        dominant_planets=DominantPlanetsResult(
            score_profile_code="fixture.profile",
            tradition_code="fixture",
            reference_version_code="v1",
            planets=(
                PlanetDominanceResult(
                    planet_code="mars",
                    total_score=1.0,
                    rank=1,
                    dominance_level="dominant",
                    factors=(),
                    explanation_facts=(),
                ),
            ),
            top_planet_code="mars",
            chart_ruler_code="mars",
            most_elevated_planet_code="mars",
        ),
        advanced_condition_facts=(
            AdvancedPlanetaryCondition(
                condition_code="hayz",
                condition_type_code="hayz",
                source_planet_code="mars",
                target_planet_code=None,
                score_profile="traditional_advanced_v1",
                reference_version="v1",
                score_impact=1.0,
                ranking_weight=1.1,
                axes_impact=PlanetConditionAxisImpact(
                    functional_strength_delta=0.0,
                    visibility_delta=0.0,
                    stability_delta=0.0,
                    intensity_delta=0.0,
                    coherence_delta=0.0,
                    support_delta=0.0,
                    constraint_delta=0.0,
                ),
                reason="fact runtime fixture",
            ),
        ),
    )

    result = ChartInterpretationInputBuilder().build(source, chart_id="chart-1", locale="fr")

    assert result.chart_id == "chart-1"
    assert result.chart_type == "natal"
    assert result.locale == "fr"
    assert [item.code for item in result.objects] == ["mars"]
    assert [item.code for item in result.dignities] == ["mars"]
    assert [item.code for item in result.house_positions] == ["mars"]
    assert [item.code for item in result.rulerships] == ["mars"]
    assert [item.fixed_star_code for item in result.fixed_star_contacts] == ["regulus"]
    assert [item.code for item in result.dominance] == ["mars"]
    assert [item.condition_code for item in result.advanced_condition_facts] == ["hayz"]
    assert result.metadata.object_count == 1
