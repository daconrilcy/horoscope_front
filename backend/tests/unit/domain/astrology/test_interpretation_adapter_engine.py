"""Tests du moteur d'adaptation interpretative."""

from __future__ import annotations

from app.domain.astrology.condition.contracts import PlanetConditionProfile
from app.domain.astrology.dominance.contracts import DominantPlanetsResult, PlanetDominanceResult
from app.domain.astrology.interpretation_adapters import InterpretationAdapterEngine
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _profile(planet_code: str, *, visibility: float, constraint: float) -> PlanetConditionProfile:
    """Construit un profil conditionnel minimal pour le moteur."""
    return PlanetConditionProfile(
        planet_code=planet_code,
        score_profile="traditional_standard",
        tradition="traditional",
        reference_version="test",
        sect="day",
        functional_strength=0.0,
        visibility=visibility,
        stability=0.0,
        intensity=0.0,
        coherence=0.0,
        support=0.0,
        constraint=constraint,
        ranking_score=0.0,
        condition_level="moderate",
        breakdown=(),
        explanation_facts=(),
    )


def _dominant(planet_code: str) -> DominantPlanetsResult:
    """Construit une dominante minimale."""
    return DominantPlanetsResult(
        score_profile_code="natal_standard_v1",
        tradition_code="modern",
        reference_version_code="v1",
        planets=(
            PlanetDominanceResult(
                planet_code=planet_code,
                total_score=1.0,
                rank=1,
                dominance_level="dominant",
                factors=(),
                explanation_facts=(),
            ),
        ),
        top_planet_code=planet_code,
        chart_ruler_code=planet_code,
        most_elevated_planet_code=planet_code,
    )


def test_interpretation_adapter_engine_returns_complete_result() -> None:
    """Le moteur assemble signaux, themes et listes de priorite."""
    result = InterpretationAdapterEngine().calculate(
        runtime_reference=complete_reference(),
        planet_positions=(),
        aspects=(),
        dignities=(),
        condition_profiles=(_profile("mars", visibility=0.79, constraint=0.62),),
        condition_signals=(),
        advanced_conditions=(),
        dominant_planets=_dominant("mars"),
    )

    assert [signal.signal_code for signal in result.signals] == [
        "dominant_mars_signature",
        "high_externalization",
        "constraint_on_action",
    ]
    assert result.dominant_topics == (
        "drive_assertion_action",
        "visibility_expression",
        "frustration_pressure",
    )
    assert result.critical_patterns == ("dominant_mars_signature",)
