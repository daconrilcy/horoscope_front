import math
from datetime import datetime

import pytest
import swisseph as swe

from app.prediction import astro_calculator
from app.prediction.astro_calculator import V1_PLANETS, AstroCalculator
from app.prediction.exceptions import PredictionEngineError
from app.prediction.schemas import PlanetState, StepAstroState

# Natal cusps for testing (Placidus-like for some latitude)
# House 1 starts at 0, House 2 at 30, ..., House 12 at 330
MOCK_NATAL_CUSPS = [float(i * 30) for i in range(12)]


@pytest.fixture
def calculator():
    return AstroCalculator(
        natal_cusps=MOCK_NATAL_CUSPS,
        latitude=48.8566,  # Paris
        longitude=2.3522,
    )


def test_all_v1_planets_present(calculator):
    # J2000.0
    jd = 2451545.0
    state = calculator.compute_step(jd, datetime.now())

    assert isinstance(state, StepAstroState)
    assert len(state.planets) == 10
    for name in V1_PLANETS:
        assert name in state.planets
        assert isinstance(state.planets[name], PlanetState)


def test_asc_mc_in_range(calculator):
    jd = 2451545.0
    state = calculator.compute_step(jd, datetime.now())

    assert 0 <= state.ascendant_deg < 360
    assert 0 <= state.mc_deg < 360
    assert len(state.house_cusps) == 12


def test_longitude_in_range(calculator):
    jd = 2451545.0
    state = calculator.compute_step(jd, datetime.now())

    for p in state.planets.values():
        assert 0 <= p.longitude < 360


def test_sign_code_from_longitude(calculator):
    jd = 2451545.0
    state = calculator.compute_step(jd, datetime.now())

    sun = state.planets["Sun"]
    expected_sign = int(math.floor(sun.longitude / 30.0))
    assert sun.sign_code == expected_sign


def test_retrograde_detection(calculator):
    # Mercury retrograde: 2026-03-15
    jd = swe.julday(2026, 3, 15, 12.0)
    state = calculator.compute_step(jd, datetime.now())

    mercury = state.planets["Mercury"]
    assert mercury.speed_lon < 0
    assert mercury.is_retrograde is True


def test_direct_detection(calculator):
    jd = swe.julday(2026, 4, 15, 12.0)
    state = calculator.compute_step(jd, datetime.now())

    mercury = state.planets["Mercury"]
    assert mercury.speed_lon > 0
    assert mercury.is_retrograde is False


def test_natal_house_boundary(calculator):
    # MOCK_NATAL_CUSPS: H1=0, H2=30, H3=60 ...

    # Just after H2 cusp
    # We override _natal_house_for_longitude to test it directly
    h = calculator._natal_house_for_longitude(30.1)
    assert h == 2

    # Just before H2 cusp
    h = calculator._natal_house_for_longitude(29.9)
    assert h == 1

    # Wrap around: H12 starts at 330, H1 starts at 0
    h = calculator._natal_house_for_longitude(359.9)
    assert h == 12
    h = calculator._natal_house_for_longitude(0.1)
    assert h == 1


def test_fallback_porphyre():
    # Extreme latitude where Placidus fails
    calc_extreme = AstroCalculator(
        natal_cusps=MOCK_NATAL_CUSPS,
        latitude=89.0,
        longitude=0.0,
    )
    jd = 2451545.0
    state = calc_extreme.compute_step(jd, datetime.now())

    assert state.house_system_effective == "porphyre"


def test_unknown_planet_raises(calculator):
    jd = 2451545.0
    with pytest.raises(PredictionEngineError, match="not in V1_PLANETS scope"):
        calculator._compute_planet(jd, "Chiron")


def test_natal_house_wrap_around():
    # Test with non-zero start for House 1
    # H1 starts at 350, H2 at 20
    custom_cusps = [350.0, 20.0, 50.0, 80.0, 110.0, 140.0, 170.0, 200.0, 230.0, 260.0, 290.0, 320.0]
    calc = AstroCalculator(natal_cusps=custom_cusps, latitude=0, longitude=0)

    assert calc._natal_house_for_longitude(355.0) == 1
    assert calc._natal_house_for_longitude(5.0) == 1
    assert calc._natal_house_for_longitude(25.0) == 2
    assert calc._natal_house_for_longitude(345.0) == 12


def test_invalid_natal_cusp_count_raises() -> None:
    with pytest.raises(PredictionEngineError, match="Expected 12 natal cusps"):
        AstroCalculator(natal_cusps=[0.0, 30.0], latitude=0.0, longitude=0.0)


def test_invalid_placidus_output_falls_back_to_porphyre(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_houses(
        jd: float,
        lat: float,
        lon: float,
        system: bytes,
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        if system == b"P":
            return (
                (0.0, 30.0, 30.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0),
                (45.0, 180.0),
            )
        return (
            (0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0),
            (15.0, 275.0),
        )

    monkeypatch.setattr(astro_calculator.swe, "houses", fake_houses)

    calc = AstroCalculator(natal_cusps=MOCK_NATAL_CUSPS, latitude=48.8566, longitude=2.3522)
    state = calc.compute_step(2451545.0, datetime.now())

    assert state.house_system_effective == "porphyre"
    assert state.house_cusps == [
        0.0,
        30.0,
        60.0,
        90.0,
        120.0,
        150.0,
        180.0,
        210.0,
        240.0,
        270.0,
        300.0,
        330.0,
    ]
    assert state.ascendant_deg == 15.0
    assert state.mc_deg == 275.0


def test_houses_are_normalized_and_support_13_cusp_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_houses(
        jd: float,
        lat: float,
        lon: float,
        system: bytes,
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        return (
            (
                999.0,
                360.0,
                390.0,
                420.0,
                450.0,
                480.0,
                510.0,
                540.0,
                570.0,
                600.0,
                630.0,
                660.0,
                690.0,
            ),
            (-10.0, 721.0),
        )

    monkeypatch.setattr(astro_calculator.swe, "houses", fake_houses)

    calc = AstroCalculator(natal_cusps=MOCK_NATAL_CUSPS, latitude=48.8566, longitude=2.3522)
    state = calc.compute_step(2451545.0, datetime.now())

    assert state.house_system_effective == "placidus"
    assert state.house_cusps == [
        0.0,
        30.0,
        60.0,
        90.0,
        120.0,
        150.0,
        180.0,
        210.0,
        240.0,
        270.0,
        300.0,
        330.0,
    ]
    assert state.ascendant_deg == 350.0
    assert state.mc_deg == 1.0
