from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from app.prediction.event_detector import EventDetector
from app.prediction.schemas import NatalChart, PlanetState, StepAstroState
from app.prediction.temporal_sampler import DayGrid
from app.prediction.turning_point_detector import TurningPointDetector


def _make_event_type_mock(priority: int, base_weight: float) -> MagicMock:
    m = MagicMock()
    m.priority = priority
    m.base_weight = base_weight
    return m


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    # Mock planet profiles for orb_active_deg
    planet_profiles = {
        "Sun": MagicMock(orb_active_deg=2.0),
        "Moon": MagicMock(orb_active_deg=2.0),
        "Mars": MagicMock(orb_active_deg=2.0),
    }
    ctx.prediction_context.planet_profiles = planet_profiles

    # Mock aspect profiles for orb_multiplier
    aspect_profiles = {
        "conjunction": MagicMock(orb_multiplier=1.0),
        "square": MagicMock(orb_multiplier=1.0),
    }
    ctx.prediction_context.aspect_profiles = aspect_profiles

    # Mock event types for priority/weight — empty (always fallback)
    ctx.ruleset_context.event_types = {}

    return ctx


@pytest.fixture
def mock_ctx_with_event_types():
    """Context with real taxonomy event_types — exercises nominal lookup path."""
    ctx = MagicMock()
    ctx.prediction_context.planet_profiles = {
        "Sun": MagicMock(orb_active_deg=2.0),
        "Moon": MagicMock(orb_active_deg=2.0),
        "Mars": MagicMock(orb_active_deg=2.0),
        "Asc": MagicMock(orb_active_deg=2.0),
    }
    ctx.prediction_context.aspect_profiles = {
        "conjunction": MagicMock(orb_multiplier=1.0),
        "square": MagicMock(orb_multiplier=1.0),
    }
    ctx.ruleset_context.event_types = {
        "aspect_exact_to_angle": _make_event_type_mock(80, 2.0),
        "aspect_exact_to_luminary": _make_event_type_mock(75, 1.8),
        "aspect_exact_to_personal": _make_event_type_mock(68, 1.5),
        "aspect_enter_orb": _make_event_type_mock(40, 1.0),
        "aspect_exit_orb": _make_event_type_mock(25, 0.5),
        "moon_sign_ingress": _make_event_type_mock(72, 1.5),
        "asc_sign_change": _make_event_type_mock(78, 2.0),
        "planetary_hour_change": _make_event_type_mock(20, 0.8),
    }
    return ctx


@pytest.fixture
def natal_chart():
    return NatalChart(planet_positions={"Sun": 0.0}, planet_houses={"Sun": 1}, house_sign_rulers={})


