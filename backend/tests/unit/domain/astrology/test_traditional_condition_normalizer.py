"""Tests des contrats traditionnels explicites hayz et rejoicing."""

from types import SimpleNamespace

import pytest

from app.domain.astrology.advanced_conditions.contracts import (
    AdvancedPlanetaryCondition,
    PlanetConditionAxisImpact,
)
from app.domain.astrology.advanced_conditions.traditional_condition_normalizer import (
    TraditionalConditionNormalizer,
)
from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    ChartSectResult,
    PlanetDignityResult,
    PlanetSectCondition,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_traditional_condition_normalizer_projects_calculated_hayz_and_rejoicing() -> None:
    """La normalisation consomme les faits calcules sans recreer la doctrine."""
    dignity = _dignity(
        planet_code="moon",
        sect_condition=_sect_condition("moon", is_in_sect=True),
        accidental_breakdown=(
            AccidentalDignityMatch(
                dignity_type_code="planetary_joy",
                score_value=3,
                source="planetary_joy_house",
                reason="moon matches planetary_joy: house_code=3",
                condition="house_code=3",
            ),
        ),
    )
    hayz = AdvancedPlanetaryCondition(
        condition_code="hayz",
        condition_type_code="hayz",
        source_planet_code="moon",
        target_planet_code=None,
        score_profile="traditional_advanced_v1",
        reference_version="v1",
        score_impact=1.5,
        ranking_weight=1.0,
        axes_impact=_axis_impact(),
        reason="moon matches hayz factors.",
        calculation_facts={
            "hemisphere_match": True,
            "sign_gender_match": True,
            "calculation_basis": "sect_hemisphere_sign_gender",
            "reference_system": "traditional",
        },
    )

    result = TraditionalConditionNormalizer().normalize(
        dignities=[dignity],
        planet_positions=[SimpleNamespace(planet_code="moon", house_number=3)],
        advanced_conditions=[hayz],
        runtime_reference=complete_reference(),
    )

    planet = result.planets[0]
    assert planet.hayz.is_hayz is True
    assert planet.hayz.sect_match is True
    assert planet.hayz.hemisphere_match is True
    assert planet.hayz.sign_gender_match is True
    assert planet.rejoicing.is_rejoicing is True
    assert planet.rejoicing.current_house == 3
    assert planet.rejoicing.rejoicing_house == 3


def test_traditional_condition_normalizer_requires_planet_sect_contract() -> None:
    """La normalisation refuse un resultat de dignite sans condition de secte."""
    dignity = _dignity(planet_code="sun", sect_condition=None, accidental_breakdown=())

    with pytest.raises(ValueError, match="planet sect condition contract is required"):
        TraditionalConditionNormalizer().normalize(
            dignities=[dignity],
            planet_positions=[SimpleNamespace(planet_code="sun", house_number=10)],
            advanced_conditions=[],
            runtime_reference=complete_reference(),
        )


def test_traditional_condition_normalizer_exposes_runtime_joy_house_without_match() -> None:
    """La maison de joie reste explicite meme quand la planete ne s'y trouve pas."""
    dignity = _dignity(
        planet_code="moon",
        sect_condition=_sect_condition("moon", is_in_sect=True),
        accidental_breakdown=(),
    )

    result = TraditionalConditionNormalizer().normalize(
        dignities=[dignity],
        planet_positions=[SimpleNamespace(planet_code="moon", house_number=4)],
        advanced_conditions=[],
        runtime_reference=complete_reference(),
    )

    planet = result.planets[0]
    assert planet.rejoicing.is_rejoicing is False
    assert planet.rejoicing.current_house == 4
    assert planet.rejoicing.rejoicing_house == 3


def test_traditional_condition_normalizer_explains_in_sect_non_hayz_components() -> None:
    """Un astre dans la secte mais non hayz expose les composants echoues."""
    dignity = _dignity(
        planet_code="sun",
        sect_condition=_sect_condition("sun", is_in_sect=True),
        accidental_breakdown=(),
    )

    result = TraditionalConditionNormalizer().normalize(
        dignities=[dignity],
        planet_positions=[SimpleNamespace(planet_code="sun", sign_code="cancer", house_number=10)],
        advanced_conditions=[],
        runtime_reference=complete_reference(),
    )

    planet = result.planets[0]
    assert planet.hayz.is_hayz is False
    assert planet.hayz.sect_match is True
    assert planet.hayz.hemisphere_match is True
    assert planet.hayz.sign_gender_match is False
    assert planet.hayz.evidence == (
        "sun hayz factors: hemisphere_match=true;sign_gender_match=false",
    )


def _dignity(
    *,
    planet_code: str,
    sect_condition: PlanetSectCondition | None,
    accidental_breakdown: tuple[AccidentalDignityMatch, ...],
) -> PlanetDignityResult:
    """Construit un resultat de dignite minimal pour les contrats traditionnels."""
    return PlanetDignityResult(
        planet_code=planet_code,
        score_profile="traditional_standard",
        tradition="traditional",
        reference_version="v1",
        sect="night",
        chart_sect=ChartSectResult(
            chart_sect="night",
            sun_horizon_position="below_horizon",
            sun_above_horizon=False,
            calculation_basis="sun_house_horizon_rule",
            reference_system="traditional",
        ),
        sect_condition=sect_condition,
        essential_score=0,
        accidental_score=0,
        total_score=0,
        functional_strength_score=0,
        expression_quality_score=0,
        intensity_score=0,
        essential_breakdown=(),
        accidental_breakdown=accidental_breakdown,
    )


def _sect_condition(planet_code: str, *, is_in_sect: bool) -> PlanetSectCondition:
    """Construit une condition de secte planetaire minimale."""
    return PlanetSectCondition(
        planet_code=planet_code,
        chart_sect="night",
        intrinsic_sect="nocturnal",
        planet_sect_condition="in_sect" if is_in_sect else "out_of_sect",
        is_in_sect=is_in_sect,
        is_out_of_sect=not is_in_sect,
        calculation_basis="chart_sect_vs_planet_intrinsic_sect",
        reference_system="traditional",
    )


def _axis_impact() -> PlanetConditionAxisImpact:
    """Construit un impact neutre pour les conditions avancees de test."""
    return PlanetConditionAxisImpact(
        functional_strength_delta=0,
        visibility_delta=0,
        stability_delta=0,
        intensity_delta=0,
        coherence_delta=0,
        support_delta=0,
        constraint_delta=0,
    )
