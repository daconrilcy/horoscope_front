import pytest
from datetime import date, datetime
from unittest.mock import MagicMock

from app.prediction.event_detector import EventDetector
from app.prediction.schemas import StepAstroState, PlanetState, AstroEvent
from app.prediction.temporal_sampler import DayGrid, SamplePoint


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
    
    # Mock event types for priority/weight
    ctx.ruleset_context.event_types = {}
    
    return ctx

@pytest.fixture
def natal_positions():
    return {"Sun": 0.0}

def create_step(ut_jd, planets, asc_deg=0.0):
    planet_states = {
        code: PlanetState(code=code, longitude=lon, speed_lon=1.0, is_retrograde=False, sign_code=int(lon//30), natal_house_transited=1)
        for code, lon in planets.items()
    }
    return StepAstroState(
        ut_jd=ut_jd,
        local_time=datetime.now(),
        ascendant_deg=asc_deg,
        mc_deg=0.0,
        house_cusps=[0.0]*12,
        house_system_effective="placidus",
        planets=planet_states
    )

def test_enter_orb_detected(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    # orb_max for Sun-Sun conjunction is 2.0
    steps = [
        create_step(2460000.0, {"Sun": 357.5}), # orb = 2.5
        create_step(2460000.1, {"Sun": 358.5}), # orb = 1.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")
    
    events = detector.detect(steps, day_grid)
    
    enter_events = [e for e in events if e.event_type == "enter_orb"]
    assert len(enter_events) == 1
    assert enter_events[0].body == "Sun"
    assert enter_events[0].target == "Sun"
    assert enter_events[0].aspect == "conjunction"
    assert enter_events[0].metadata["phase"] == "applying"

def test_exit_orb_detected(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    steps = [
        create_step(2460000.0, {"Sun": 1.5}), # orb = 1.5
        create_step(2460000.1, {"Sun": 2.5}), # orb = 2.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")
    
    events = detector.detect(steps, day_grid)
    
    exit_events = [e for e in events if e.event_type == "exit_orb"]
    assert len(exit_events) == 1
    assert exit_events[0].metadata["phase"] == "separating"

def test_exact_detected(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    steps = [
        create_step(2460000.0, {"Sun": 358.5}), # orb = 1.5
        create_step(2460000.1, {"Sun": 359.9}), # orb = 0.1
        create_step(2460000.2, {"Sun": 1.5}),   # orb = 1.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.3, None, None, date(2024, 1, 1), "UTC")
    
    events = detector.detect(steps, day_grid)
    
    exact_events = [e for e in events if e.event_type == "exact"]
    assert len(exact_events) == 1
    assert exact_events[0].ut_time == 2460000.1
    assert exact_events[0].orb_deg == pytest.approx(0.1)

def test_moon_ingress_detected(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    steps = [
        create_step(2460000.0, {"Moon": 29.5}), # Sign 0
        create_step(2460000.1, {"Moon": 30.5}), # Sign 1
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")
    
    events = detector.detect(steps, day_grid)
    
    ingress = [e for e in events if e.event_type == "moon_sign_ingress"]
    assert len(ingress) == 1
    assert ingress[0].metadata["from_sign"] == 0
    assert ingress[0].metadata["to_sign"] == 1

def test_asc_change_detected(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    steps = [
        create_step(2460000.0, {}, asc_deg=29.9), # Sign 0
        create_step(2460000.1, {}, asc_deg=30.1), # Sign 1
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")
    
    events = detector.detect(steps, day_grid)
    
    asc_change = [e for e in events if e.event_type == "asc_sign_change"]
    assert len(asc_change) == 1
    assert asc_change[0].metadata["from_sign"] == 0
    assert asc_change[0].metadata["to_sign"] == 1

def test_24_planetary_hours(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    # Sunday (2024-03-03 is a Sunday)
    day_grid = DayGrid([], 2460372.5, 2460373.5, 2460372.7, 2460373.2, date(2024, 3, 3), "UTC")
    
    events = detector.detect([], day_grid)
    
    ph_events = [e for e in events if e.event_type == "planetary_hour_change"]
    assert len(ph_events) == 24
    # First ruler of Sunday is Sun
    assert ph_events[0].body == "Sun"
    assert ph_events[0].metadata["hour_number"] == 1

def test_non_v1_target_ignored(mock_ctx):
    # Eris is not in V1 targets
    natal_positions = {"Eris": 10.0}
    detector = EventDetector(mock_ctx, natal_positions)
    assert "Eris" not in detector.natal_positions

def test_minor_aspect_ignored(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    # 150 degrees (Quincunx) is not in ASPECTS_V1
    steps = [
        create_step(2460000.0, {"Sun": 150.0}),
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")
    
    events = detector.detect(steps, day_grid)
    aspect_events = [e for e in events if e.event_type in ["enter_orb", "exact", "exit_orb"]]
    assert len(aspect_events) == 0

def test_events_sorted_by_time(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
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


def test_applying_true_on_decreasing_orb(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    # Orb decreasing from 2.5 → 1.5 (crossing orb_max=2.0): enter_orb with applying phase
    steps = [
        create_step(2460000.0, {"Sun": 357.5}),  # orb = 2.5
        create_step(2460000.1, {"Sun": 358.5}),  # orb = 1.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    enter = [e for e in events if e.event_type == "enter_orb"]
    assert len(enter) == 1
    assert enter[0].metadata["phase"] == "applying"


def test_separating_true_on_increasing_orb(mock_ctx, natal_positions):
    detector = EventDetector(mock_ctx, natal_positions)
    # Orb increasing from 1.5 → 2.5 (crossing orb_max=2.0): exit_orb with separating phase
    steps = [
        create_step(2460000.0, {"Sun": 1.5}),  # orb = 1.5
        create_step(2460000.1, {"Sun": 2.5}),  # orb = 2.5
    ]
    day_grid = DayGrid([], 2460000.0, 2460000.2, None, None, date(2024, 1, 1), "UTC")

    events = detector.detect(steps, day_grid)

    exit_evts = [e for e in events if e.event_type == "exit_orb"]
    assert len(exit_evts) == 1
    assert exit_evts[0].metadata["phase"] == "separating"
