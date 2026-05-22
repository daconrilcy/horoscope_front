"""Fabrique de signaux techniques pour les conditions planetaires avancees."""

from __future__ import annotations

from app.domain.astrology.planetary_conditions.contracts import (
    ConditionConfidence,
    ConditionSeverity,
    MoonPhaseCondition,
    PlanetaryConditionFamily,
    PlanetaryConditionsBundle,
    PlanetaryConditionSignal,
    PlanetaryMotionDirection,
    PlanetVisibilityKey,
    SolarPhaseRelationKey,
    SolarProximityConditionKey,
    WaxingWaningState,
)


def build_planetary_condition_signals(
    *,
    bundle: PlanetaryConditionsBundle,
) -> tuple[PlanetaryConditionSignal, ...]:
    """Construit les signaux factuels rattaches a un bundle planetaire."""
    signals: list[PlanetaryConditionSignal] = []
    if bundle.solar_proximity is not None:
        signals.extend(_build_solar_proximity_signals(bundle))
    if bundle.motion is not None:
        signals.extend(_build_motion_signals(bundle))
    if bundle.solar_phase_relation is not None:
        signals.extend(_build_solar_phase_signals(bundle))
    if bundle.visibility is not None:
        signals.extend(_build_visibility_signals(bundle))
    return tuple(signals)


def build_global_moon_phase_signals(
    moon_phase: MoonPhaseCondition | None,
) -> tuple[PlanetaryConditionSignal, ...]:
    """Construit les signaux globaux derives de la phase lunaire disponible."""
    if moon_phase is None:
        return ()
    if moon_phase.waxing_or_waning is WaxingWaningState.WAXING:
        return (
            PlanetaryConditionSignal(
                planet_key="moon",
                condition_key="waxing_moon",
                condition_family=PlanetaryConditionFamily.LUNAR_PHASE,
                severity=ConditionSeverity.MINOR,
                confidence=ConditionConfidence.HIGH,
                is_active=True,
                value=moon_phase.sun_moon_angle_deg,
                unit="degree",
                metadata={
                    "phase_key": moon_phase.phase_key.value,
                    "phase_index": moon_phase.phase_index,
                },
            ),
        )
    if moon_phase.waxing_or_waning is WaxingWaningState.WANING:
        return (
            PlanetaryConditionSignal(
                planet_key="moon",
                condition_key="waning_moon",
                condition_family=PlanetaryConditionFamily.LUNAR_PHASE,
                severity=ConditionSeverity.MINOR,
                confidence=ConditionConfidence.HIGH,
                is_active=True,
                value=moon_phase.sun_moon_angle_deg,
                unit="degree",
                metadata={
                    "phase_key": moon_phase.phase_key.value,
                    "phase_index": moon_phase.phase_index,
                },
            ),
        )
    return ()


def _build_solar_proximity_signals(
    bundle: PlanetaryConditionsBundle,
) -> tuple[PlanetaryConditionSignal, ...]:
    condition = bundle.solar_proximity
    if condition is None:
        return ()
    if condition.condition_key is SolarProximityConditionKey.COMBUST:
        return (
            PlanetaryConditionSignal(
                planet_key=bundle.planet_key,
                condition_key="combust",
                condition_family=PlanetaryConditionFamily.SOLAR_PROXIMITY,
                severity=condition.severity,
                confidence=ConditionConfidence.HIGH,
                is_active=condition.is_active,
                value=condition.sun_distance_deg,
                unit="degree",
                metadata={"orb_deg": condition.orb_deg},
            ),
        )
    if condition.condition_key is SolarProximityConditionKey.UNDER_BEAMS:
        return (
            PlanetaryConditionSignal(
                planet_key=bundle.planet_key,
                condition_key="under_beams",
                condition_family=PlanetaryConditionFamily.SOLAR_PROXIMITY,
                severity=condition.severity,
                confidence=ConditionConfidence.MEDIUM,
                is_active=condition.is_active,
                value=condition.sun_distance_deg,
                unit="degree",
                metadata={"orb_deg": condition.orb_deg},
            ),
        )
    return ()


def _build_motion_signals(
    bundle: PlanetaryConditionsBundle,
) -> tuple[PlanetaryConditionSignal, ...]:
    condition = bundle.motion
    if condition is None:
        return ()
    if condition.direction is PlanetaryMotionDirection.RETROGRADE:
        return (
            PlanetaryConditionSignal(
                planet_key=bundle.planet_key,
                condition_key="retrograde",
                condition_family=PlanetaryConditionFamily.MOTION,
                severity=ConditionSeverity.MODERATE,
                confidence=ConditionConfidence.HIGH,
                is_active=condition.is_retrograde,
                value=condition.speed_deg_per_day,
                unit="degree_per_day",
                metadata={"speed_state": condition.speed_state.value},
            ),
        )
    if condition.direction is PlanetaryMotionDirection.STATIONARY:
        return (
            PlanetaryConditionSignal(
                planet_key=bundle.planet_key,
                condition_key="stationary",
                condition_family=PlanetaryConditionFamily.MOTION,
                severity=ConditionSeverity.MAJOR,
                confidence=ConditionConfidence.HIGH,
                is_active=condition.is_stationary,
                value=condition.speed_deg_per_day,
                unit="degree_per_day",
                metadata={"speed_state": condition.speed_state.value},
            ),
        )
    return ()


def _build_solar_phase_signals(
    bundle: PlanetaryConditionsBundle,
) -> tuple[PlanetaryConditionSignal, ...]:
    condition = bundle.solar_phase_relation
    if condition is None or bundle.planet_key == "sun":
        return ()
    if condition.relation_key is SolarPhaseRelationKey.ORIENTAL:
        return (
            PlanetaryConditionSignal(
                planet_key=bundle.planet_key,
                condition_key="oriental",
                condition_family=PlanetaryConditionFamily.SOLAR_PHASE,
                severity=ConditionSeverity.MINOR,
                confidence=ConditionConfidence.HIGH,
                is_active=True,
                value=condition.angular_distance_deg,
                unit="degree",
            ),
        )
    if condition.relation_key is SolarPhaseRelationKey.OCCIDENTAL:
        return (
            PlanetaryConditionSignal(
                planet_key=bundle.planet_key,
                condition_key="occidental",
                condition_family=PlanetaryConditionFamily.SOLAR_PHASE,
                severity=ConditionSeverity.MINOR,
                confidence=ConditionConfidence.HIGH,
                is_active=True,
                value=condition.angular_distance_deg,
                unit="degree",
            ),
        )
    return ()


def _build_visibility_signals(
    bundle: PlanetaryConditionsBundle,
) -> tuple[PlanetaryConditionSignal, ...]:
    condition = bundle.visibility
    if condition is None:
        return ()
    if condition.visibility_key is PlanetVisibilityKey.EMERGING:
        return (
            PlanetaryConditionSignal(
                planet_key=bundle.planet_key,
                condition_key="emerging",
                condition_family=PlanetaryConditionFamily.VISIBILITY,
                severity=ConditionSeverity.MINOR,
                confidence=condition.confidence,
                is_active=True,
                value=None,
                unit=None,
                metadata={"visibility_key": condition.visibility_key.value},
            ),
        )
    return ()
