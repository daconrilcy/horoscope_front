"""Tests du calculateur pur de phase lunaire natale."""

from math import inf, nan

import pytest

from app.domain.astrology.planetary_conditions import (
    MoonPhaseCondition,
    MoonPhaseKey,
    WaxingWaningState,
    calculate_moon_phase_condition,
)


def test_calculator_is_public_and_returns_contract() -> None:
    """La fonction publique retourne le contrat lunaire existant."""
    condition = calculate_moon_phase_condition(
        moon_longitude_deg=42.0,
        sun_longitude_deg=42.0,
    )

    assert isinstance(condition, MoonPhaseCondition)
    assert condition.phase_key is MoonPhaseKey.NEW_MOON
    assert condition.sun_moon_angle_deg == 0.0
    assert condition.illumination_ratio == 0.0
    assert condition.waxing_or_waning is WaxingWaningState.EXACT
    assert condition.phase_index == 0


def test_calculator_uses_moon_minus_sun_angle_across_zero() -> None:
    """L'angle relatif suit exactement `(Lune - Soleil) % 360`."""
    first = calculate_moon_phase_condition(moon_longitude_deg=10.0, sun_longitude_deg=350.0)
    second = calculate_moon_phase_condition(moon_longitude_deg=2.0, sun_longitude_deg=358.0)

    assert first.sun_moon_angle_deg == 20.0
    assert second.sun_moon_angle_deg == 4.0


def test_calculator_normalizes_input_longitudes() -> None:
    """Les longitudes hors cercle sont reduites avant le calcul."""
    wrapped_positive = calculate_moon_phase_condition(
        moon_longitude_deg=361.0,
        sun_longitude_deg=0.0,
    )
    wrapped_negative = calculate_moon_phase_condition(
        moon_longitude_deg=-1.0,
        sun_longitude_deg=0.0,
    )
    wrapped_full_turn = calculate_moon_phase_condition(
        moon_longitude_deg=720.0,
        sun_longitude_deg=0.0,
    )

    assert wrapped_positive.sun_moon_angle_deg == 1.0
    assert wrapped_negative.sun_moon_angle_deg == 359.0
    assert wrapped_full_turn.sun_moon_angle_deg == 0.0
    assert wrapped_full_turn.waxing_or_waning is WaxingWaningState.EXACT


def test_decimal_wrapped_longitudes_snap_major_angles() -> None:
    """Les artefacts flottants proches des angles majeurs restent exacts."""
    new_moon = calculate_moon_phase_condition(
        moon_longitude_deg=360.1,
        sun_longitude_deg=0.1,
    )
    full_moon = calculate_moon_phase_condition(
        moon_longitude_deg=540.1,
        sun_longitude_deg=0.1,
    )

    assert new_moon.sun_moon_angle_deg == 0.0
    assert new_moon.waxing_or_waning is WaxingWaningState.EXACT
    assert new_moon.phase_key is MoonPhaseKey.NEW_MOON
    assert full_moon.sun_moon_angle_deg == 180.0
    assert full_moon.waxing_or_waning is WaxingWaningState.EXACT
    assert full_moon.phase_key is MoonPhaseKey.FULL_MOON


def test_major_angle_snap_uses_absolute_tolerance_only() -> None:
    """La tolerance de snap ne s'elargit pas avec une tolerance relative."""
    near_full_moon = calculate_moon_phase_condition(
        moon_longitude_deg=180.00000001,
        sun_longitude_deg=0.0,
    )

    assert near_full_moon.sun_moon_angle_deg == pytest.approx(180.00000001)
    assert near_full_moon.waxing_or_waning is WaxingWaningState.WANING
    assert near_full_moon.phase_key is MoonPhaseKey.FULL_MOON


@pytest.mark.parametrize(
    ("angle_deg", "expected_state"),
    [
        (0.0, WaxingWaningState.EXACT),
        (1.0, WaxingWaningState.WAXING),
        (90.0, WaxingWaningState.WAXING),
        (179.999, WaxingWaningState.WAXING),
        (180.0, WaxingWaningState.EXACT),
        (180.001, WaxingWaningState.WANING),
        (270.0, WaxingWaningState.WANING),
        (359.999, WaxingWaningState.WANING),
    ],
)
def test_waxing_waning_state_follows_angle_hemisphere(
    angle_deg: float,
    expected_state: WaxingWaningState,
) -> None:
    """Le demi-cercle lunaire controle l'etat croissant ou decroissant."""
    condition = calculate_moon_phase_condition(
        moon_longitude_deg=angle_deg,
        sun_longitude_deg=0.0,
    )

    assert condition.waxing_or_waning is expected_state


