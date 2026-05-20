"""Aides de tests pour les conditions planetaires avancees."""

from __future__ import annotations

from app.domain.astrology.condition.contracts import PlanetConditionProfile
from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    ChartSectResult,
    PlanetDignityResult,
    PlanetSectCondition,
)
from app.domain.astrology.natal_calculation import AspectResult, PlanetPosition
from tests.factories.astrology_runtime_reference_factory import complete_reference


def position(
    planet_code: str,
    sign_code: str,
    *,
    longitude: float = 0.0,
    house_number: int = 1,
    is_retrograde: bool = False,
) -> PlanetPosition:
    """Construit une position planetaire minimale."""
    return PlanetPosition(
        planet_code=planet_code,
        longitude=longitude,
        sign_code=sign_code,
        house_number=house_number,
        speed_longitude=0.1,
        is_retrograde=is_retrograde,
    )


def dignity(
    planet_code: str,
    *accidental_codes: str,
) -> PlanetDignityResult:
    """Construit un resultat de dignite avec matches accidentels choisis."""
    return PlanetDignityResult(
        planet_code=planet_code,
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
            planet_code=planet_code,
            chart_sect="day",
            intrinsic_sect="unknown",
            planet_sect_condition="unknown",
            is_in_sect=False,
            is_out_of_sect=False,
            calculation_basis="chart_sect_vs_planet_intrinsic_sect",
            reference_system="runtime_accidental_sect_rules",
        ),
        essential_score=0.0,
        accidental_score=0.0,
        total_score=0.0,
        functional_strength_score=0.0,
        expression_quality_score=0.0,
        intensity_score=0.0,
        essential_breakdown=(),
        accidental_breakdown=tuple(
            AccidentalDignityMatch(
                dignity_type_code=code,
                score_value=1.0,
                source="test",
                reason=f"{planet_code} matches {code}",
                condition=code,
            )
            for code in accidental_codes
        ),
    )


def profile(planet_code: str) -> PlanetConditionProfile:
    """Construit un profil conditionnel minimal."""
    return PlanetConditionProfile(
        planet_code=planet_code,
        score_profile="traditional_standard",
        tradition="traditional",
        reference_version="test",
        sect="day",
        functional_strength=1.0,
        visibility=0.0,
        stability=0.0,
        intensity=0.0,
        coherence=0.0,
        support=0.0,
        constraint=0.0,
        ranking_score=1.0,
        condition_level="mixed",
        breakdown=(),
        explanation_facts=(),
    )


def aspect(
    planet_a: str, planet_b: str, *, orb_used: float = 1.0, orb_max: float = 8.0
) -> AspectResult:
    """Construit un aspect majeur minimal."""
    return AspectResult(
        aspect_code="conjunction",
        planet_a=planet_a,
        planet_b=planet_b,
        angle=0.0,
        orb=orb_used,
        orb_used=orb_used,
        orb_max=orb_max,
        family="major",
        is_major=True,
        is_minor=False,
        default_valence="contextual",
        interpretive_valence="fusion",
        energy_type="fusion",
    )


def advanced_engine_result(
    positions: tuple[PlanetPosition, ...],
    dignities: tuple[PlanetDignityResult, ...],
    aspects: tuple[AspectResult, ...] = (),
):
    """Calcule les conditions avancees avec la reference de fixture."""
    from app.domain.astrology.advanced_conditions.advanced_condition_engine import (
        AdvancedConditionEngine,
    )

    return AdvancedConditionEngine().calculate(
        runtime_reference=complete_reference(),
        planet_positions=positions,
        aspects=aspects,
        dignities=dignities,
        condition_profiles=tuple(profile(item.planet_code) for item in positions),
    )
