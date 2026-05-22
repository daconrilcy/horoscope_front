"""Resolution pure des profils symboliques depuis des faits planetaires."""

from __future__ import annotations

from app.domain.astrology.planetary_conditions.contracts import (
    MoonPhaseCondition,
    MoonPhaseKey,
    PlanetaryConditionsBundle,
    PlanetaryMotionDirection,
    PlanetVisibilityKey,
    SolarPhaseRelationKey,
    SolarProximityConditionKey,
)

from .advanced_condition_profile_catalog import ADVANCED_CONDITION_PROFILE_CATALOG
from .contracts import AdvancedConditionInterpretationProfile


def resolve_advanced_condition_profiles(
    *,
    bundle: PlanetaryConditionsBundle,
    moon_phase: MoonPhaseCondition | None,
    tradition_key: str | None = None,
) -> tuple[AdvancedConditionInterpretationProfile, ...]:
    """Retourne les profils applicables aux conditions deja calculees."""
    profiles: list[AdvancedConditionInterpretationProfile] = []
    for condition_key in _condition_keys(bundle=bundle, moon_phase=moon_phase):
        profiles.extend(
            _profiles_for_condition(
                condition_key=condition_key,
                planet_key=bundle.planet_key,
                tradition_key=tradition_key,
            )
        )
    return tuple(profiles)


def _condition_keys(
    *,
    bundle: PlanetaryConditionsBundle,
    moon_phase: MoonPhaseCondition | None,
) -> tuple[str, ...]:
    collected: list[str] = []
    _append_once(collected, _solar_proximity_key(bundle))
    _append_once(collected, _motion_key(bundle))
    _append_once(collected, _visibility_key(bundle))
    _append_once(collected, _solar_phase_key(bundle))
    _append_once(collected, _moon_phase_key(bundle, moon_phase))
    return tuple(collected)


def _append_once(collected: list[str], condition_key: str | None) -> None:
    if condition_key is not None and condition_key not in collected:
        collected.append(condition_key)


def _solar_proximity_key(bundle: PlanetaryConditionsBundle) -> str | None:
    condition = bundle.solar_proximity
    if condition is None or not condition.is_active:
        return None
    if condition.condition_key in {
        SolarProximityConditionKey.CAZIMI,
        SolarProximityConditionKey.COMBUST,
        SolarProximityConditionKey.UNDER_BEAMS,
    }:
        return condition.condition_key.value
    return None


def _motion_key(bundle: PlanetaryConditionsBundle) -> str | None:
    condition = bundle.motion
    if condition is None:
        return None
    if condition.direction in {
        PlanetaryMotionDirection.RETROGRADE,
        PlanetaryMotionDirection.STATIONARY,
    }:
        return condition.direction.value
    return None


def _visibility_key(bundle: PlanetaryConditionsBundle) -> str | None:
    condition = bundle.visibility
    if condition is None:
        return None
    if condition.visibility_key in {
        PlanetVisibilityKey.INVISIBLE,
        PlanetVisibilityKey.UNDER_BEAMS,
        PlanetVisibilityKey.EMERGING,
    }:
        return condition.visibility_key.value
    return None


def _solar_phase_key(bundle: PlanetaryConditionsBundle) -> str | None:
    condition = bundle.solar_phase_relation
    if condition is None:
        return None
    if condition.relation_key in {
        SolarPhaseRelationKey.ORIENTAL,
        SolarPhaseRelationKey.OCCIDENTAL,
    }:
        return condition.relation_key.value
    return None


def _moon_phase_key(
    bundle: PlanetaryConditionsBundle,
    moon_phase: MoonPhaseCondition | None,
) -> str | None:
    if bundle.planet_key != "moon" or moon_phase is None:
        return None
    if moon_phase.phase_key in {MoonPhaseKey.FULL_MOON, MoonPhaseKey.NEW_MOON}:
        return moon_phase.phase_key.value
    return None


def _profiles_for_condition(
    *,
    condition_key: str,
    planet_key: str,
    tradition_key: str | None,
) -> tuple[AdvancedConditionInterpretationProfile, ...]:
    normalized_planet = planet_key.strip().lower()
    normalized_tradition = _normalize_optional(tradition_key)
    priority = (
        (
            (normalized_planet, normalized_tradition),
            (normalized_planet, None),
            (None, normalized_tradition),
            (None, None),
        )
        if normalized_tradition is not None
        else ((normalized_planet, None), (None, None))
    )
    for candidate_planet, candidate_tradition in priority:
        matches = tuple(
            profile
            for profile in ADVANCED_CONDITION_PROFILE_CATALOG
            if profile.condition_key == condition_key
            and _normalize_optional(profile.planet_key) == candidate_planet
            and _normalize_optional(profile.tradition_key) == candidate_tradition
        )
        if matches:
            return matches
    return ()


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized or None