def create_step(ut_jd, planets, asc_deg=0.0):
    planet_states = {
        code: PlanetState(
            code=code,
            longitude=lon,
            speed_lon=1.0,
            is_retrograde=False,
            sign_code=int(lon // 30),
            natal_house_transited=1,
        )
        for code, lon in planets.items()
    }
    return StepAstroState(
        ut_jd=ut_jd,
        local_time=datetime.now(),
        ascendant_deg=asc_deg,
        mc_deg=0.0,
        house_cusps=[0.0] * 12,
        house_system_effective="placidus",
        planets=planet_states,
    )


def test_enter_orb_detected(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    # orb_max for Sun-Sun conjunction is 2.0
    steps = [
        create_step(2460000.0, {"Sun": 357.5}),  # orb = 2.5
        create_step(2460000.1, {"Sun": 358.5}),  # orb = 1.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    enter_events = [e for e in events if e.event_type == "aspect_enter_orb"]
    assert len(enter_events) == 1
    assert enter_events[0].body == "Sun"
    assert enter_events[0].target == "Sun"
    assert enter_events[0].aspect == "conjunction"
    assert enter_events[0].metadata["phase"] == "applying"
    assert enter_events[0].metadata["orb_max"] == pytest.approx(2.0)
    assert enter_events[0].metadata["natal_house_target"] == 1
    assert enter_events[0].metadata["natal_house_transited"] == 1


def test_exit_orb_detected(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    steps = [
        create_step(2460000.0, {"Sun": 1.5}),  # orb = 1.5
        create_step(2460000.1, {"Sun": 2.5}),  # orb = 2.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    exit_events = [e for e in events if e.event_type == "aspect_exit_orb"]
    assert len(exit_events) == 1
    assert exit_events[0].metadata["phase"] == "separating"


def test_exact_detected(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    steps = [
        create_step(2460000.0, {"Sun": 358.5}),  # orb = 1.5
        create_step(2460000.1, {"Sun": 359.9}),  # orb = 0.1
        create_step(2460000.2, {"Sun": 1.5}),  # orb = 1.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.3, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    # target=Sun → luminary family
    exact_events = [e for e in events if e.event_type == "aspect_exact_to_luminary"]
    assert len(exact_events) == 1
    assert exact_events[0].ut_time == 2460000.1
    assert exact_events[0].orb_deg == pytest.approx(0.1)
    assert exact_events[0].metadata["orb_max"] == pytest.approx(2.0)
    assert exact_events[0].metadata["natal_house_target"] == 1


def test_moon_ingress_detected(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    steps = [
        create_step(2460000.0, {"Moon": 29.5}),  # Sign 0
        create_step(2460000.1, {"Moon": 30.5}),  # Sign 1
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    ingress = [e for e in events if e.event_type == "moon_sign_ingress"]
    assert len(ingress) == 1
    assert ingress[0].metadata["from_sign"] == 0
    assert ingress[0].metadata["to_sign"] == 1


def test_asc_change_detected(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    steps = [
        create_step(2460000.0, {}, asc_deg=29.9),  # Sign 0
        create_step(2460000.1, {}, asc_deg=30.1),  # Sign 1
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    asc_change = [e for e in events if e.event_type == "asc_sign_change"]
    assert len(asc_change) == 1
    assert asc_change[0].metadata["from_sign"] == 0
    assert asc_change[0].metadata["to_sign"] == 1


def test_24_planetary_hours(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    # Sunday (2024-03-03 is a Sunday)
    day_grid = DayGrid([], 2460372.5, 2460373.5, 2460372.7, 2460373.2, date(2024, 3, 3), "UTC")

    events = detector.detect([], day_grid)

    ph_events = [e for e in events if e.event_type == "planetary_hour_change"]
    assert len(ph_events) == 24
    # First ruler of Sunday is Sun
    assert ph_events[0].body == "Sun"
    assert ph_events[0].metadata["hour_number"] == 1


def test_exact_metadata_uses_prev_step_house(mock_ctx, natal_chart):
    """Régression H1 : natal_house_transited de l'exact doit venir du step i-1, pas du step i."""
    detector = EventDetector(mock_ctx, natal_chart)

    # Step 0 : orb=1.5, transit house=1
    # Step 1 : orb=0.1 (minimum exact), transit house=1
    # Step 2 : orb=1.5, transit house=2  ← le bug prenait cette valeur
    # L'exact est horodaté à step 1 → natal_house_transited doit être 1, pas 2.
    def make_step(jd, sun_lon, house):
        return StepAstroState(
            ut_jd=jd,
            local_time=datetime.now(),
            ascendant_deg=0.0,
            mc_deg=0.0,
            house_cusps=[0.0] * 12,
            house_system_effective="placidus",
            planets={
                "Sun": PlanetState(
                    code="Sun",
                    longitude=sun_lon,
                    speed_lon=1.0,
                    is_retrograde=False,
                    sign_code=int(sun_lon // 30),
                    natal_house_transited=house,
                )
            },
        )

    steps = [
        make_step(2460000.0, 358.5, 1),  # orb=1.5, house=1
        make_step(2460000.1, 359.9, 1),  # orb=0.1, house=1  ← exact ici
        make_step(
            2460000.2,
            1.5,
            2,
        ),  # orb=1.5, house=2  ← step courant au moment de la détection
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.3, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)
    # target=Sun → luminary family
    exact_events = [e for e in events if e.event_type == "aspect_exact_to_luminary"]
    assert len(exact_events) == 1
    assert exact_events[0].ut_time == 2460000.1
    assert exact_events[0].metadata["natal_house_transited"] == 1  # du step 1, pas 2


def test_non_v1_target_ignored(mock_ctx):
    # Eris is not in V1 targets
    chart = NatalChart(
        planet_positions={"Eris": 10.0}, planet_houses={"Eris": 1}, house_sign_rulers={}
    )
    detector = EventDetector(mock_ctx, chart)
    assert "Eris" not in detector.natal_positions


def test_minor_aspect_ignored(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    # 150 degrees (Quincunx) is not in ASPECTS_V1
    steps = [
        create_step(2460000.0, {"Sun": 150.0}),
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)
    aspect_events = [
        e
        for e in events
        if e.event_type in EventDetector.EXACT_EVENT_TYPES | {"aspect_enter_orb", "aspect_exit_orb"}
    ]
    assert len(aspect_events) == 0


def test_events_sorted_by_time(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    # Moon ingress at step 1 (ut=2460000.2); planetary hours start at sunrise (ut=2460000.1).
    # Events from different sources are interleaved — detect() must sort them.
    steps = [
        create_step(2460000.0, {"Moon": 29.5}),
        create_step(2460000.2, {"Moon": 30.5}),  # moon_sign_ingress at 2460000.2
    ]
    day_grid = DayGrid([], 2460000.0, 2460001.0, 2460000.1, 2460000.6, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    times = [e.ut_time for e in events]
    assert times == sorted(times)


def test_applying_true_on_decreasing_orb(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    # Orb decreasing from 2.5 → 1.5 (crossing orb_max=2.0): enter_orb with applying phase
    steps = [
        create_step(2460000.0, {"Sun": 357.5}),  # orb = 2.5
        create_step(2460000.1, {"Sun": 358.5}),  # orb = 1.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    enter = [e for e in events if e.event_type == "aspect_enter_orb"]
    assert len(enter) == 1
    assert enter[0].metadata["phase"] == "applying"


def test_separating_true_on_increasing_orb(mock_ctx, natal_chart):
    detector = EventDetector(mock_ctx, natal_chart)
    # Orb increasing from 1.5 → 2.5 (crossing orb_max=2.0): exit_orb with separating phase
    steps = [
        create_step(2460000.0, {"Sun": 1.5}),  # orb = 1.5
        create_step(2460000.1, {"Sun": 2.5}),  # orb = 2.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    exit_evts = [e for e in events if e.event_type == "aspect_exit_orb"]
    assert len(exit_evts) == 1
    assert exit_evts[0].metadata["phase"] == "separating"


def test_orb_max_resolves_lowercase_profiles_without_fallback(mock_ctx):
    mock_ctx.prediction_context.planet_profiles = {
        "sun": MagicMock(orb_active_deg=3.0),
    }
    mock_ctx.prediction_context.aspect_profiles = {
        "conjunction": MagicMock(orb_multiplier=1.5),
    }
    chart = NatalChart(
        planet_positions={"Sun": 0.0}, planet_houses={"Sun": 1}, house_sign_rulers={}
    )
    detector = EventDetector(mock_ctx, chart)

    orb_max = detector._orb_max("Sun", "conjunction")

    assert orb_max == pytest.approx(4.5)


def test_orb_max_falls_back_when_profile_value_is_none(mock_ctx):
    mock_ctx.prediction_context.planet_profiles = {
        "sun": MagicMock(orb_active_deg=None),
    }
    mock_ctx.prediction_context.aspect_profiles = {
        "conjunction": MagicMock(orb_multiplier=1.5),
    }
    chart = NatalChart(
        planet_positions={"Sun": 0.0}, planet_houses={"Sun": 1}, house_sign_rulers={}
    )
    detector = EventDetector(mock_ctx, chart)

    orb_max = detector._orb_max("Sun", "conjunction")

    assert orb_max == pytest.approx(3.0)


# ── T5: Nouveaux tests de taxonomie ───────────────────────────────────────────


def test_discriminate_exact_code_angle():
    """Aspect exact vers Asc ou MC → aspect_exact_to_angle."""
    ctx = MagicMock()
    ctx.prediction_context.planet_profiles = {}
    ctx.prediction_context.aspect_profiles = {}
    ctx.ruleset_context.event_types = {}
    chart = NatalChart(planet_positions={}, planet_houses={}, house_sign_rulers={})
    detector = EventDetector(ctx, chart)

    assert detector._discriminate_exact_code("Asc") == "aspect_exact_to_angle"
    assert detector._discriminate_exact_code("MC") == "aspect_exact_to_angle"


def test_discriminate_exact_code_luminary():
    """Aspect exact vers Sun ou Moon → aspect_exact_to_luminary."""
    ctx = MagicMock()
    ctx.prediction_context.planet_profiles = {}
    ctx.prediction_context.aspect_profiles = {}
    ctx.ruleset_context.event_types = {}
    chart = NatalChart(planet_positions={}, planet_houses={}, house_sign_rulers={})
    detector = EventDetector(ctx, chart)

    assert detector._discriminate_exact_code("Sun") == "aspect_exact_to_luminary"
    assert detector._discriminate_exact_code("Moon") == "aspect_exact_to_luminary"


def test_discriminate_exact_code_personal():
    """Aspect exact vers toute autre cible → aspect_exact_to_personal."""
    ctx = MagicMock()
    ctx.prediction_context.planet_profiles = {}
    ctx.prediction_context.aspect_profiles = {}
    ctx.ruleset_context.event_types = {}
    chart = NatalChart(planet_positions={}, planet_houses={}, house_sign_rulers={})
    detector = EventDetector(ctx, chart)

    for target in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"):
        assert detector._discriminate_exact_code(target) == "aspect_exact_to_personal"
    assert detector._discriminate_exact_code(None) == "aspect_exact_to_personal"


def test_nominal_taxonomy_path_priority_and_weight(mock_ctx_with_event_types):
    """Avec event_types renseignés, les événements reçoivent les priorités du ruleset."""
    chart = NatalChart(
        planet_positions={"Sun": 0.0},
        planet_houses={"Sun": 1},
        house_sign_rulers={},
    )
    detector = EventDetector(mock_ctx_with_event_types, chart)

    # enter_orb event
    steps = [
        create_step(2460000.0, {"Sun": 357.5}),  # orb=2.5 > orb_max=2.0
        create_step(2460000.1, {"Sun": 358.5}),  # orb=1.5 < orb_max → enter_orb
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")
    events = detector.detect(steps, day_grid)

    enter = [e for e in events if e.event_type == "aspect_enter_orb"]
    assert len(enter) == 1
    assert enter[0].priority == 40
    assert enter[0].base_weight == pytest.approx(1.0)


def test_nominal_exit_orb_priority_and_weight(mock_ctx_with_event_types):
    chart = NatalChart(
        planet_positions={"Sun": 0.0},
        planet_houses={"Sun": 1},
        house_sign_rulers={},
    )
    detector = EventDetector(mock_ctx_with_event_types, chart)

    steps = [
        create_step(2460000.0, {"Sun": 1.5}),  # orb=1.5 < orb_max
        create_step(2460000.1, {"Sun": 2.5}),  # orb=2.5 > orb_max → exit_orb
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")
    events = detector.detect(steps, day_grid)

    exit_events = [e for e in events if e.event_type == "aspect_exit_orb"]
    assert len(exit_events) == 1
    assert exit_events[0].priority == 25
    assert exit_events[0].base_weight == pytest.approx(0.5)


def test_exact_to_luminary_priority(mock_ctx_with_event_types):
    """Exact aspect to Sun → aspect_exact_to_luminary avec priority=75."""
    chart = NatalChart(
        planet_positions={"Sun": 0.0},
        planet_houses={"Sun": 1},
        house_sign_rulers={},
    )
    detector = EventDetector(mock_ctx_with_event_types, chart)

    steps = [
        create_step(2460000.0, {"Sun": 358.5}),  # orb=1.5
        create_step(2460000.1, {"Sun": 359.9}),  # orb=0.1 — exact minimum
        create_step(2460000.2, {"Sun": 1.5}),  # orb=1.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.3, None, None, date(2024, 1, 1), "UTC")
    events = detector.detect(steps, day_grid)

    exact = [e for e in events if e.event_type == "aspect_exact_to_luminary"]
    assert len(exact) == 1
    assert exact[0].priority == 75
    assert exact[0].base_weight == pytest.approx(1.8)


def test_exact_to_angle_priority(mock_ctx_with_event_types):
    """Exact aspect to Asc → aspect_exact_to_angle avec priority=80."""
    chart = NatalChart(
        planet_positions={"Asc": 0.0},
        planet_houses={"Asc": 1},
        house_sign_rulers={},
    )
    mock_ctx_with_event_types.prediction_context.planet_profiles["Asc"] = MagicMock(
        orb_active_deg=2.0
    )
    detector = EventDetector(mock_ctx_with_event_types, chart)

    steps = [
        create_step(2460000.0, {"Sun": 358.5}),  # orb=1.5
        create_step(2460000.1, {"Sun": 359.9}),  # orb=0.1 — exact minimum
        create_step(2460000.2, {"Sun": 1.5}),  # orb=1.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.3, None, None, date(2024, 1, 1), "UTC")
    events = detector.detect(steps, day_grid)

    exact = [e for e in events if e.event_type == "aspect_exact_to_angle"]
    assert len(exact) == 1
    assert exact[0].priority == 80
    assert exact[0].base_weight == pytest.approx(2.0)


def test_nominal_moon_ingress_priority_and_weight(mock_ctx_with_event_types, natal_chart):
    detector = EventDetector(mock_ctx_with_event_types, natal_chart)
    steps = [
        create_step(2460000.0, {"Moon": 29.5}),
        create_step(2460000.1, {"Moon": 30.5}),
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    ingress_events = [e for e in events if e.event_type == "moon_sign_ingress"]
    assert len(ingress_events) == 1
    assert ingress_events[0].priority == 72
    assert ingress_events[0].base_weight == pytest.approx(1.5)


def test_nominal_asc_sign_change_priority_and_weight(mock_ctx_with_event_types, natal_chart):
    detector = EventDetector(mock_ctx_with_event_types, natal_chart)
    steps = [
        create_step(2460000.0, {}, asc_deg=29.9),
        create_step(2460000.1, {}, asc_deg=30.1),
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    asc_events = [e for e in events if e.event_type == "asc_sign_change"]
    assert len(asc_events) == 1
    assert asc_events[0].priority == 78
    assert asc_events[0].base_weight == pytest.approx(2.0)


def test_planetary_hour_change_below_pivot_threshold(mock_ctx_with_event_types):
    """planetary_hour_change seul ne doit pas déclencher un pivot high_priority_event."""
    chart = NatalChart(planet_positions={}, planet_houses={}, house_sign_rulers={})
    detector = EventDetector(mock_ctx_with_event_types, chart)

    day_grid = DayGrid([], 2460372.5, 2460373.5, 2460372.7, 2460373.2, date(2024, 3, 3), "UTC")
    events = detector.detect([], day_grid)

    ph_events = [e for e in events if e.event_type == "planetary_hour_change"]
    assert len(ph_events) == 24

    # Toutes les priorités sont en dessous du seuil de pivot
    pivot_threshold = TurningPointDetector.PRIORITY_PIVOT_THRESHOLD
    for evt in ph_events:
        assert evt.priority < pivot_threshold, (
            f"planetary_hour_change a priority={evt.priority} >= pivot threshold {pivot_threshold}"
        )

    # Vérifier qu'aucun pivot n'est créé par ces événements seuls
    step_times = [evt.local_time for evt in ph_events]
    # Simuler detection: notes constantes, events = seulement des planetary_hours
    notes_by_step = [{"love": 10} for _ in step_times]
    events_by_step = [[evt] for evt in ph_events]
    tpd = TurningPointDetector()
    pivots = tpd.detect(notes_by_step, events_by_step, step_times)
    high_priority_pivots = [p for p in pivots if p.reason == "high_priority_event"]
    assert len(high_priority_pivots) == 0, (
        "planetary_hour_change alone triggered high_priority_event pivots"
    )
