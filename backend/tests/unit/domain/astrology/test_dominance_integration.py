"""Tests d'integration dominance et conditions avancees."""

from __future__ import annotations

from app.domain.astrology.advanced_conditions.contracts import (
    AdvancedPlanetaryCondition,
    PlanetConditionAxisImpact,
)
from app.domain.astrology.dominance.planet_dominance_engine import PlanetDominanceEngine
from tests.factories.astrology_runtime_reference_factory import complete_reference
from tests.unit.domain.astrology.test_planet_dominance_engine import (
    _aspect,
    _house_rulers,
    _houses,
    _positions,
    _profiles,
)


def test_dominance_condition_strength_uses_advanced_ranking_weight() -> None:
    """La dominance tient compte du ranking_weight avance deja calcule."""
    advanced = AdvancedPlanetaryCondition(
        condition_code="hayz",
        condition_type_code="hayz",
        source_planet_code="mars",
        target_planet_code=None,
        score_profile="traditional_advanced_v1",
        reference_version="v1",
        score_impact=1.0,
        ranking_weight=10.0,
        axes_impact=PlanetConditionAxisImpact(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        reason="mars matches hayz.",
    )

    result = PlanetDominanceEngine().calculate(
        runtime_reference=complete_reference(),
        planet_positions=_positions(),
        houses=_houses(),
        house_rulers=_house_rulers(),
        condition_profiles=_profiles(),
        aspects=(_aspect(planet_a="sun", planet_b="mars", orb_used=1.0),),
        advanced_conditions=(advanced,),
    )

    mars = next(item for item in result.planets if item.planet_code == "mars")
    strength = next(item for item in mars.factors if item.factor_code == "condition_strength")

    assert strength.reason.endswith("advanced ranking weight is 10.")
    assert strength.normalized_value == 1.0
