# Tests golden astronomiques sensibles CS-250.
"""Verifie les cas sensibles contre les valeurs SwissEph gelées."""

from __future__ import annotations

import pytest

from app.domain.astrology.runtime.astronomical_proof import (
    SENSITIVE_GOLDEN_CASES,
    GoldenExpectedReference,
    SensitiveGoldenCase,
    calculate_sensitive_case,
)


@pytest.mark.parametrize("case", SENSITIVE_GOLDEN_CASES, ids=lambda item: item.golden_case_id)
def test_sensitive_golden_case_matches_frozen_reference(case: SensitiveGoldenCase) -> None:
    """Chaque cas sensible reste dans les tolerances canoniques."""
    actual = calculate_sensitive_case(case)
    expected = case.expected_reference

    _assert_angle_close(
        actual.sun_longitude, expected.sun_longitude, case.tolerance.longitude_degrees
    )
    _assert_angle_close(
        actual.moon_longitude,
        expected.moon_longitude,
        case.tolerance.longitude_degrees,
    )
    _assert_angle_close(
        actual.mercury_longitude,
        expected.mercury_longitude,
        case.tolerance.longitude_degrees,
    )
    _assert_angle_close(
        actual.ascendant_longitude,
        expected.ascendant_longitude,
        case.tolerance.house_angle_degrees,
    )
    _assert_angle_close(
        actual.mc_longitude, expected.mc_longitude, case.tolerance.house_angle_degrees
    )
    _assert_angle_close(
        actual.cusp_1_longitude,
        expected.cusp_1_longitude,
        case.tolerance.house_angle_degrees,
    )
    _assert_angle_close(
        actual.cusp_10_longitude,
        expected.cusp_10_longitude,
        case.tolerance.house_angle_degrees,
    )
    _assert_ayanamsa_close(actual, expected, case)


def test_sensitive_golden_suite_covers_required_case_families() -> None:
    """La suite couvre les familles sensibles demandees par CS-241/CS-250."""
    case_ids = {case.golden_case_id for case in SENSITIVE_GOLDEN_CASES}

    assert {
        "paris-normal-placidus",
        "paris-dst-ambiguous",
        "paris-dst-nonexistent",
        "high-latitude-placidus",
        "lahiri-sidereal",
        "topocentric-altitude",
        "whole-sign-paris",
        "placidus-edge-helsinki",
    } == case_ids


def _assert_angle_close(actual: float, expected: float, tolerance: float) -> None:
    """Compare deux longitudes circulaires avec une tolerance en degres."""
    delta = abs((actual - expected + 180.0) % 360.0 - 180.0)
    assert delta <= tolerance


def _assert_ayanamsa_close(
    actual: GoldenExpectedReference,
    expected: GoldenExpectedReference,
    case: SensitiveGoldenCase,
) -> None:
    """Verifie l'ayanamsa uniquement pour les cas sideraux."""
    if expected.ayanamsa_value is None:
        assert actual.ayanamsa_value is None
        return
    assert actual.ayanamsa_value is not None
    assert abs(actual.ayanamsa_value - expected.ayanamsa_value) <= case.tolerance.ayanamsa_degrees
