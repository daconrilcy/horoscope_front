"""Tests du calculateur pur de mouvement planetaire."""

from math import inf, nan
from types import MappingProxyType

import pytest

from app.domain.astrology.planetary_conditions import (
    DEFAULT_PLANETARY_MOTION_PROFILES,
    PlanetaryMotionDirection,
    PlanetaryMotionProfile,
    PlanetarySpeedState,
    calculate_planetary_motion_condition,
    calculate_planetary_motion_conditions,
)


def test_calculator_returns_direct_retrograde_and_stationary_directions() -> None:
    """La direction est derivee de la vitesse avec priorite stationnaire."""
    profile = PlanetaryMotionProfile(
        planet_key="mars",
        mean_speed_deg_per_day=0.5,
        stationary_threshold_abs=0.05,
    )

    direct = calculate_planetary_motion_condition(
        planet_key="mars",
        speed_deg_per_day=0.2,
        profile=profile,
    )
    retrograde = calculate_planetary_motion_condition(
        planet_key="mars",
        speed_deg_per_day=-0.2,
        profile=profile,
    )
    stationary_from_positive = calculate_planetary_motion_condition(
        planet_key="mars",
        speed_deg_per_day=0.05,
        profile=profile,
    )
    stationary_from_negative = calculate_planetary_motion_condition(
        planet_key="mars",
        speed_deg_per_day=-0.05,
        profile=profile,
    )

    assert direct.direction is PlanetaryMotionDirection.DIRECT
    assert direct.is_retrograde is False
    assert direct.is_stationary is False
    assert retrograde.direction is PlanetaryMotionDirection.RETROGRADE
    assert retrograde.is_retrograde is True
    assert retrograde.is_stationary is False
    assert stationary_from_positive.direction is PlanetaryMotionDirection.STATIONARY
    assert stationary_from_positive.is_stationary is True
    assert stationary_from_negative.direction is PlanetaryMotionDirection.STATIONARY
    assert stationary_from_negative.is_retrograde is False


def test_zero_speed_is_stationary_and_not_unknown() -> None:
    """La vitesse nulle produit une stationnarite explicite."""
    condition = calculate_planetary_motion_condition(
        planet_key="saturn",
        speed_deg_per_day=0.0,
        profile=PlanetaryMotionProfile(
            planet_key="saturn",
            mean_speed_deg_per_day=0.033,
            stationary_threshold_abs=0.00165,
        ),
    )

    assert condition.direction is PlanetaryMotionDirection.STATIONARY
    assert condition.direction is not PlanetaryMotionDirection.UNKNOWN
    assert condition.absolute_speed_deg_per_day == 0.0
    assert condition.normalized_speed_ratio == 0.0
    assert condition.speed_state is PlanetarySpeedState.VERY_SLOW


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (0.39, PlanetarySpeedState.VERY_SLOW),
        (0.4, PlanetarySpeedState.SLOW),
        (0.79, PlanetarySpeedState.SLOW),
        (0.8, PlanetarySpeedState.NORMAL),
        (1.2, PlanetarySpeedState.NORMAL),
        (1.21, PlanetarySpeedState.FAST),
        (1.6, PlanetarySpeedState.FAST),
        (1.61, PlanetarySpeedState.VERY_FAST),
    ],
)
def test_speed_states_follow_configurable_ratio_bounds(
    ratio: float,
    expected: PlanetarySpeedState,
) -> None:
    """Les bornes relatives suivent le contrat strict du profil."""
    profile = PlanetaryMotionProfile(
        planet_key="venus",
        mean_speed_deg_per_day=2.0,
        stationary_threshold_abs=0.01,
    )

    condition = calculate_planetary_motion_condition(
        planet_key="venus",
        speed_deg_per_day=ratio * profile.mean_speed_deg_per_day,
        profile=profile,
    )

    assert condition.normalized_speed_ratio == ratio
    assert condition.speed_state is expected


def test_custom_speed_thresholds_change_state_without_new_contract() -> None:
    """Les seuils personnalises sont portes uniquement par le profil fourni."""
    profile = PlanetaryMotionProfile(
        planet_key="mercury",
        mean_speed_deg_per_day=1.0,
        stationary_threshold_abs=0.01,
        very_slow_ratio_threshold=0.2,
        slow_ratio_threshold=0.5,
        fast_ratio_threshold=1.5,
        very_fast_ratio_threshold=2.0,
    )

    condition = calculate_planetary_motion_condition(
        planet_key="mercury",
        speed_deg_per_day=1.8,
        profile=profile,
    )

    assert condition.speed_state is PlanetarySpeedState.FAST


