from datetime import datetime, timedelta, timezone

import pytest

from app.prediction.block_generator import BlockGenerator
from app.prediction.schemas import AstroEvent
from app.prediction.turning_point_detector import TurningPoint, TurningPointDetector


def create_event(priority: int, local_time: datetime, *, ut_time: float = 0.0) -> AstroEvent:
    return AstroEvent(
        event_type="aspect",
        ut_time=ut_time,
        local_time=local_time,
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=1.0,
        priority=priority,
        base_weight=1.0,
    )


@pytest.fixture
def base_data():
    start_time = datetime(2026, 3, 7, 0, 0, tzinfo=timezone.utc)
    step_times = [start_time + timedelta(minutes=15 * index) for index in range(96)]
    notes_by_step = [{"love": 10, "work": 10, "health": 10} for _ in range(96)]
    events_by_step = [[] for _ in range(96)]
    contributions_by_step = [[] for _ in range(96)]
    return step_times, notes_by_step, events_by_step, contributions_by_step


def test_pivot_delta_note_3(base_data):
    # AC2: threshold is now 3; delta=3 triggers a pivot
    step_times, notes_by_step, events_by_step, _ = base_data
    for index in range(4, 96):
        notes_by_step[index]["love"] = 13  # delta = 3

    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)

    assert len(pivots) == 1
    assert pivots[0].reason == "delta_note"
    assert pivots[0].local_time == step_times[4]
    assert "love" in pivots[0].categories_impacted


def test_no_pivot_delta_note_2(base_data):
    # AC2: delta=2 is now below the threshold, no pivot expected
    step_times, notes_by_step, events_by_step, _ = base_data
    for index in range(4, 96):
        notes_by_step[index]["love"] = 12  # delta = 2

    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)

    assert len(pivots) == 0


def test_no_pivot_delta_note_1(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    notes_by_step[4]["love"] = 11

    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)

    assert len(pivots) == 0


def test_pivot_top3_change(base_data):
    # AC2: money delta=10 >= 3, pivot expected (reason is delta_note, higher priority)
    step_times, notes_by_step, events_by_step, _ = base_data
    notes_by_step[3] = {"love": 10, "work": 10, "health": 10, "money": 5}
    notes_by_step[4] = {"love": 10, "work": 10, "health": 10, "money": 15}

    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)

    assert len(pivots) >= 1
    assert any(p.reason in ("delta_note", "top3_change") for p in pivots)


def test_no_pivot_top3_change_below_threshold(base_data):
    # AC2: top3_change with max_delta < 3 must NOT produce a pivot
    # All steps track money=10; step 4 changes to 11 (delta=1 < 3)
    step_times, notes_by_step, events_by_step, _ = base_data
    for step_notes in notes_by_step:
        step_notes["money"] = 10
    notes_by_step[4]["money"] = 11  # delta = 1, below threshold

    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)

    # max_delta=1, no pivot expected
    assert len(pivots) == 0


def test_pivot_high_priority(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    events_by_step[10].append(create_event(70, step_times[10]))

    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)

    assert len(pivots) == 1
    assert pivots[0].reason == "high_priority_event"
    assert pivots[0].local_time == step_times[10]


def test_signal_driven_single_block_no_pivot(base_data):
    # AC1: without pivots, the whole day is one block (no fixed hourly grid)
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data

    generator = BlockGenerator()
    blocks = generator.generate(
        [],
        notes_by_step,
        events_by_step,
        step_times,
        contributions_by_step,
    )

    assert len(blocks) == 1
    assert blocks[0].block_index == 0
    assert blocks[0].start_local == step_times[0]
    assert blocks[0].end_local == step_times[-1] + timedelta(minutes=15)


def test_adaptive_split(base_data):
    # AC1: 1 pivot -> 2 blocks (before/after pivot)
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    pivot = TurningPoint(
        local_time=step_times[5],
        reason="delta_note",
        categories_impacted=["love"],
        trigger_event=None,
        severity=1.0,
    )

    generator = BlockGenerator()
    blocks = generator.generate(
        [pivot],
        notes_by_step,
        events_by_step,
        step_times,
        contributions_by_step,
    )

    assert len(blocks) == 2
    assert blocks[0].start_local == step_times[0]
    assert blocks[0].end_local == step_times[5]
    assert blocks[1].start_local == step_times[5]
    assert blocks[1].end_local == step_times[-1] + timedelta(minutes=15)


def test_tone_positive(base_data):
    # With no pivots -> 1 block; tone computed from all 96 steps
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    for index in range(96):
        notes_by_step[index] = {"love": 15, "work": 15, "health": 15}

    generator = BlockGenerator()
    blocks = generator.generate(
        [],
        notes_by_step,
        events_by_step,
        step_times,
        contributions_by_step,
    )
    assert blocks[0].tone_code == "positive"


def test_tone_negative(base_data):
    # With no pivots -> 1 block; tone computed from all 96 steps
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    for index in range(96):
        notes_by_step[index] = {"love": 5, "work": 5, "health": 5}

    generator = BlockGenerator()
    blocks = generator.generate(
        [],
        notes_by_step,
        events_by_step,
        step_times,
        contributions_by_step,
    )
    assert blocks[0].tone_code == "negative"


def test_two_blocks_with_single_pivot(base_data):
    # AC1: pivot at step[7] yields exactly 2 blocks
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    pivot = TurningPoint(
        local_time=step_times[7],
        reason="delta_note",
        categories_impacted=["love"],
        trigger_event=None,
        severity=1.0,
    )

    generator = BlockGenerator()
    blocks = generator.generate(
        [pivot],
        notes_by_step,
        events_by_step,
        step_times,
        contributions_by_step,
    )

    assert len(blocks) == 2
    assert blocks[0].start_local == step_times[0]
    assert blocks[0].end_local == step_times[7]
    assert blocks[1].start_local == step_times[7]


def test_driver_traceable(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    event = create_event(50, step_times[0])
    contributions_by_step = [[] for _ in range(96)]
    for index in range(4):
        contributions_by_step[index] = [(event, {"love": 0.8, "work": 0.2, "health": 0.1})]

    generator = BlockGenerator()
    blocks = generator.generate(
        [],
        notes_by_step,
        events_by_step,
        step_times,
        contributions_by_step,
    )

    assert event in blocks[0].driver_events


def test_driver_events_grouped_by_logical_signature(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    contributions_by_step = [[] for _ in range(96)]
    for index in range(4):
        event = create_event(50, step_times[index], ut_time=float(index))
        contributions_by_step[index] = [(event, {"love": 0.5})]

    generator = BlockGenerator()
    blocks = generator.generate(
        [],
        notes_by_step,
        events_by_step,
        step_times,
        contributions_by_step,
    )

    assert len(blocks[0].driver_events) == 3
