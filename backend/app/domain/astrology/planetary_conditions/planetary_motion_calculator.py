"""Calcul pur des conditions de mouvement planetaire."""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite

from app.domain.astrology.planetary_conditions.contracts import (
    PlanetaryMotionCondition,
    PlanetaryMotionDirection,
    PlanetaryMotionProfile,
    PlanetarySpeedState,
)


def calculate_planetary_motion_condition(
    *,
    planet_key: str,
    speed_deg_per_day: float,
    profile: PlanetaryMotionProfile,
) -> PlanetaryMotionCondition:
    """Classe la direction et la vitesse relative d'une planete."""
    if not isfinite(speed_deg_per_day):
        raise ValueError("speed_deg_per_day must be finite")
    if profile.planet_key != planet_key:
        raise ValueError("planet_key must match the planetary motion profile")

    absolute_speed = abs(speed_deg_per_day)
    direction = _motion_direction(
        speed_deg_per_day=speed_deg_per_day,
        stationary_threshold_abs=profile.stationary_threshold_abs,
    )
    normalized_ratio = _normalized_speed_ratio(
        absolute_speed_deg_per_day=absolute_speed,
        mean_speed_deg_per_day=profile.mean_speed_deg_per_day,
    )

    return PlanetaryMotionCondition(
        planet_key=planet_key,
        speed_deg_per_day=speed_deg_per_day,
        absolute_speed_deg_per_day=absolute_speed,
        direction=direction,
        speed_state=_speed_state(normalized_ratio, profile),
        is_retrograde=direction is PlanetaryMotionDirection.RETROGRADE,
        is_stationary=direction is PlanetaryMotionDirection.STATIONARY,
        normalized_speed_ratio=normalized_ratio,
    )


def calculate_planetary_motion_conditions(
    *,
    speeds_by_planet: Mapping[str, float],
    profiles_by_planet: Mapping[str, PlanetaryMotionProfile],
) -> Mapping[str, PlanetaryMotionCondition]:
    """Retourne les conditions de mouvement pour plusieurs planetes."""
    conditions: dict[str, PlanetaryMotionCondition] = {}
    for planet_key, speed_deg_per_day in speeds_by_planet.items():
        try:
            profile = profiles_by_planet[planet_key]
        except KeyError as exc:
            raise ValueError(f"missing planetary motion profile for {planet_key}") from exc
        conditions[planet_key] = calculate_planetary_motion_condition(
            planet_key=planet_key,
            speed_deg_per_day=speed_deg_per_day,
            profile=profile,
        )
    return conditions


def _motion_direction(
    *,
    speed_deg_per_day: float,
    stationary_threshold_abs: float,
) -> PlanetaryMotionDirection:
    if abs(speed_deg_per_day) <= stationary_threshold_abs:
        return PlanetaryMotionDirection.STATIONARY
    if speed_deg_per_day < 0:
        return PlanetaryMotionDirection.RETROGRADE
    return PlanetaryMotionDirection.DIRECT


def _normalized_speed_ratio(
    *,
    absolute_speed_deg_per_day: float,
    mean_speed_deg_per_day: float,
) -> float | None:
    if mean_speed_deg_per_day <= 0:
        return None
    return absolute_speed_deg_per_day / mean_speed_deg_per_day


def _speed_state(
    normalized_speed_ratio: float | None,
    profile: PlanetaryMotionProfile,
) -> PlanetarySpeedState:
    if normalized_speed_ratio is None:
        return PlanetarySpeedState.UNKNOWN
    if normalized_speed_ratio < profile.very_slow_ratio_threshold:
        return PlanetarySpeedState.VERY_SLOW
    if normalized_speed_ratio < profile.slow_ratio_threshold:
        return PlanetarySpeedState.SLOW
    if normalized_speed_ratio <= profile.fast_ratio_threshold:
        return PlanetarySpeedState.NORMAL
    if normalized_speed_ratio <= profile.very_fast_ratio_threshold:
        return PlanetarySpeedState.FAST
    return PlanetarySpeedState.VERY_FAST
