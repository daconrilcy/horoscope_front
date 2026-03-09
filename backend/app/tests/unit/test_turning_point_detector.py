# backend/app/tests/unit/test_turning_point_detector.py
from datetime import datetime, timedelta

from app.prediction.schemas import AstroEvent
from app.prediction.turning_point_detector import TurningPointDetector

BASE_TIME = datetime(2026, 3, 9, 6, 0, 0)
STEP = timedelta(minutes=15)


def make_step_times(n: int) -> list[datetime]:
    return [BASE_TIME + i * STEP for i in range(n)]


def make_notes(n: int, default: int = 10) -> list[dict[str, int]]:
    codes = ["energy", "mood", "work", "love", "money", "health"]
    return [{c: default for c in codes} for _ in range(n)]


def make_event(event_type: str, priority: int, step_index: int) -> AstroEvent:
    t = BASE_TIME + step_index * STEP
    return AstroEvent(
        event_type=event_type,
        ut_time=float(step_index),
        local_time=t,
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=0.5,
        priority=priority,
        base_weight=1.0,
    )


def test_no_pivot_on_small_delta():
    detector = TurningPointDetector()
    times = make_step_times(3)
    notes = make_notes(3, 10)
    notes[1]["energy"] = 12  # delta = 2 < 3
    events = [[], [], []]

    pivots = detector.detect(notes, events, times)
    assert len(pivots) == 0


def test_pivot_on_threshold_delta():
    detector = TurningPointDetector()
    times = make_step_times(3)
    notes = make_notes(3, 10)
    notes[1]["energy"] = 13  # delta = 3 >= 3
    notes[2]["energy"] = 13  # stay at 13 to avoid second pivot
    events = [[], [], []]

    pivots = detector.detect(notes, events, times)
    assert len(pivots) == 1
    assert pivots[0].reason == "delta_note"
    assert "energy" in pivots[0].categories_impacted


def test_pivot_on_high_priority_event():
    detector = TurningPointDetector()
    times = make_step_times(3)
    notes = make_notes(3, 10)
    events = [[], [make_event("test", 65, 1)], []]

    pivots = detector.detect(notes, events, times)
    assert len(pivots) == 1
    assert pivots[0].reason == "high_priority_event"
    assert pivots[0].trigger_event.priority == 65


def test_asc_sign_change_does_not_create_decision_pivot():
    detector = TurningPointDetector()
    times = make_step_times(3)
    notes = make_notes(3, 10)
    events = [[], [make_event("asc_sign_change", 78, 1)], []]

    pivots = detector.detect(notes, events, times)

    assert pivots == []


def test_no_top3_change_below_threshold():
    detector = TurningPointDetector()
    times = make_step_times(3)
    # Energy, Mood, Work are top 3 (all 10)
    # Love is 9.
    notes = [
        {"energy": 10, "mood": 10, "work": 10, "love": 9},
        {"energy": 10, "mood": 10, "work": 10, "love": 11},  # Love becomes top 3 (11 > 10)
        {"energy": 10, "mood": 10, "work": 10, "love": 11},
    ]
    # Max delta is abs(11-9) = 2 < 3
    events = [[], [], []]

    pivots = detector.detect(notes, events, times)
    assert len(pivots) == 0
