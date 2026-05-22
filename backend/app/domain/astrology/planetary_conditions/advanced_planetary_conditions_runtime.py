"""Orchestration pure des conditions planetaires avancees natales."""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from typing import Protocol

from app.domain.astrology.planetary_conditions.contracts import (
    AdvancedPlanetaryConditionsResult,
    MoonPhaseCondition,
    PlanetaryConditionsBundle,
)
from app.domain.astrology.planetary_conditions.moon_phase_calculator import (
    calculate_moon_phase_condition,
)
from app.domain.astrology.planetary_conditions.planetary_motion_calculator import (
    calculate_planetary_motion_conditions,
)
from app.domain.astrology.planetary_conditions.planetary_motion_profiles import (
    DEFAULT_PLANETARY_MOTION_PROFILES,
)
from app.domain.astrology.planetary_conditions.planetary_visibility_calculator import (
    calculate_planet_visibility_conditions,
)
from app.domain.astrology.planetary_conditions.signal_factory import (
    build_global_moon_phase_signals,
    build_planetary_condition_signals,
)
from app.domain.astrology.planetary_conditions.solar_phase_relation_calculator import (
    calculate_solar_phase_relations,
)
from app.domain.astrology.planetary_conditions.solar_proximity_calculator import (
    calculate_solar_proximity_conditions,
)


class _PlanetPositionLike(Protocol):
    longitude: float


def calculate_advanced_planetary_conditions(
    *,
    planetary_positions: Mapping[str, _PlanetPositionLike],
    planetary_speeds_deg_per_day: Mapping[str, float],
) -> AdvancedPlanetaryConditionsResult:
    """Assemble les calculateurs purs en resultat global de conditions avancees."""
    planet_longitudes = _extract_planet_longitudes(planetary_positions)
    sun_longitude = planet_longitudes.get("sun")
    if sun_longitude is None:
        return AdvancedPlanetaryConditionsResult(conditions_by_planet={})

    solar_proximity_conditions = calculate_solar_proximity_conditions(
        planet_longitudes_deg=planet_longitudes,
        sun_longitude_deg=sun_longitude,
    )
    solar_phase_relations = calculate_solar_phase_relations(
        planet_longitudes_deg=planet_longitudes,
        sun_longitude_deg=sun_longitude,
    )
    motion_conditions = calculate_planetary_motion_conditions(
        speeds_by_planet=_supported_speeds(planetary_speeds_deg_per_day),
        profiles_by_planet=DEFAULT_PLANETARY_MOTION_PROFILES,
    )
    visibility_conditions = calculate_planet_visibility_conditions(
        solar_proximity_conditions=solar_proximity_conditions,
        solar_phase_relations=solar_phase_relations,
    )
    moon_phase = _calculate_moon_phase(planet_longitudes)

    conditions_by_planet: dict[str, PlanetaryConditionsBundle] = {}
    collected_signals = []
    for planet_key in planet_longitudes:
        partial_bundle = PlanetaryConditionsBundle(
            planet_key=planet_key,
            solar_proximity=solar_proximity_conditions.get(planet_key),
            solar_phase_relation=solar_phase_relations.get(planet_key),
            motion=motion_conditions.get(planet_key),
            visibility=visibility_conditions.get(planet_key),
        )
        bundle_signals = build_planetary_condition_signals(bundle=partial_bundle)
        bundle = PlanetaryConditionsBundle(
            planet_key=partial_bundle.planet_key,
            solar_proximity=partial_bundle.solar_proximity,
            solar_phase_relation=partial_bundle.solar_phase_relation,
            motion=partial_bundle.motion,
            visibility=partial_bundle.visibility,
            signals=bundle_signals,
        )
        conditions_by_planet[planet_key] = bundle
        collected_signals.extend(bundle_signals)

    global_signals = build_global_moon_phase_signals(moon_phase)
    collected_signals.extend(global_signals)
    return AdvancedPlanetaryConditionsResult(
        conditions_by_planet=conditions_by_planet,
        moon_phase=moon_phase,
        signals=tuple(collected_signals),
    )


def _extract_planet_longitudes(
    planetary_positions: Mapping[str, _PlanetPositionLike],
) -> dict[str, float]:
    return {
        planet_key: position.longitude
        for planet_key, position in planetary_positions.items()
        if isfinite(position.longitude)
    }


def _supported_speeds(
    planetary_speeds_deg_per_day: Mapping[str, float],
) -> dict[str, float]:
    return {
        planet_key: speed
        for planet_key, speed in planetary_speeds_deg_per_day.items()
        if planet_key in DEFAULT_PLANETARY_MOTION_PROFILES and isfinite(speed)
    }


def _calculate_moon_phase(
    planet_longitudes: Mapping[str, float],
) -> MoonPhaseCondition | None:
    sun_longitude = planet_longitudes.get("sun")
    moon_longitude = planet_longitudes.get("moon")
    if sun_longitude is None or moon_longitude is None:
        return None
    return calculate_moon_phase_condition(
        moon_longitude_deg=moon_longitude,
        sun_longitude_deg=sun_longitude,
    )