def test_invalid_mean_speed_returns_unknown_speed_state() -> None:
    """Une vitesse moyenne nulle ou negative bloque uniquement l'etat relatif."""
    zero_mean = calculate_planetary_motion_condition(
        planet_key="test",
        speed_deg_per_day=0.4,
        profile=PlanetaryMotionProfile(
            planet_key="test",
            mean_speed_deg_per_day=0.0,
            stationary_threshold_abs=0.0,
        ),
    )
    negative_mean = calculate_planetary_motion_condition(
        planet_key="test",
        speed_deg_per_day=-0.4,
        profile=PlanetaryMotionProfile(
            planet_key="test",
            mean_speed_deg_per_day=-1.0,
            stationary_threshold_abs=0.0,
        ),
    )

    assert zero_mean.direction is PlanetaryMotionDirection.DIRECT
    assert zero_mean.normalized_speed_ratio is None
    assert zero_mean.speed_state is PlanetarySpeedState.UNKNOWN
    assert negative_mean.direction is PlanetaryMotionDirection.RETROGRADE
    assert negative_mean.normalized_speed_ratio is None
    assert negative_mean.speed_state is PlanetarySpeedState.UNKNOWN


def test_non_finite_speed_is_rejected() -> None:
    """Les vitesses non finies ne deviennent pas des faits planetaires."""
    profile = PlanetaryMotionProfile(
        planet_key="mars",
        mean_speed_deg_per_day=0.524,
        stationary_threshold_abs=0.0262,
    )

    with pytest.raises(ValueError, match="speed_deg_per_day must be finite"):
        calculate_planetary_motion_condition(
            planet_key="mars",
            speed_deg_per_day=nan,
            profile=profile,
        )
    with pytest.raises(ValueError, match="speed_deg_per_day must be finite"):
        calculate_planetary_motion_condition(
            planet_key="mars",
            speed_deg_per_day=inf,
            profile=profile,
        )


def test_planet_key_must_match_profile_key() -> None:
    """Le profil fourni doit appartenir a la planete calculee."""
    with pytest.raises(ValueError, match="planet_key must match"):
        calculate_planetary_motion_condition(
            planet_key="mars",
            speed_deg_per_day=0.2,
            profile=DEFAULT_PLANETARY_MOTION_PROFILES["venus"],
        )
    with pytest.raises(ValueError, match="planet_key must match"):
        calculate_planetary_motion_conditions(
            speeds_by_planet={"mars": 0.2},
            profiles_by_planet={"mars": DEFAULT_PLANETARY_MOTION_PROFILES["venus"]},
        )


def test_default_profiles_match_expected_catalog_values() -> None:
    """Le catalogue expose les dix vitesses moyennes demandees."""
    expected_mean_speeds = {
        "moon": 13.176,
        "mercury": 1.2,
        "venus": 1.18,
        "sun": 0.9856,
        "mars": 0.524,
        "jupiter": 0.083,
        "saturn": 0.033,
        "uranus": 0.0117,
        "neptune": 0.006,
        "pluto": 0.004,
    }

    assert isinstance(DEFAULT_PLANETARY_MOTION_PROFILES, MappingProxyType)
    assert set(DEFAULT_PLANETARY_MOTION_PROFILES) == set(expected_mean_speeds)
    for planet_key, expected_mean_speed in expected_mean_speeds.items():
        profile = DEFAULT_PLANETARY_MOTION_PROFILES[planet_key]
        assert profile.planet_key == planet_key
        assert profile.mean_speed_deg_per_day == expected_mean_speed
        assert profile.stationary_threshold_abs == expected_mean_speed * 0.05
    with pytest.raises(TypeError):
        DEFAULT_PLANETARY_MOTION_PROFILES["mars"] = DEFAULT_PLANETARY_MOTION_PROFILES["venus"]  # type: ignore[index]


def test_batch_calculator_returns_all_conditions_and_rejects_missing_profile() -> None:
    """Le calcul de lot conserve les cles et refuse les profils absents."""
    conditions = calculate_planetary_motion_conditions(
        speeds_by_planet={
            "mars": -0.1,
            "venus": 1.18,
        },
        profiles_by_planet=DEFAULT_PLANETARY_MOTION_PROFILES,
    )

    assert tuple(conditions) == ("mars", "venus")
    assert conditions["mars"].direction is PlanetaryMotionDirection.RETROGRADE
    assert conditions["venus"].speed_state is PlanetarySpeedState.NORMAL
    with pytest.raises(ValueError, match="missing planetary motion profile for ceres"):
        calculate_planetary_motion_conditions(
            speeds_by_planet={"ceres": 0.1},
            profiles_by_planet=DEFAULT_PLANETARY_MOTION_PROFILES,
        )
