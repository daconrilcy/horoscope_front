"""Tests d'integration des modificateurs avances dans le scoring accidentel."""

from pydantic import TypeAdapter

from app.domain.astrology.dignities.contracts import PlanetDignityInput, PlanetDignityResult
from app.domain.astrology.dignities.planet_dignity_scoring_service import (
    PlanetDignityScoringService,
)
from app.domain.astrology.planetary_conditions.contracts import (
    AdvancedPlanetaryConditionsResult,
    ConditionConfidence,
    ConditionSeverity,
    MoonPhaseCondition,
    MoonPhaseKey,
    PlanetaryConditionsBundle,
    PlanetaryMotionCondition,
    PlanetaryMotionDirection,
    PlanetarySolarPhaseRelation,
    PlanetarySpeedState,
    PlanetVisibilityCondition,
    PlanetVisibilityKey,
    SolarPhaseRelationKey,
    SolarProximityCondition,
    SolarProximityConditionKey,
    WaxingWaningState,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_scoring_service_adds_advanced_modifiers_to_score_and_result() -> None:
    """Le score accidentel, le total et le resultat incluent les modificateurs."""
    reference = complete_reference()
    planets = (
        PlanetDignityInput("sun", 120, "leo", 10, 1, False),
        PlanetDignityInput("mars", 240, "sagittarius", 10, -0.2, True),
    )
    baseline = PlanetDignityScoringService().calculate(planets, reference)
    advanced = PlanetDignityScoringService().calculate(
        planets,
        reference,
        advanced_planetary_conditions=AdvancedPlanetaryConditionsResult(
            conditions_by_planet={
                "mars": PlanetaryConditionsBundle(
                    planet_key="mars",
                    motion=PlanetaryMotionCondition(
                        planet_key="mars",
                        speed_deg_per_day=-0.2,
                        absolute_speed_deg_per_day=0.2,
                        direction=PlanetaryMotionDirection.RETROGRADE,
                        speed_state=PlanetarySpeedState.VERY_SLOW,
                        is_retrograde=True,
                        is_stationary=False,
                        normalized_speed_ratio=0.3,
                    ),
                    visibility=PlanetVisibilityCondition(
                        planet_key="mars",
                        visibility_key=PlanetVisibilityKey.INVISIBLE,
                        is_visible=False,
                        confidence=ConditionConfidence.HIGH,
                        reason="test_fact",
                    ),
                    solar_phase_relation=PlanetarySolarPhaseRelation(
                        planet_key="mars",
                        relation_key=SolarPhaseRelationKey.ORIENTAL,
                        angular_distance_deg=80,
                        is_oriental=True,
                        is_occidental=False,
                    ),
                )
            }
        ),
    )

    baseline_mars = next(result for result in baseline if result.planet_code == "mars")
    advanced_mars = next(result for result in advanced if result.planet_code == "mars")
    modifier_codes = {modifier.key for modifier in advanced_mars.advanced_condition_modifiers}

    assert modifier_codes == {
        "retrograde_penalty",
        "very_slow_penalty",
        "invisible_penalty",
        "oriental_superior_bonus",
    }
    assert advanced_mars.accidental_score == baseline_mars.accidental_score - 7
    assert advanced_mars.total_score == baseline_mars.total_score - 7
    assert any(
        modifier.category == "motion_condition"
        for modifier in advanced_mars.advanced_condition_modifiers
    )
    assert "advanced_condition_modifiers" not in TypeAdapter(PlanetDignityResult).dump_python(
        advanced_mars,
        mode="json",
    )
    assert "advanced_condition_modifiers" not in str(TypeAdapter(PlanetDignityResult).json_schema())


def test_scoring_service_applies_lunar_phase_only_to_moon() -> None:
    """La phase lunaire ajoute un modificateur seulement a la Lune."""
    reference = complete_reference()
    planets = (
        PlanetDignityInput("sun", 120, "leo", 10, 1, False),
        PlanetDignityInput("moon", 210, "scorpio", 3, 1, False),
        PlanetDignityInput("venus", 40, "taurus", 5, 1, False),
    )

    results = PlanetDignityScoringService().calculate(
        planets,
        reference,
        advanced_planetary_conditions=AdvancedPlanetaryConditionsResult(
            conditions_by_planet={
                "moon": PlanetaryConditionsBundle(planet_key="moon"),
                "venus": PlanetaryConditionsBundle(planet_key="venus"),
            },
            moon_phase=MoonPhaseCondition(
                phase_key=MoonPhaseKey.FULL_MOON,
                sun_moon_angle_deg=180,
                illumination_ratio=1,
                waxing_or_waning=WaxingWaningState.EXACT,
                phase_index=4,
            ),
        ),
    )

    moon = next(result for result in results if result.planet_code == "moon")
    venus = next(result for result in results if result.planet_code == "venus")

    assert _modifier_codes(moon) == {"full_moon_bonus"}
    assert _modifier_codes(venus) == set()


def test_scoring_service_keeps_sun_free_from_combust_penalty() -> None:
    """Le Soleil ne recoit pas de penalite solaire avancee."""
    reference = complete_reference()
    planets = (PlanetDignityInput("sun", 120, "leo", 10, 1, False),)

    result = PlanetDignityScoringService().calculate(
        planets,
        reference,
        advanced_planetary_conditions=AdvancedPlanetaryConditionsResult(
            conditions_by_planet={
                "sun": PlanetaryConditionsBundle(
                    planet_key="sun",
                    solar_proximity=SolarProximityCondition(
                        planet_key="sun",
                        condition_key=SolarProximityConditionKey.COMBUST,
                        sun_distance_deg=1,
                        orb_deg=1,
                        severity=ConditionSeverity.MAJOR,
                        is_active=True,
                    ),
                )
            }
        ),
    )[0]

    assert _modifier_codes(result) == set()


def _modifier_codes(result: object) -> set[str]:
    """Retourne les modificateurs avances exposes par le resultat."""
    return {modifier.key for modifier in result.advanced_condition_modifiers}
