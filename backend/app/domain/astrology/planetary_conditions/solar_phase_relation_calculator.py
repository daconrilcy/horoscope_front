"""Calcul pur de la relation solaire oriental-occidental des planetes."""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite

from app.domain.astrology.planetary_conditions.contracts import (
    PlanetarySolarPhaseRelation,
    SolarPhaseRelationKey,
    SolarPhaseRelationThresholds,
)


def calculate_solar_phase_relation(
    *,
    planet_key: str,
    planet_longitude_deg: float,
    sun_longitude_deg: float,
    thresholds: SolarPhaseRelationThresholds | None = None,
) -> PlanetarySolarPhaseRelation:
    """Classe la relation Soleil-planete depuis l'angle zodiacal relatif.

    L'angle relatif suit `(planete - Soleil) % 360.0`. Par convention de cette
    story, l'opposition exacte a `180.0` degres appartient a l'hemicycle
    occidental.
    """
    active_thresholds = thresholds or SolarPhaseRelationThresholds()
    if planet_key == "sun":
        return _relation(
            planet_key=planet_key,
            relation_key=SolarPhaseRelationKey.CONJUNCT_SOLAR,
            angular_distance_deg=0.0,
        )

    relative_angle = _relative_solar_angle_deg(
        planet_longitude_deg=planet_longitude_deg,
        sun_longitude_deg=sun_longitude_deg,
    )
    if _is_conjunct_solar(
        relative_angle,
        tolerance_deg=active_thresholds.conjunction_tolerance_deg,
    ):
        return _relation(
            planet_key=planet_key,
            relation_key=SolarPhaseRelationKey.CONJUNCT_SOLAR,
            angular_distance_deg=relative_angle,
        )
    if relative_angle <= 180.0:
        return _relation(
            planet_key=planet_key,
            relation_key=SolarPhaseRelationKey.OCCIDENTAL,
            angular_distance_deg=relative_angle,
        )
    return _relation(
        planet_key=planet_key,
        relation_key=SolarPhaseRelationKey.ORIENTAL,
        angular_distance_deg=relative_angle,
    )


def calculate_solar_phase_relations(
    *,
    planet_longitudes_deg: Mapping[str, float],
    sun_longitude_deg: float,
    thresholds: SolarPhaseRelationThresholds | None = None,
) -> Mapping[str, PlanetarySolarPhaseRelation]:
    """Retourne les relations solaires pour plusieurs planetes."""
    return {
        planet_key: calculate_solar_phase_relation(
            planet_key=planet_key,
            planet_longitude_deg=planet_longitude_deg,
            sun_longitude_deg=sun_longitude_deg,
            thresholds=thresholds,
        )
        for planet_key, planet_longitude_deg in planet_longitudes_deg.items()
    }


def _relation(
    *,
    planet_key: str,
    relation_key: SolarPhaseRelationKey,
    angular_distance_deg: float,
) -> PlanetarySolarPhaseRelation:
    return PlanetarySolarPhaseRelation(
        planet_key=planet_key,
        relation_key=relation_key,
        angular_distance_deg=angular_distance_deg,
        is_oriental=relation_key is SolarPhaseRelationKey.ORIENTAL,
        is_occidental=relation_key is SolarPhaseRelationKey.OCCIDENTAL,
    )


def _relative_solar_angle_deg(
    *,
    planet_longitude_deg: float,
    sun_longitude_deg: float,
) -> float:
    return (
        _normalize_longitude_deg(planet_longitude_deg) - _normalize_longitude_deg(sun_longitude_deg)
    ) % 360.0


def _normalize_longitude_deg(longitude_deg: float) -> float:
    if not isfinite(longitude_deg):
        raise ValueError("longitude must be finite")
    return longitude_deg % 360.0


def _is_conjunct_solar(relative_angle_deg: float, *, tolerance_deg: float) -> bool:
    return relative_angle_deg <= tolerance_deg or (360.0 - relative_angle_deg) <= tolerance_deg
