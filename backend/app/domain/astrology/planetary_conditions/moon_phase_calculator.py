"""Calcul pur de la phase lunaire natale depuis deux longitudes."""

from __future__ import annotations

from math import cos, isclose, isfinite, radians

from app.domain.astrology.planetary_conditions.contracts import (
    MoonPhaseCondition,
    MoonPhaseKey,
    WaxingWaningState,
)

_PHASE_INDEX_BY_KEY = {
    MoonPhaseKey.NEW_MOON: 0,
    MoonPhaseKey.WAXING_CRESCENT: 1,
    MoonPhaseKey.FIRST_QUARTER: 2,
    MoonPhaseKey.WAXING_GIBBOUS: 3,
    MoonPhaseKey.FULL_MOON: 4,
    MoonPhaseKey.WANING_GIBBOUS: 5,
    MoonPhaseKey.LAST_QUARTER: 6,
    MoonPhaseKey.WANING_CRESCENT: 7,
    MoonPhaseKey.BALSAMIC: 8,
}
_ANGLE_SNAP_TOLERANCE_DEG = 1e-9


def calculate_moon_phase_condition(
    *,
    moon_longitude_deg: float,
    sun_longitude_deg: float,
) -> MoonPhaseCondition:
    """Retourne le fait contractuel de phase lunaire pour des longitudes finies.

    L'illumination expose une approximation geometrique suffisante pour classer
    le theme natal; elle ne remplace pas un calcul photometrique specialise.
    """
    sun_moon_angle_deg = _compute_sun_moon_angle_deg(
        moon_longitude_deg=moon_longitude_deg,
        sun_longitude_deg=sun_longitude_deg,
    )
    phase_key = _resolve_phase_key(sun_moon_angle_deg)
    return MoonPhaseCondition(
        phase_key=phase_key,
        sun_moon_angle_deg=sun_moon_angle_deg,
        illumination_ratio=_compute_illumination_ratio(sun_moon_angle_deg),
        waxing_or_waning=_resolve_waxing_waning(sun_moon_angle_deg),
        phase_index=_resolve_phase_index(phase_key),
    )


def _compute_sun_moon_angle_deg(
    *,
    moon_longitude_deg: float,
    sun_longitude_deg: float,
) -> float:
    normalized_moon_longitude_deg = _normalize_longitude_deg(moon_longitude_deg)
    normalized_sun_longitude_deg = _normalize_longitude_deg(sun_longitude_deg)
    return _snap_major_angle((normalized_moon_longitude_deg - normalized_sun_longitude_deg) % 360.0)


def _normalize_longitude_deg(longitude_deg: float) -> float:
    _ensure_finite_longitude(longitude_deg)
    return longitude_deg % 360.0


def _ensure_finite_longitude(longitude_deg: float) -> None:
    if not isfinite(longitude_deg):
        raise ValueError("longitude must be finite")


def _snap_major_angle(sun_moon_angle_deg: float) -> float:
    if isclose(
        sun_moon_angle_deg,
        0.0,
        rel_tol=0.0,
        abs_tol=_ANGLE_SNAP_TOLERANCE_DEG,
    ):
        return 0.0
    if isclose(
        sun_moon_angle_deg,
        180.0,
        rel_tol=0.0,
        abs_tol=_ANGLE_SNAP_TOLERANCE_DEG,
    ):
        return 180.0
    if isclose(
        sun_moon_angle_deg,
        360.0,
        rel_tol=0.0,
        abs_tol=_ANGLE_SNAP_TOLERANCE_DEG,
    ):
        return 0.0
    return sun_moon_angle_deg


def _compute_illumination_ratio(sun_moon_angle_deg: float) -> float:
    return (1.0 - cos(radians(sun_moon_angle_deg))) / 2.0


def _resolve_waxing_waning(sun_moon_angle_deg: float) -> WaxingWaningState:
    if sun_moon_angle_deg in (0.0, 180.0):
        return WaxingWaningState.EXACT
    if sun_moon_angle_deg < 180.0:
        return WaxingWaningState.WAXING
    return WaxingWaningState.WANING


def _resolve_phase_key(sun_moon_angle_deg: float) -> MoonPhaseKey:
    if sun_moon_angle_deg >= 337.5 or sun_moon_angle_deg < 22.5:
        return MoonPhaseKey.NEW_MOON
    if 157.5 <= sun_moon_angle_deg < 202.5:
        return MoonPhaseKey.FULL_MOON
    if 315.0 <= sun_moon_angle_deg < 337.5:
        return MoonPhaseKey.BALSAMIC
    if sun_moon_angle_deg < 67.5:
        return MoonPhaseKey.WAXING_CRESCENT
    if sun_moon_angle_deg < 112.5:
        return MoonPhaseKey.FIRST_QUARTER
    if sun_moon_angle_deg < 157.5:
        return MoonPhaseKey.WAXING_GIBBOUS
    if sun_moon_angle_deg < 247.5:
        return MoonPhaseKey.WANING_GIBBOUS
    if sun_moon_angle_deg < 292.5:
        return MoonPhaseKey.LAST_QUARTER
    return MoonPhaseKey.WANING_CRESCENT


def _resolve_phase_index(phase_key: MoonPhaseKey) -> int:
    return _PHASE_INDEX_BY_KEY[phase_key]
