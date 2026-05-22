"""Tests du runtime pur des conditions planetaires avancees."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.astrology.planetary_conditions import (
    MoonPhaseKey,
    PlanetaryMotionDirection,
    PlanetVisibilityKey,
    SolarProximityConditionKey,
    WaxingWaningState,
    calculate_advanced_planetary_conditions,
)


@dataclass(frozen=True, slots=True)
class _Position:
    longitude: float


def test_runtime_builds_planet_bundles_global_moon_phase_and_signals() -> None:
    """Le runtime assemble les calculateurs CS-209 a CS-213 sans recalcul externe."""
    result = calculate_advanced_planetary_conditions(
        planetary_positions={
            "sun": _Position(100.0),
            "moon": _Position(190.0),
            "venus": _Position(106.0),
            "mercury": _Position(110.0),
            "mars": _Position(240.0),
            "jupiter": _Position(84.0),
            "saturn": _Position(300.0),
        },
        planetary_speeds_deg_per_day={
            "sun": 0.98,
            "moon": 13.2,
            "venus": 1.18,
            "mercury": 1.1,
            "mars": -0.2,
            "jupiter": 0.08,
            "saturn": 0.0,
        },
    )

    assert set(result.conditions_by_planet) == {
        "sun",
        "moon",
        "venus",
        "mercury",
        "mars",
        "jupiter",
        "saturn",
    }
    assert (
        result.conditions_by_planet["sun"].visibility.visibility_key is PlanetVisibilityKey.VISIBLE
    )
    assert (
        result.conditions_by_planet["venus"].solar_proximity.condition_key
        is SolarProximityConditionKey.COMBUST
    )
    assert (
        result.conditions_by_planet["mercury"].solar_proximity.condition_key
        is SolarProximityConditionKey.UNDER_BEAMS
    )
    assert (
        result.conditions_by_planet["mars"].motion.direction is PlanetaryMotionDirection.RETROGRADE
    )
    assert (
        result.conditions_by_planet["saturn"].motion.direction
        is PlanetaryMotionDirection.STATIONARY
    )
    assert (
        result.conditions_by_planet["jupiter"].visibility.visibility_key
        is PlanetVisibilityKey.EMERGING
    )
    assert result.moon_phase is not None
    assert result.moon_phase.phase_key is MoonPhaseKey.FIRST_QUARTER
    assert result.moon_phase.waxing_or_waning is WaxingWaningState.WAXING

    signal_keys = {signal.condition_key for signal in result.signals}
    assert {
        "combust",
        "under_beams",
        "retrograde",
        "stationary",
        "emerging",
        "oriental",
        "occidental",
        "waxing_moon",
    } <= signal_keys
    assert all(signal.is_active for signal in result.signals)
    assert tuple(result.conditions_by_planet["venus"].signals)


def test_runtime_tolerates_missing_motion_speed_without_dropping_other_facts() -> None:
    """Une vitesse absente laisse seulement le mouvement de la planete a None."""
    result = calculate_advanced_planetary_conditions(
        planetary_positions={
            "sun": _Position(0.0),
            "moon": _Position(250.0),
            "mars": _Position(20.0),
        },
        planetary_speeds_deg_per_day={"sun": 0.98},
    )

    mars_bundle = result.conditions_by_planet["mars"]
    assert mars_bundle.motion is None
    assert mars_bundle.solar_proximity is not None
    assert mars_bundle.solar_phase_relation is not None
    assert mars_bundle.visibility is not None
    assert result.moon_phase is not None
    assert result.signals


def test_runtime_keeps_global_lunar_signals_absent_without_luminaries() -> None:
    """La phase lunaire globale reste optionnelle quand une lumiere manque."""
    result = calculate_advanced_planetary_conditions(
        planetary_positions={
            "sun": _Position(0.0),
            "venus": _Position(40.0),
        },
        planetary_speeds_deg_per_day={},
    )

    assert result.moon_phase is None
    assert "waxing_moon" not in {signal.condition_key for signal in result.signals}
    assert "waning_moon" not in {signal.condition_key for signal in result.signals}


def test_runtime_returns_empty_result_without_sun_reference() -> None:
    """Le Soleil absent bloque seulement l'orchestration solaire globale."""
    result = calculate_advanced_planetary_conditions(
        planetary_positions={"moon": _Position(120.0)},
        planetary_speeds_deg_per_day={"moon": 13.0},
    )

    assert result.conditions_by_planet == {}
    assert result.moon_phase is None
    assert result.signals == ()
