"""Tests du moteur factuel des dominantes planetaires."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from app.domain.astrology.condition.contracts import PlanetConditionProfile
from app.domain.astrology.dominance.contracts import PlanetDominanceFactor
from app.domain.astrology.dominance.planet_dominance_engine import PlanetDominanceEngine
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.natal_calculation import AspectResult, PlanetPosition
from app.domain.astrology.runtime.house_runtime_data import (
    HouseOccupantRuntimeData,
    HouseRuntimeData,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference

PROJECT_ROOT = Path(__file__).resolve().parents[5]
ENGINE_SOURCE = PROJECT_ROOT / "backend/app/domain/astrology/dominance/planet_dominance_engine.py"


def _profiles() -> tuple[PlanetConditionProfile, ...]:
    """Construit des profils conditionnels factuels pour le moteur."""
    return (
        PlanetConditionProfile(
            planet_code="sun",
            score_profile="traditional_standard",
            tradition="traditional",
            reference_version="test",
            sect="day",
            functional_strength=4.0,
            visibility=2.0,
            stability=0.0,
            intensity=0.0,
            coherence=0.0,
            support=0.0,
            constraint=0.0,
            ranking_score=6.0,
            condition_level="strong",
            breakdown=(),
            explanation_facts=(),
        ),
        PlanetConditionProfile(
            planet_code="mars",
            score_profile="traditional_standard",
            tradition="traditional",
            reference_version="test",
            sect="day",
            functional_strength=2.0,
            visibility=1.0,
            stability=0.0,
            intensity=0.0,
            coherence=0.0,
            support=0.0,
            constraint=0.0,
            ranking_score=3.0,
            condition_level="supportive",
            breakdown=(),
            explanation_facts=(),
        ),
    )


def _positions() -> tuple[PlanetPosition, ...]:
    """Construit les positions minimales necessaires au classement."""
    return (
        PlanetPosition(
            planet_code="sun",
            longitude=20.0,
            sign_code="aries",
            house_number=10,
        ),
        PlanetPosition(
            planet_code="mars",
            longitude=110.0,
            sign_code="cancer",
            house_number=1,
        ),
    )


def _houses() -> tuple[HouseRuntimeData, ...]:
    """Construit des maisons avec occupants runtime deja resolus."""
    return (
        HouseRuntimeData(
            number=1,
            cusp_longitude=0.0,
            occupants=[HouseOccupantRuntimeData("mars", "cancer", 110.0)],
        ),
        HouseRuntimeData(
            number=10,
            cusp_longitude=270.0,
            occupants=[HouseOccupantRuntimeData("sun", "aries", 20.0)],
        ),
    )


def _house_rulers() -> tuple[HouseRulerResult, ...]:
    """Construit une charge de maitrises dominee par Mars."""
    return (
        HouseRulerResult(
            house_number=1,
            cusp_sign="aries",
            ruler_planet="mars",
            ruler_planet_sign="cancer",
            ruler_planet_house=1,
        ),
        HouseRulerResult(
            house_number=2,
            cusp_sign="taurus",
            ruler_planet="venus",
            ruler_planet_sign="taurus",
            ruler_planet_house=2,
        ),
        HouseRulerResult(
            house_number=3,
            cusp_sign="gemini",
            ruler_planet="mercury",
            ruler_planet_sign="gemini",
            ruler_planet_house=3,
        ),
        HouseRulerResult(
            house_number=4,
            cusp_sign="cancer",
            ruler_planet="moon",
            ruler_planet_sign="cancer",
            ruler_planet_house=4,
        ),
        HouseRulerResult(
            house_number=5,
            cusp_sign="leo",
            ruler_planet="sun",
            ruler_planet_sign="aries",
            ruler_planet_house=10,
        ),
        HouseRulerResult(
            house_number=6,
            cusp_sign="virgo",
            ruler_planet="mercury",
            ruler_planet_sign="gemini",
            ruler_planet_house=3,
        ),
        HouseRulerResult(
            house_number=7,
            cusp_sign="libra",
            ruler_planet="venus",
            ruler_planet_sign="taurus",
            ruler_planet_house=2,
        ),
        HouseRulerResult(
            house_number=8,
            cusp_sign="scorpio",
            ruler_planet="mars",
            ruler_planet_sign="cancer",
            ruler_planet_house=1,
        ),
        HouseRulerResult(
            house_number=9,
            cusp_sign="sagittarius",
            ruler_planet="jupiter",
            ruler_planet_sign="sagittarius",
            ruler_planet_house=9,
        ),
        HouseRulerResult(
            house_number=10,
            cusp_sign="capricorn",
            ruler_planet="saturn",
            ruler_planet_sign="capricorn",
            ruler_planet_house=10,
        ),
        HouseRulerResult(
            house_number=11,
            cusp_sign="aquarius",
            ruler_planet="saturn",
            ruler_planet_sign="capricorn",
            ruler_planet_house=10,
        ),
        HouseRulerResult(
            house_number=12,
            cusp_sign="pisces",
            ruler_planet="jupiter",
            ruler_planet_sign="sagittarius",
            ruler_planet_house=9,
        ),
    )


def _aspect(
    *,
    planet_a: str,
    planet_b: str,
    orb_used: float,
) -> AspectResult:
    """Construit un aspect natal minimal avec runtime enrichi."""
    return AspectResult(
        aspect_code="conjunction",
        planet_a=planet_a,
        planet_b=planet_b,
        angle=0.0,
        orb=orb_used,
        orb_used=orb_used,
        orb_max=8.0,
        family="major",
        is_major=True,
        is_minor=False,
        default_valence="contextual",
        interpretive_valence="fusion",
        energy_type="fusion",
    )


def _positions_with_venus() -> tuple[PlanetPosition, ...]:
    """Ajoute Venus pour tester les aspects avec points non classes."""
    return (
        *_positions(),
        PlanetPosition(
            planet_code="venus",
            longitude=140.0,
            sign_code="leo",
            house_number=3,
        ),
    )


def _profiles_with_venus() -> tuple[PlanetConditionProfile, ...]:
    """Ajoute un profil faible pour Venus sans changer les dominantes principales."""
    return (
        *_profiles(),
        PlanetConditionProfile(
            planet_code="venus",
            score_profile="traditional_standard",
            tradition="traditional",
            reference_version="test",
            sect="day",
            functional_strength=1.0,
            visibility=1.0,
            stability=0.0,
            intensity=0.0,
            coherence=0.0,
            support=0.0,
            constraint=0.0,
            ranking_score=2.0,
            condition_level="weak",
            breakdown=(),
            explanation_facts=(),
        ),
    )


def test_planet_dominance_contracts_are_immutable() -> None:
    """Les contributions de dominance ne peuvent pas etre modifiees apres calcul."""
    contribution = PlanetDominanceFactor(
        factor_code="chart_ruler",
        raw_value=1.0,
        normalized_value=1.0,
        weight=1.4,
        weighted_score=1.4,
        reason="mars rules the Ascendant sign.",
    )

    with pytest.raises(FrozenInstanceError):
        contribution.normalized_value = 0.0


def test_planet_dominance_engine_ranks_by_score_then_planet_code() -> None:
    """Le moteur classe les planetes par score decroissant puis code stable."""
    result = PlanetDominanceEngine().calculate(
        runtime_reference=complete_reference(),
        chart_object_positions=_positions(),
        houses=_houses(),
        house_rulers=_house_rulers(),
        condition_profiles=_profiles(),
        aspects=(_aspect(planet_a="sun", planet_b="mars", orb_used=1.0),),
    )

    assert result.score_profile_code == "natal_standard_v1"
    assert result.tradition_code == "modern"
    assert result.reference_version_code == "v1"
    assert [planet.planet_code for planet in result.planets] == ["sun", "mars"]
    assert result.planets[0].rank == 1
    assert result.planets[0].total_score >= result.planets[1].total_score
    assert result.planets[0].dominance_level in {
        "very_low",
        "low",
        "moderate",
        "high",
        "dominant",
    }
    assert {factor.factor_code for factor in result.planets[0].factors} == {
        "chart_ruler",
        "angularity",
        "condition_strength",
        "visibility",
        "most_elevated",
        "luminary_emphasis",
        "house_rulership_load",
        "aspect_centrality",
    }
    assert result.top_planet_code == "sun"
    assert result.chart_ruler_code == "mars"
    assert result.most_elevated_planet_code == "sun"


def test_planet_dominance_uses_runtime_rulership_and_condition_profiles() -> None:
    """Les facteurs critiques proviennent des faits runtime et conditionnels."""
    result = PlanetDominanceEngine().calculate(
        runtime_reference=complete_reference(),
        chart_object_positions=_positions(),
        houses=_houses(),
        house_rulers=_house_rulers(),
        condition_profiles=_profiles(),
        aspects=(),
    )
    mars = next(planet for planet in result.planets if planet.planet_code == "mars")
    sun = next(planet for planet in result.planets if planet.planet_code == "sun")

    mars_chart_ruler = next(item for item in mars.factors if item.factor_code == "chart_ruler")
    sun_strength = next(item for item in sun.factors if item.factor_code == "condition_strength")
    sun_visibility = next(item for item in sun.factors if item.factor_code == "visibility")

    assert mars_chart_ruler.raw_value == 1.0
    assert mars_chart_ruler.normalized_value == 1.0
    assert mars_chart_ruler.reason == "mars rules the Ascendant sign."
    assert sun_strength.normalized_value == 1.0
    assert sun_visibility.normalized_value == 1.0


def test_aspect_centrality_uses_dominant_aspect_runtime_scores() -> None:
    """La centralite d'aspects reutilise le classement canonique des aspects dominants."""
    result = PlanetDominanceEngine().calculate(
        runtime_reference=complete_reference(),
        chart_object_positions=_positions(),
        houses=_houses(),
        house_rulers=_house_rulers(),
        condition_profiles=_profiles(),
        aspects=(
            _aspect(planet_a="sun", planet_b="mars", orb_used=1.0),
            _aspect(planet_a="sun", planet_b="venus", orb_used=4.0),
        ),
    )

    sun = next(planet for planet in result.planets if planet.planet_code == "sun")
    mars = next(planet for planet in result.planets if planet.planet_code == "mars")
    sun_aspects = next(item for item in sun.factors if item.factor_code == "aspect_centrality")
    mars_aspects = next(item for item in mars.factors if item.factor_code == "aspect_centrality")

    assert sun_aspects.normalized_value == 1.0
    assert sun_aspects.weight == 0.8
    assert sun_aspects.weighted_score == 0.8
    assert mars_aspects.normalized_value == pytest.approx(0.561798)
    assert mars_aspects.weighted_score == pytest.approx(0.449438)
    assert sun_aspects.reason.startswith("sun aspect centrality score is")


