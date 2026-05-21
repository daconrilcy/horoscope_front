"""Calcul pur des etats de proximite solaire des planetes."""

from __future__ import annotations

from collections.abc import Mapping

from app.domain.astrology.planetary_conditions.contracts import (
    ConditionSeverity,
    SolarProximityCondition,
    SolarProximityConditionKey,
    SolarProximityThresholds,
)


def calculate_solar_proximity_condition(
    *,
    planet_key: str,
    planet_longitude_deg: float,
    sun_longitude_deg: float,
    thresholds: SolarProximityThresholds | None = None,
) -> SolarProximityCondition:
    """Classe la proximite solaire d'une planete selon des seuils ordonnes."""
    active_thresholds = thresholds or SolarProximityThresholds()
    if planet_key == "sun":
        return SolarProximityCondition(
            planet_key=planet_key,
            condition_key=SolarProximityConditionKey.NONE,
            sun_distance_deg=0.0,
            orb_deg=None,
            severity=ConditionSeverity.NONE,
            is_active=False,
        )

    sun_distance_deg = _angular_distance_deg(planet_longitude_deg, sun_longitude_deg)
    if sun_distance_deg <= active_thresholds.cazimi_max_distance_deg:
        return _active_condition(
            planet_key=planet_key,
            condition_key=SolarProximityConditionKey.CAZIMI,
            sun_distance_deg=sun_distance_deg,
            orb_deg=active_thresholds.cazimi_max_distance_deg,
            severity=ConditionSeverity.EXTREME,
        )
    if sun_distance_deg <= active_thresholds.combust_max_distance_deg:
        return _active_condition(
            planet_key=planet_key,
            condition_key=SolarProximityConditionKey.COMBUST,
            sun_distance_deg=sun_distance_deg,
            orb_deg=active_thresholds.combust_max_distance_deg,
            severity=ConditionSeverity.MAJOR,
        )
    if sun_distance_deg <= active_thresholds.under_beams_max_distance_deg:
        return _active_condition(
            planet_key=planet_key,
            condition_key=SolarProximityConditionKey.UNDER_BEAMS,
            sun_distance_deg=sun_distance_deg,
            orb_deg=active_thresholds.under_beams_max_distance_deg,
            severity=ConditionSeverity.MODERATE,
        )
    return SolarProximityCondition(
        planet_key=planet_key,
        condition_key=SolarProximityConditionKey.NONE,
        sun_distance_deg=sun_distance_deg,
        orb_deg=None,
        severity=ConditionSeverity.NONE,
        is_active=False,
    )


def calculate_solar_proximity_conditions(
    *,
    planet_longitudes_deg: Mapping[str, float],
    sun_longitude_deg: float,
    thresholds: SolarProximityThresholds | None = None,
) -> Mapping[str, SolarProximityCondition]:
    """Retourne les conditions solaires de plusieurs planetes sans effet de bord."""
    return {
        planet_key: calculate_solar_proximity_condition(
            planet_key=planet_key,
            planet_longitude_deg=planet_longitude_deg,
            sun_longitude_deg=sun_longitude_deg,
            thresholds=thresholds,
        )
        for planet_key, planet_longitude_deg in planet_longitudes_deg.items()
    }


def _active_condition(
    *,
    planet_key: str,
    condition_key: SolarProximityConditionKey,
    sun_distance_deg: float,
    orb_deg: float,
    severity: ConditionSeverity,
) -> SolarProximityCondition:
    return SolarProximityCondition(
        planet_key=planet_key,
        condition_key=condition_key,
        sun_distance_deg=sun_distance_deg,
        orb_deg=orb_deg,
        severity=severity,
        is_active=True,
    )


def _normalize_longitude_deg(longitude_deg: float) -> float:
    return longitude_deg % 360.0


def _angular_distance_deg(first_longitude_deg: float, second_longitude_deg: float) -> float:
    normalized_first = _normalize_longitude_deg(first_longitude_deg)
    normalized_second = _normalize_longitude_deg(second_longitude_deg)
    direct_distance = abs(normalized_first - normalized_second)
    return min(direct_distance, 360.0 - direct_distance)
