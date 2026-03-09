# backend/app/tests/unit/test_block_generator.py
from datetime import timedelta

from app.prediction.block_generator import BlockGenerator
from app.prediction.turning_point_detector import TurningPoint
from app.tests.fixtures.intraday_qa_fixtures import get_active_day


def test_blocks_no_overlap():
    generator = BlockGenerator()
    data = get_active_day()

    # We need synthetic pivots for the generator
    pivots = [
        TurningPoint(
            local_time=data["step_times"][20],
            reason="delta_note",
            categories_impacted=["energy"],
            trigger_event=None,
            severity=0.8,
        ),
        TurningPoint(
            local_time=data["step_times"][30],
            reason="high_priority_event",
            categories_impacted=[],
            trigger_event=data["events_by_step"][30][0],
            severity=1.0,
        ),
        TurningPoint(
            local_time=data["step_times"][50],
            reason="delta_note",
            categories_impacted=["love"],
            trigger_event=None,
            severity=0.8,
        ),
    ]

    # Empty contributions for simplicity in this unit test
    contributions = [[] for _ in range(len(data["step_times"]))]

    blocks = generator.generate(
        pivots, data["notes_by_step"], data["events_by_step"], data["step_times"], contributions
    )

    assert len(blocks) > 1
    for i in range(len(blocks) - 1):
        assert blocks[i].end_local == blocks[i + 1].start_local
        assert blocks[i].start_local < blocks[i].end_local


def test_block_boundaries_aligned_with_pivots():
    generator = BlockGenerator()
    data = get_active_day()

    # Ensure tones are different to avoid merging
    # Pivot 1 at step 20, Pivot 2 at step 30, Pivot 3 at step 50
    # Block 1: 0-19 (neutral)
    for i in range(20):
        data["notes_by_step"][i]["energy"] = 10
    # Block 2: 20-29 (positive)
    for i in range(20, 30):
        data["notes_by_step"][i]["energy"] = 15
    # Block 3: 30-49 (negative)
    for i in range(30, 50):
        data["notes_by_step"][i]["energy"] = 5
    # Block 4: 50-95 (neutral)
    for i in range(50, 96):
        data["notes_by_step"][i]["energy"] = 10

    pivot_times = [data["step_times"][20], data["step_times"][30], data["step_times"][50]]
    pivots = [
        TurningPoint(
            local_time=pt, reason="test", categories_impacted=[], trigger_event=None, severity=0.5
        )
        for pt in pivot_times
    ]

    contributions = [[] for _ in range(len(data["step_times"]))]
    blocks = generator.generate(
        pivots, data["notes_by_step"], data["events_by_step"], data["step_times"], contributions
    )

    # Boundaries should be: start, pivot1, pivot2, pivot3, end
    # With 3 pivots, we should have 4 blocks
    assert len(blocks) == 4
    boundaries = {b.start_local for b in blocks} | {blocks[-1].end_local}
    expected_boundaries = {
        data["step_times"][0],
        data["step_times"][-1] + timedelta(minutes=15),
    } | set(pivot_times)

    assert boundaries == expected_boundaries


def test_pivot_boundary_preserved_when_adjacent_blocks_look_identical():
    generator = BlockGenerator()
    data = get_active_day()
    pivot_time = data["step_times"][20]
    pivots = [
        TurningPoint(
            local_time=pivot_time,
            reason="delta_note",
            categories_impacted=["energy"],
            trigger_event=None,
            severity=0.8,
        )
    ]

    contributions = [[] for _ in range(len(data["step_times"]))]
    blocks = generator.generate(
        pivots,
        data["notes_by_step"],
        data["events_by_step"],
        data["step_times"],
        contributions,
    )

    assert len(blocks) == 2
    assert blocks[0].end_local == pivot_time
    assert blocks[1].start_local == pivot_time
