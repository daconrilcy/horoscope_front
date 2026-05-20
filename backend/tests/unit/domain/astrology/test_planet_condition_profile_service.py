"""Tests du service de profils conditionnels planetaires."""

from dataclasses import replace

from app.domain.astrology.condition.contracts import (
    PlanetConditionBreakdownItem,
    PlanetConditionExplanationFact,
    PlanetConditionProfile,
)
from app.domain.astrology.condition.planet_condition_profile_service import (
    PlanetConditionProfileService,
)
from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    ChartSectResult,
    EssentialDignityMatch,
    PlanetDignityResult,
    PlanetSectCondition,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _result() -> PlanetDignityResult:
    """Construit un resultat de dignite stable pour les assertions."""
    return PlanetDignityResult(
        planet_code="sun",
        score_profile="traditional_standard",
        tradition="traditional",
        reference_version="test",
        sect="day",
        chart_sect=ChartSectResult(
            chart_sect="day",
            sun_horizon_position="above_horizon",
            sun_above_horizon=True,
            calculation_basis="sun_house_horizon_rule",
            reference_system="traditional",
        ),
        sect_condition=PlanetSectCondition(
            planet_code="sun",
            chart_sect="day",
            intrinsic_sect="diurnal",
            planet_sect_condition="in_sect",
            is_in_sect=True,
            is_out_of_sect=False,
            calculation_basis="chart_sect_vs_planet_intrinsic_sect",
            reference_system="traditional",
        ),
        essential_score=5.0,
        accidental_score=4.0,
        total_score=9.0,
        functional_strength_score=1.9,
        expression_quality_score=1.5,
        intensity_score=1.5,
        essential_breakdown=(
            EssentialDignityMatch(
                dignity_type_code="domicile",
                score_value=5.0,
                source="essential_rule",
                reason="sun in leo: domicile",
                sign_code="leo",
                degree_start=0.0,
                degree_end=30.0,
            ),
        ),
        accidental_breakdown=(
            AccidentalDignityMatch(
                dignity_type_code="angular_house",
                score_value=4.0,
                source="house_modality",
                reason="sun matches angular house",
                condition="house_codes=(1, 4, 7, 10)",
            ),
        ),
    )


def _reference_with_condition_axes():
    """Ajoute des axes de test au runtime sans creer de mapping metier local."""
    reference = complete_reference()
    dignity_reference = reference.dignity_reference
    essential_weights = tuple(
        replace(
            weight,
            condition_visibility=0.3,
            condition_stability=0.4,
            condition_coherence=0.2,
            condition_support=0.5,
            condition_constraint=0.1,
        )
        if weight.dignity_type_code == "domicile"
        else weight
        for weight in dignity_reference.essential_weights["traditional_standard"]
    )
    accidental_weights = tuple(
        replace(
            weight,
            condition_visibility=0.7,
            condition_stability=0.1,
            condition_coherence=0.3,
            condition_support=0.2,
            condition_constraint=0.4,
        )
        if weight.dignity_type_code == "angular_house"
        else weight
        for weight in dignity_reference.accidental_weights["traditional_standard"]
    )
    return replace(
        reference,
        dignity_reference=replace(
            dignity_reference,
            essential_weights={"traditional_standard": essential_weights},
            accidental_weights={"traditional_standard": accidental_weights},
        ),
    )


def test_condition_contracts_are_immutable_and_typed() -> None:
    """Les contrats conditionnels sont des dataclasses immutables explicites."""
    profile = PlanetConditionProfile(
        planet_code="sun",
        score_profile="traditional_standard",
        tradition="traditional",
        reference_version="test",
        sect="day",
        functional_strength=1.0,
        visibility=0.0,
        stability=0.0,
        intensity=1.0,
        coherence=0.0,
        support=0.0,
        constraint=0.0,
        ranking_score=2.0,
        condition_level="supportive",
        breakdown=(
            PlanetConditionBreakdownItem(
                dignity_family="essential",
                dignity_type_code="domicile",
                source="essential_rule",
                reason="fact",
                score_value=5.0,
                functional_strength=1.0,
                visibility=0.0,
                stability=0.0,
                intensity=1.0,
                coherence=0.0,
                support=0.0,
                constraint=0.0,
            ),
        ),
        explanation_facts=(PlanetConditionExplanationFact("ranking_score", "2"),),
    )

    assert profile.breakdown[0].dignity_type_code == "domicile"
    assert profile.explanation_facts[0].fact_type == "ranking_score"


def test_service_derives_axes_from_dignity_result_and_runtime_weights() -> None:
    """Les axes canoniques proviennent du resultat de dignite et du runtime."""
    profile = PlanetConditionProfileService().calculate(
        (_result(),),
        _reference_with_condition_axes(),
    )[0]

    assert profile.functional_strength == 1.9
    assert profile.intensity == 1.5
    assert profile.visibility == 1.0
    assert profile.stability == 0.5
    assert profile.coherence == 0.5
    assert profile.support == 0.7
    assert profile.constraint == 0.5
    assert profile.ranking_score == 5.6
    assert profile.condition_level == "strong"
    assert [item.dignity_type_code for item in profile.breakdown] == [
        "domicile",
        "angular_house",
    ]
    assert profile.explanation_facts == (
        PlanetConditionExplanationFact("essential_match_count", "1"),
        PlanetConditionExplanationFact("accidental_match_count", "1"),
        PlanetConditionExplanationFact("ranking_score", "5.6"),
    )


def test_condition_ranking_is_deterministic() -> None:
    """Le classement reste stable pour les memes entrees."""
    service = PlanetConditionProfileService()
    reference = _reference_with_condition_axes()

    first = service.calculate((_result(),), reference)
    second = service.calculate((_result(),), reference)

    assert first == second
