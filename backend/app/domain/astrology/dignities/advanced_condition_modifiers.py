"""Conversion pure des conditions avancees en modificateurs accidentels."""

from __future__ import annotations

from app.domain.astrology.dignities.advanced_condition_modifier_profiles import (
    ADVANCED_CONDITION_MODIFIER_PROFILES,
    AdvancedConditionModifierProfile,
)
from app.domain.astrology.dignities.contracts import AccidentalDignityModifier
from app.domain.astrology.planetary_conditions.contracts import (
    MoonPhaseCondition,
    MoonPhaseKey,
    PlanetaryConditionsBundle,
    PlanetaryMotionDirection,
    PlanetarySpeedState,
    PlanetVisibilityKey,
    SolarPhaseRelationKey,
    SolarProximityConditionKey,
)

_SUPERIOR_PLANETS = frozenset({"mars", "jupiter", "saturn"})


def calculate_advanced_condition_modifiers(
    *,
    bundle: PlanetaryConditionsBundle,
    moon_phase: MoonPhaseCondition | None,
) -> tuple[AccidentalDignityModifier, ...]:
    """Retourne les modificateurs accidentels deduits de faits deja calcules."""
    modifiers = [
        *_solar_condition_modifiers(bundle),
        *_motion_condition_modifiers(bundle),
        *_visibility_condition_modifiers(bundle),
        *_solar_phase_condition_modifiers(bundle),
        *_lunar_condition_modifiers(bundle, moon_phase),
    ]
    return tuple(modifiers)


def _solar_condition_modifiers(
    bundle: PlanetaryConditionsBundle,
) -> tuple[AccidentalDignityModifier, ...]:
    solar_proximity = bundle.solar_proximity
    if solar_proximity is None or not solar_proximity.is_active:
        return ()
    condition_key = solar_proximity.condition_key
    if condition_key is SolarProximityConditionKey.CAZIMI:
        return (_modifier("cazimi_bonus", "solar_proximity:cazimi"),)
    if condition_key is SolarProximityConditionKey.COMBUST and bundle.planet_key != "sun":
        return (_modifier("combust_penalty", "solar_proximity:combust"),)
    if condition_key is SolarProximityConditionKey.UNDER_BEAMS:
        return (_modifier("under_beams_penalty", "solar_proximity:under_beams"),)
    return ()


def _motion_condition_modifiers(
    bundle: PlanetaryConditionsBundle,
) -> tuple[AccidentalDignityModifier, ...]:
    motion = bundle.motion
    if motion is None:
        return ()
    modifiers: list[AccidentalDignityModifier] = []
    if motion.direction is PlanetaryMotionDirection.RETROGRADE or motion.is_retrograde:
        modifiers.append(_modifier("retrograde_penalty", "motion:retrograde"))
    if motion.direction is PlanetaryMotionDirection.STATIONARY or motion.is_stationary:
        modifiers.append(_modifier("stationary_bonus", "motion:stationary"))
    if motion.speed_state is PlanetarySpeedState.VERY_FAST:
        modifiers.append(_modifier("very_fast_bonus", "motion:very_fast"))
    if motion.speed_state is PlanetarySpeedState.VERY_SLOW:
        modifiers.append(_modifier("very_slow_penalty", "motion:very_slow"))
    return tuple(modifiers)


def _visibility_condition_modifiers(
    bundle: PlanetaryConditionsBundle,
) -> tuple[AccidentalDignityModifier, ...]:
    visibility = bundle.visibility
    if visibility is None:
        return ()
    if visibility.visibility_key is PlanetVisibilityKey.INVISIBLE:
        return (_modifier("invisible_penalty", "visibility:invisible"),)
    if visibility.visibility_key is PlanetVisibilityKey.EMERGING:
        return (_modifier("emerging_bonus", "visibility:emerging"),)
    return ()


def _solar_phase_condition_modifiers(
    bundle: PlanetaryConditionsBundle,
) -> tuple[AccidentalDignityModifier, ...]:
    phase_relation = bundle.solar_phase_relation
    if phase_relation is None or bundle.planet_key not in _SUPERIOR_PLANETS:
        return ()
    if phase_relation.relation_key is SolarPhaseRelationKey.ORIENTAL:
        return (_modifier("oriental_superior_bonus", "solar_phase:oriental_superior"),)
    if phase_relation.relation_key is SolarPhaseRelationKey.OCCIDENTAL:
        return (_modifier("occidental_superior_penalty", "solar_phase:occidental_superior"),)
    return ()


def _lunar_condition_modifiers(
    bundle: PlanetaryConditionsBundle,
    moon_phase: MoonPhaseCondition | None,
) -> tuple[AccidentalDignityModifier, ...]:
    if bundle.planet_key != "moon" or moon_phase is None:
        return ()
    if moon_phase.phase_key is MoonPhaseKey.FULL_MOON:
        return (_modifier("full_moon_bonus", "lunar_phase:full_moon"),)
    if moon_phase.phase_key is MoonPhaseKey.NEW_MOON:
        return (_modifier("new_moon_penalty", "lunar_phase:new_moon"),)
    return ()


def _modifier(key: str, reason: str) -> AccidentalDignityModifier:
    profile = _profile(key)
    return AccidentalDignityModifier(
        key=profile.condition_key,
        category=profile.category,
        score_delta=profile.score_delta,
        reason=reason,
        source="advanced_condition_modifier",
    )


def _profile(key: str) -> AdvancedConditionModifierProfile:
    return ADVANCED_CONDITION_MODIFIER_PROFILES[key]
