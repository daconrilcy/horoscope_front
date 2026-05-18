"""Tests du builder daily enrichi, dont les événements étoiles fixes runtime."""

from datetime import date, datetime
from types import SimpleNamespace

import pytest

from app.domain.prediction.enriched_astro_events_builder import EnrichedAstroEventsBuilder
from app.domain.prediction.schemas import NatalChart, PlanetState, StepAstroState

MAJOR_ASPECT_ANGLES = (
    (0.0, "conjunction"),
    (60.0, "sextile"),
    (90.0, "square"),
    (120.0, "trine"),
    (180.0, "opposition"),
)
MAJOR_ASPECT_ORBS = {code: 1.5 for _angle, code in MAJOR_ASPECT_ANGLES}
fixed_star_parameters = {
    "fixed_star_orb_deg": 1.0,
    "fixed_star_max_visual_magnitude": 2.5,
    "fixed_star_base_weight": 0.6,
}


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

    events = builder._compute_sky_aspects([state], MAJOR_ASPECT_ANGLES, MAJOR_ASPECT_ORBS)
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
    events = builder._compute_progressions(
        natal,
        today,
        birth,
        ref_dt,
        MAJOR_ASPECT_ANGLES,
        MAJOR_ASPECT_ORBS,
    )
    assert isinstance(events, list)


def test_compute_fixed_star_conjunctions_uses_runtime_reference(builder):
    """Les conjonctions fixed star lisent le contrat runtime injecté."""
    p_moon = PlanetState(
        code="moon",
        longitude=150.2,
        speed_lon=13.0,
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
        planets={"Moon": p_moon},
        house_system_effective="placidus",
    )
    stars = (
        SimpleNamespace(
            key="regulus",
            display_name="Regulus",
            ecliptic_longitude_deg=150.0,
            visual_magnitude=1.4,
            keywords=("royalty",),
            source_category="historical_astrological_source",
            source_key="robson_fixed_stars",
        ),
    )

    events = builder._compute_fixed_star_conjunctions(
        [state],
        fixed_stars=stars,
        parameters=fixed_star_parameters,
    )

    assert len(events) == 1
    assert events[0].target == "regulus"
    assert events[0].base_weight == pytest.approx(0.6)
    assert events[0].metadata == {
        "orb_max": 1.0,
        "star_key": "regulus",
        "star_display_name": "Regulus",
        "visual_magnitude": 1.4,
        "fixed_star_source_category": "historical_astrological_source",
        "fixed_star_source_key": "robson_fixed_stars",
        "fixed_star_keywords": ["royalty"],
    }


def test_compute_fixed_star_conjunctions_uses_ruleset_orb(builder):
    """L'orbe fixed star vient du ruleset et filtre les étoiles hors seuil."""
    p_moon = PlanetState(
        code="moon",
        longitude=150.8,
        speed_lon=13.0,
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
        planets={"Moon": p_moon},
        house_system_effective="placidus",
    )
    stars = (
        SimpleNamespace(
            key="regulus",
            display_name="Regulus",
            ecliptic_longitude_deg=150.0,
            visual_magnitude=1.4,
        ),
    )

    narrow_events = builder._compute_fixed_star_conjunctions(
        [state],
        fixed_stars=stars,
        parameters={**fixed_star_parameters, "fixed_star_orb_deg": 0.5},
    )
    wide_events = builder._compute_fixed_star_conjunctions(
        [state],
        fixed_stars=stars,
        parameters={**fixed_star_parameters, "fixed_star_orb_deg": 1.0},
    )

    assert narrow_events == []
    assert len(wide_events) == 1
    assert wide_events[0].metadata["orb_max"] == 1.0


def test_compute_fixed_star_conjunctions_filters_visual_magnitude(builder):
    """Le seuil de magnitude ignore les étoiles trop faibles sans rejeter l'absence."""
    p_moon = PlanetState(
        code="moon",
        longitude=150.0,
        speed_lon=13.0,
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
        planets={"Moon": p_moon},
        house_system_effective="placidus",
    )
    stars = (
        SimpleNamespace(
            key="bright",
            display_name="Bright",
            ecliptic_longitude_deg=150.0,
            visual_magnitude=2.0,
        ),
        SimpleNamespace(
            key="unknown",
            display_name="Unknown",
            ecliptic_longitude_deg=150.0,
            visual_magnitude=None,
        ),
        SimpleNamespace(
            key="faint",
            display_name="Faint",
            ecliptic_longitude_deg=150.0,
            visual_magnitude=3.5,
        ),
    )

    events = builder._compute_fixed_star_conjunctions(
        [state],
        fixed_stars=stars,
        parameters=fixed_star_parameters,
    )

    assert {event.target for event in events} == {"bright", "unknown"}


def test_angular_distance(builder):
    assert builder._angular_distance(350, 10) == 20
    assert builder._angular_distance(10, 350) == 20
    assert builder._angular_distance(180, 0) == 180
    assert builder._angular_distance(0, 180) == 180
    assert builder._angular_distance(90, 100) == 10
