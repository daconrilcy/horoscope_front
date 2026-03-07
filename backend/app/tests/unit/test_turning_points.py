import pytest
from datetime import datetime, timedelta, timezone
from app.prediction.turning_point_detector import TurningPointDetector, TurningPoint
from app.prediction.block_generator import BlockGenerator, TimeBlock
from app.prediction.schemas import AstroEvent

def create_event(priority: int, local_time: datetime) -> AstroEvent:
    return AstroEvent(
        event_type="aspect",
        ut_time=0.0,
        local_time=local_time,
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=1.0,
        priority=priority,
        base_weight=1.0
    )

@pytest.fixture
def base_data():
    # 96 steps of 15 minutes = 24 hours
    start_time = datetime(2026, 3, 7, 0, 0, tzinfo=timezone.utc)
    step_times = [start_time + timedelta(minutes=15 * i) for i in range(96)]
    
    # Base notes: all 10
    notes_by_step = [{"love": 10, "work": 10, "health": 10} for _ in range(96)]
    
    # Empty events
    events_by_step = [[] for _ in range(96)]
    
    # Empty contributions: list of lists of (event, contrib_dict) tuples
    contributions_by_step = [[] for _ in range(96)]
    
    return step_times, notes_by_step, events_by_step, contributions_by_step

def test_pivot_delta_note_2(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    # Rule 1: Delta >= 2
    for i in range(4, 96):
        notes_by_step[i]["love"] = 12
    
    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)
    
    assert len(pivots) == 1
    assert pivots[0].reason == "delta_note"
    assert pivots[0].local_time == step_times[4]
    assert "love" in pivots[0].categories_impacted

def test_no_pivot_delta_note_1(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    # Delta = 1
    notes_by_step[4]["love"] = 11
    
    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)
    
    assert len(pivots) == 0

def test_pivot_top3_change(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    # Initially: love(10), work(10), health(10) -> all top 3 (tie)
    # Step 4: money(15) enters top 3
    notes_by_step[3] = {"love": 10, "work": 10, "health": 10, "money": 5}
    notes_by_step[4] = {"love": 10, "work": 10, "health": 10, "money": 15}
    
    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)
    
    assert any(p.reason == "top3_change" for p in pivots)

def test_pivot_high_priority(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    # Rule 3: Priority >= 65
    event = create_event(70, step_times[10])
    events_by_step[10].append(event)
    
    detector = TurningPointDetector()
    pivots = detector.detect(notes_by_step, events_by_step, step_times)
    
    assert len(pivots) == 1
    assert pivots[0].reason == "high_priority_event"
    assert pivots[0].local_time == step_times[10]

def test_24_blocks_no_pivot(base_data):
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    pivots = []
    
    generator = BlockGenerator()
    blocks = generator.generate(pivots, notes_by_step, events_by_step, step_times, contributions_by_step)
    
    assert len(blocks) == 24
    for i, block in enumerate(blocks):
        assert block.block_index == i
        # Standard block is 4 steps = 1 hour
        assert block.end_local - block.start_local == timedelta(hours=1)

def test_adaptive_split(base_data):
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    # Pivot at step 5 (second block: steps 4, 5, 6, 7)
    # Should split into [4, 5) and [5, 7]
    pivot = TurningPoint(local_time=step_times[5], reason="delta_note", categories_impacted=["love"], trigger_event=None, severity=1.0)
    pivots = [pivot]
    
    generator = BlockGenerator()
    blocks = generator.generate(pivots, notes_by_step, events_by_step, step_times, contributions_by_step)
    
    # 23 standard blocks (23h) + 2 split blocks (1h total) = 25 blocks
    assert len(blocks) == 25
    # Block 1 should be standard (0-3)
    assert blocks[0].start_local == step_times[0]
    assert blocks[0].end_local == step_times[4]
    
    # Block 2 should be split (step 4)
    assert blocks[1].start_local == step_times[4]
    assert blocks[1].end_local == step_times[5]
    
    # Block 3 should be split (steps 5, 6, 7)
    assert blocks[2].start_local == step_times[5]
    assert blocks[2].end_local == step_times[8]

def test_tone_positive(base_data):
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    # First block: steps 0, 1, 2, 3
    for i in range(4):
        notes_by_step[i] = {"love": 15, "work": 15, "health": 15}

    generator = BlockGenerator()
    blocks = generator.generate([], notes_by_step, events_by_step, step_times, contributions_by_step)
    assert blocks[0].tone_code == "positive"

def test_tone_negative(base_data):
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    for i in range(4):
        notes_by_step[i] = {"love": 5, "work": 5, "health": 5}

    generator = BlockGenerator()
    blocks = generator.generate([], notes_by_step, events_by_step, step_times, contributions_by_step)
    assert blocks[0].tone_code == "negative"

def test_min_block_1_step(base_data):
    step_times, notes_by_step, events_by_step, contributions_by_step = base_data
    # Pivot at step 7 splits second standard block [4-8) into [4,7) (3 steps) and [7,8) (1 step)
    pivot = TurningPoint(local_time=step_times[7], reason="delta_note", categories_impacted=["love"], trigger_event=None, severity=1.0)

    generator = BlockGenerator()
    blocks = generator.generate([pivot], notes_by_step, events_by_step, step_times, contributions_by_step)

    assert len(blocks) == 25
    one_step_blocks = [b for b in blocks if b.end_local - b.start_local == timedelta(minutes=15)]
    assert len(one_step_blocks) == 1
    assert one_step_blocks[0].start_local == step_times[7]

def test_driver_traceable(base_data):
    step_times, notes_by_step, events_by_step, _ = base_data
    event = create_event(50, step_times[0])
    contrib_dict = {"love": 0.8, "work": 0.2, "health": 0.1}
    contributions_by_step = [[] for _ in range(96)]
    for i in range(4):
        contributions_by_step[i] = [(event, contrib_dict)]

    generator = BlockGenerator()
    blocks = generator.generate([], notes_by_step, events_by_step, step_times, contributions_by_step)

    assert event in blocks[0].driver_events
