"""Compose les faits solaires amont en condition de visibilite planetaire."""

from __future__ import annotations

from collections.abc import Mapping

from app.domain.astrology.planetary_conditions.contracts import (
    ConditionConfidence,
    PlanetarySolarPhaseRelation,
    PlanetVisibilityCondition,
    PlanetVisibilityKey,
    PlanetVisibilityThresholds,
    SolarPhaseRelationKey,
    SolarProximityCondition,
    SolarProximityConditionKey,
)


def calculate_planet_visibility_condition(
    *,
    planet_key: str,
    solar_proximity_condition: SolarProximityCondition,
    solar_phase_relation: PlanetarySolarPhaseRelation,
    thresholds: PlanetVisibilityThresholds | None = None,
) -> PlanetVisibilityCondition:
    """Retourne la visibilite symbolique depuis les faits solaires deja calcules."""
    active_thresholds = thresholds or PlanetVisibilityThresholds()
    if planet_key == "sun":
        visibility_key = PlanetVisibilityKey.VISIBLE
    elif _is_solar_conjunction(
        solar_proximity_condition=solar_proximity_condition,
        thresholds=active_thresholds,
    ):
        visibility_key = PlanetVisibilityKey.CONJUNCT_SOLAR
    elif solar_proximity_condition.condition_key is SolarProximityConditionKey.COMBUST:
        visibility_key = PlanetVisibilityKey.INVISIBLE
    elif solar_proximity_condition.condition_key is SolarProximityConditionKey.UNDER_BEAMS:
        visibility_key = PlanetVisibilityKey.UNDER_BEAMS
    elif _is_emerging(
        solar_proximity_condition=solar_proximity_condition,
        solar_phase_relation=solar_phase_relation,
        thresholds=active_thresholds,
    ):
        visibility_key = PlanetVisibilityKey.EMERGING
    else:
        visibility_key = PlanetVisibilityKey.VISIBLE

    return PlanetVisibilityCondition(
        planet_key=planet_key,
        visibility_key=visibility_key,
        is_visible=_resolve_visibility_value(visibility_key),
        confidence=_resolve_visibility_confidence(visibility_key),
        reason=_resolve_visibility_reason(visibility_key, planet_key=planet_key),
    )


def calculate_planet_visibility_conditions(
    *,
    solar_proximity_conditions: Mapping[str, SolarProximityCondition],
    solar_phase_relations: Mapping[str, PlanetarySolarPhaseRelation],
    thresholds: PlanetVisibilityThresholds | None = None,
) -> Mapping[str, PlanetVisibilityCondition]:
    """Compose un mapping de visibilite pour chaque cle de proximite fournie."""
    return {
        planet_key: calculate_planet_visibility_condition(
            planet_key=planet_key,
            solar_proximity_condition=solar_proximity_condition,
            solar_phase_relation=solar_phase_relations[planet_key],
            thresholds=thresholds,
        )
        for planet_key, solar_proximity_condition in solar_proximity_conditions.items()
    }


def _is_solar_conjunction(
    *,
    solar_proximity_condition: SolarProximityCondition,
    thresholds: PlanetVisibilityThresholds,
) -> bool:
    return (
        solar_proximity_condition.condition_key is SolarProximityConditionKey.CAZIMI
        or solar_proximity_condition.sun_distance_deg <= thresholds.conjunction_tolerance_deg
    )


def _is_emerging(
    *,
    solar_proximity_condition: SolarProximityCondition,
    solar_phase_relation: PlanetarySolarPhaseRelation,
    thresholds: PlanetVisibilityThresholds,
) -> bool:
    return (
        solar_phase_relation.relation_key is SolarPhaseRelationKey.ORIENTAL
        and solar_proximity_condition.sun_distance_deg > thresholds.under_beams_limit_deg
        and solar_proximity_condition.sun_distance_deg <= thresholds.emerging_limit_deg
    )


def _resolve_visibility_value(visibility_key: PlanetVisibilityKey) -> bool:
    return visibility_key in {
        PlanetVisibilityKey.VISIBLE,
        PlanetVisibilityKey.CONJUNCT_SOLAR,
        PlanetVisibilityKey.EMERGING,
    }


def _resolve_visibility_confidence(
    visibility_key: PlanetVisibilityKey,
) -> ConditionConfidence:
    if visibility_key is PlanetVisibilityKey.CONJUNCT_SOLAR:
        return ConditionConfidence.EXACT
    if visibility_key is PlanetVisibilityKey.EMERGING:
        return ConditionConfidence.MEDIUM
    return ConditionConfidence.HIGH


def _resolve_visibility_reason(
    visibility_key: PlanetVisibilityKey,
    *,
    planet_key: str,
) -> str:
    if planet_key == "sun":
        return "sun_visible"
    return {
        PlanetVisibilityKey.VISIBLE: "outside_visibility_restrictions",
        PlanetVisibilityKey.CONJUNCT_SOLAR: "solar_conjunction",
        PlanetVisibilityKey.INVISIBLE: "combust",
        PlanetVisibilityKey.UNDER_BEAMS: "under_beams",
        PlanetVisibilityKey.EMERGING: "planet_exiting_solar_beams",
    }[visibility_key]