def test_aspect_centrality_ignores_non_ranked_point_participants() -> None:
    """Les aspects de points astraux ne normalisent pas les scores des planetes."""
    result = PlanetDominanceEngine().calculate(
        runtime_reference=complete_reference(),
        chart_object_positions=_positions_with_venus(),
        houses=_houses(),
        house_rulers=_house_rulers(),
        condition_profiles=_profiles_with_venus(),
        aspects=(
            _aspect(planet_a="north_node", planet_b="south_node", orb_used=0.1),
            _aspect(planet_a="sun", planet_b="mars", orb_used=4.0),
        ),
    )

    sun = next(planet for planet in result.planets if planet.planet_code == "sun")
    mars = next(planet for planet in result.planets if planet.planet_code == "mars")
    venus = next(planet for planet in result.planets if planet.planet_code == "venus")
    sun_aspects = next(item for item in sun.factors if item.factor_code == "aspect_centrality")
    mars_aspects = next(item for item in mars.factors if item.factor_code == "aspect_centrality")
    venus_aspects = next(item for item in venus.factors if item.factor_code == "aspect_centrality")

    assert sun_aspects.raw_value == 1.0
    assert mars_aspects.raw_value == 1.0
    assert venus_aspects.raw_value == 0.0
    assert venus_aspects.reason == "venus aspect centrality score is 0."


def test_planet_dominance_handles_missing_condition_profile() -> None:
    """Une planete sans profil conditionnel reste calculable avec score nul."""
    result = PlanetDominanceEngine().calculate(
        runtime_reference=complete_reference(),
        chart_object_positions=_positions(),
        houses=_houses(),
        house_rulers=_house_rulers(),
        condition_profiles=_profiles()[0:1],
        aspects=(),
    )

    mars = next(planet for planet in result.planets if planet.planet_code == "mars")
    mars_strength = next(item for item in mars.factors if item.factor_code == "condition_strength")
    mars_visibility = next(item for item in mars.factors if item.factor_code == "visibility")

    assert mars_strength.normalized_value == 0.0
    assert mars_strength.reason == "mars has no condition strength profile."
    assert mars_visibility.normalized_value == 0.0
    assert mars_visibility.reason == "mars has no visibility profile."


def test_planet_dominance_does_not_recalculate_sect() -> None:
    """Le moteur de dominance consomme des profils et conditions deja calcules."""
    source = ENGINE_SOURCE.read_text(encoding="utf-8")

    assert "SectCalculator" not in source
    assert "PlanetSectConditionCalculator" not in source
    assert "planet_sect_condition_calculator" not in source
