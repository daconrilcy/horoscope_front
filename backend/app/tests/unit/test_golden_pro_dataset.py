from __future__ import annotations

import pytest

from app.domain.astrology.ephemeris_provider import calculate_planets
from app.domain.astrology.houses_provider import calculate_houses
from app.domain.astrology.natal_preparation import BirthInput, prepare_birth_data
from app.tests.golden.pro_fixtures import GoldenProCase, load_golden_pro_dataset


def _is_swisseph_available() -> bool:
    try:
        import swisseph  # noqa: F401

        return True
    except ImportError:
        return False


requires_swisseph = pytest.mark.skipif(
    not _is_swisseph_available(),
    reason="pyswisseph non disponible dans cet environnement",
)


def _circular_diff_degrees(actual: float, expected: float) -> float:
    raw = abs(actual - expected) % 360.0
    return min(raw, 360.0 - raw)


def _assert_with_tolerance(actual: float, expected: float, tolerance: float, label: str) -> None:
    diff = _circular_diff_degrees(actual, expected)
    assert diff <= tolerance, (
        f"{label}: attendu={expected:.6f}, obtenu={actual:.6f}, "
        f"delta={diff:.6f} > tolerance={tolerance}"
    )


@pytest.mark.golden
def test_golden_pro_dataset_schema_and_scope() -> None:
    dataset = load_golden_pro_dataset()

    assert dataset.dataset_id == "golden-pro-v1"
    assert 50 <= dataset.case_count <= 200
    # On vérifie que les tolérances du dataset sont cohérentes avec les attentes pro
    assert dataset.tolerances["planets_deg"] == 0.01
    assert dataset.tolerances["angles_deg"] == 0.05

    for case in dataset.cases:
        assert case.settings.engine == "swisseph", f"Engine {case.settings.engine} non supporté"
        assert case.settings.ephe.startswith("swisseph")
        assert case.settings.frame in {"geocentric", "topocentric"}
        assert case.settings.zodiac in {"tropical", "sidereal"}
        assert case.settings.house_system in {"placidus", "equal", "whole_sign"}


@pytest.mark.golden
@requires_swisseph
@pytest.mark.parametrize(
    "case",
    load_golden_pro_dataset().cases,
    ids=lambda c: c.case_id if isinstance(c, GoldenProCase) else "golden-pro-case",
)
def test_golden_pro_dataset_positions_and_angles(case: GoldenProCase) -> None:
    dataset = load_golden_pro_dataset()
    planet_tolerance = dataset.tolerances["planets_deg"]
    angle_tolerance = dataset.tolerances["angles_deg"]

    birth_input = BirthInput(
        birth_date=case.datetime.birth_date,
        birth_time=case.datetime.birth_time,
        birth_place=case.place_resolved.name,
        birth_timezone=case.datetime.birth_timezone,
        birth_lat=case.place_resolved.lat,
        birth_lon=case.place_resolved.lon,
    )
    prepared = prepare_birth_data(birth_input)
    _assert_with_tolerance(
        prepared.julian_day,
        case.datetime.expected_jd_ut,
        tolerance=1e-6,
        label=f"{case.case_id}.jd_ut",
    )

    ephemeris_result = calculate_planets(
        prepared.julian_day,
        lat=case.place_resolved.lat,
        lon=case.place_resolved.lon,
        zodiac=case.settings.zodiac,
        frame=case.settings.frame,
        altitude_m=case.place_resolved.altitude_m,
    )
    houses = calculate_houses(
        prepared.julian_day,
        lat=case.place_resolved.lat,
        lon=case.place_resolved.lon,
        house_system=case.settings.house_system,
        frame=case.settings.frame,
        altitude_m=case.place_resolved.altitude_m,
    )
    planets = {planet.planet_id: planet for planet in ephemeris_result.planets}

    _assert_with_tolerance(
        planets["sun"].longitude,
        case.expected.sun,
        planet_tolerance,
        f"{case.case_id}.sun",
    )
    _assert_with_tolerance(
        planets["moon"].longitude,
        case.expected.moon,
        planet_tolerance,
        f"{case.case_id}.moon",
    )
    _assert_with_tolerance(
        planets["mercury"].longitude,
        case.expected.mercury,
        planet_tolerance,
        f"{case.case_id}.mercury",
    )
    _assert_with_tolerance(
        houses.ascendant_longitude,
        case.expected.asc,
        angle_tolerance,
        f"{case.case_id}.asc",
    )
    _assert_with_tolerance(
        houses.mc_longitude,
        case.expected.mc,
        angle_tolerance,
        f"{case.case_id}.mc",
    )
    _assert_with_tolerance(
        houses.cusps[0],
        case.expected.cusp_1,
        angle_tolerance,
        f"{case.case_id}.cusp_1",
    )
    _assert_with_tolerance(
        houses.cusps[9],
        case.expected.cusp_10,
        angle_tolerance,
        f"{case.case_id}.cusp_10",
    )