@pytest.mark.parametrize(
    ("angle_deg", "expected_key", "expected_index"),
    [
        (0.0, MoonPhaseKey.NEW_MOON, 0),
        (22.499, MoonPhaseKey.NEW_MOON, 0),
        (22.5, MoonPhaseKey.WAXING_CRESCENT, 1),
        (67.499, MoonPhaseKey.WAXING_CRESCENT, 1),
        (67.5, MoonPhaseKey.FIRST_QUARTER, 2),
        (112.499, MoonPhaseKey.FIRST_QUARTER, 2),
        (112.5, MoonPhaseKey.WAXING_GIBBOUS, 3),
        (157.499, MoonPhaseKey.WAXING_GIBBOUS, 3),
        (157.5, MoonPhaseKey.FULL_MOON, 4),
        (180.0, MoonPhaseKey.FULL_MOON, 4),
        (202.499, MoonPhaseKey.FULL_MOON, 4),
        (202.5, MoonPhaseKey.WANING_GIBBOUS, 5),
        (247.499, MoonPhaseKey.WANING_GIBBOUS, 5),
        (247.5, MoonPhaseKey.LAST_QUARTER, 6),
        (292.499, MoonPhaseKey.LAST_QUARTER, 6),
        (292.5, MoonPhaseKey.WANING_CRESCENT, 7),
        (314.999, MoonPhaseKey.WANING_CRESCENT, 7),
        (315.0, MoonPhaseKey.BALSAMIC, 8),
        (330.0, MoonPhaseKey.BALSAMIC, 8),
        (337.499, MoonPhaseKey.BALSAMIC, 8),
        (337.5, MoonPhaseKey.NEW_MOON, 0),
        (350.0, MoonPhaseKey.NEW_MOON, 0),
    ],
)
def test_phase_boundaries_and_indexes_are_stable(
    angle_deg: float,
    expected_key: MoonPhaseKey,
    expected_index: int,
) -> None:
    """Les bornes de segmentation et l'index public restent stables."""
    condition = calculate_moon_phase_condition(
        moon_longitude_deg=angle_deg,
        sun_longitude_deg=0.0,
    )

    assert condition.phase_key is expected_key
    assert condition.phase_index == expected_index


def test_balsamic_priority_does_not_override_new_moon() -> None:
    """La plage balsamique s'arrete avant la fenetre de nouvelle lune."""
    balsamic = calculate_moon_phase_condition(moon_longitude_deg=330.0, sun_longitude_deg=0.0)
    new_moon = calculate_moon_phase_condition(moon_longitude_deg=350.0, sun_longitude_deg=0.0)
    full_moon = calculate_moon_phase_condition(moon_longitude_deg=180.0, sun_longitude_deg=0.0)

    assert balsamic.phase_key is MoonPhaseKey.BALSAMIC
    assert new_moon.phase_key is MoonPhaseKey.NEW_MOON
    assert full_moon.phase_key is MoonPhaseKey.FULL_MOON


def test_illumination_ratio_uses_approximate_geometric_formula() -> None:
    """L'illumination suit la formule contractuelle bornee entre zero et un."""
    new_moon = calculate_moon_phase_condition(moon_longitude_deg=0.0, sun_longitude_deg=0.0)
    first_quarter = calculate_moon_phase_condition(
        moon_longitude_deg=90.0,
        sun_longitude_deg=0.0,
    )
    full_moon = calculate_moon_phase_condition(moon_longitude_deg=180.0, sun_longitude_deg=0.0)

    assert new_moon.illumination_ratio == 0.0
    assert first_quarter.illumination_ratio == pytest.approx(0.5)
    assert full_moon.illumination_ratio == 1.0


def test_non_finite_longitudes_are_rejected() -> None:
    """Les valeurs non finies ne produisent pas de phase inconnue silencieuse."""
    with pytest.raises(ValueError, match="longitude must be finite"):
        calculate_moon_phase_condition(moon_longitude_deg=nan, sun_longitude_deg=0.0)
    with pytest.raises(ValueError, match="longitude must be finite"):
        calculate_moon_phase_condition(moon_longitude_deg=0.0, sun_longitude_deg=inf)
