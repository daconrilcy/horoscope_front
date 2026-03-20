from datetime import date, datetime

import pytest

from app.prediction.enriched_astro_events_builder import EnrichedAstroEventsBuilder
from app.prediction.schemas import NatalChart, PlanetState, StepAstroState


@pytest.fixture
def builder():
    return EnrichedAstroEventsBuilder()


def test_compute_sky_aspects(builder):
    # Mock states with Sun at 0° and Moon at 60° (Sextile)
    p1 = PlanetState(
        code="sun",
        longitude=0.0,
        speed_lon=1.0,
        is_retrograde=False,
        sign_code=1,
        natal_house_transited=1,
    )
    p2 = PlanetState(
        code="moon",
        longitude=60.1,
        speed_lon=13.0,
        is_retrograde=False,
        sign_code=3,
        natal_house_transited=3,
    )

    state = StepAstroState(
        ut_jd=2461119.5,
        local_time=datetime(2026, 3, 19, 12, 0),
        ascendant_deg=0.0,
        mc_deg=0.0,
        house_cusps=[0.0] * 12,
        planets={"Sun": p1, "Moon": p2},
        house_system_effective="placidus",
    )

    events = builder._compute_sky_aspects([state])
    assert len(events) >= 1
    # Find the sun-moon sextile
    ev = next(e for e in events if e.body == "moon" and e.target == "sun")
    assert ev.aspect == "sextile"
    assert pytest.approx(ev.orb_deg, 0.01) == 0.1


def test_compute_returns(builder):
    # Natal Sun at 150°
    natal = NatalChart(
        planet_positions={"Sun": 150.0}, planet_houses={}, house_sign_rulers={}, natal_aspects=[]
    )

    # Transiting Sun at 150.2°
    p_sun = PlanetState(
        code="sun",
        longitude=150.2,
        speed_lon=1.0,
        is_retrograde=False,
        sign_code=5,
        natal_house_transited=5,
    )
    state = StepAstroState(
        ut_jd=2461119.5,
        local_time=datetime(2026, 3, 19, 12, 0),
        ascendant_deg=0.0,
        mc_deg=0.0,
        house_cusps=[0.0] * 12,
        planets={"Sun": p_sun},
        house_system_effective="placidus",
    )

    events = builder._compute_returns([state], natal)
    assert any(e.event_type == "solar_return" for e in events)


def test_compute_progressions(builder):
    # Progressions calculation is deterministic based on age
    natal = NatalChart(
        planet_positions={"Moon": 10.0}, planet_houses={}, house_sign_rulers={}, natal_aspects=[]
    )
    # Person born 30 years ago
    birth = datetime(1996, 3, 19, 12, 0)
    today = date(2026, 3, 19)

    ref_dt = datetime(2026, 3, 19, 0, 0)
    events = builder._compute_progressions(natal, today, birth, ref_dt)
    assert isinstance(events, list)


def test_angular_distance(builder):
    assert builder._angular_distance(350, 10) == 20
    assert builder._angular_distance(10, 350) == 20
    assert builder._angular_distance(180, 0) == 180
    assert builder._angular_distance(0, 180) == 180
    assert builder._angular_distance(90, 100) == 10
