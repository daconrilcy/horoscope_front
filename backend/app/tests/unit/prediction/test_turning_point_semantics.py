from datetime import datetime, timedelta, UTC
from app.prediction.turning_point_detector import TurningPointDetector
from app.prediction.schemas import V3TimeBlock, AstroEvent, V3TurningPoint, V3PrimaryDriver

def test_detect_v3_semantics_emergence():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)
    
    # prev: low intensity, curr: high intensity -> emergence
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 2.0, 0.8, ["work"]),
        V3TimeBlock(1, start + timedelta(hours=2), start + timedelta(hours=4), "rising", 10.0, 0.8, ["work", "love"])
    ]
    
    events = [
        AstroEvent("aspect_exact_to_personal", 0.0, start + timedelta(hours=2), "Sun", "Moon", "conjunction", 0.0, 80, 1.0)
    ]
    
    pivots = detector.detect_v3(blocks, events)
    
    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.change_type == "emergence"
    assert tp.previous_categories == ["work"]
    assert tp.next_categories == ["work", "love"]
    assert tp.primary_driver is not None
    assert tp.primary_driver.event_type == "aspect_exact_to_personal"
    assert tp.primary_driver.body == "Sun"

def test_detect_v3_semantics_attenuation():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)
    
    # prev: high intensity, curr: low intensity -> attenuation
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 10.0, 0.8, ["work"]),
        V3TimeBlock(1, start + timedelta(hours=2), start + timedelta(hours=4), "falling", 2.0, 0.8, ["work"])
    ]
    
    pivots = detector.detect_v3(blocks, [])
    
    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.change_type == "attenuation"

def test_detect_v3_semantics_recomposition():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)

    # Orientation change + enough intensity diff to trigger reason
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "rising", 6.0, 0.8, ["work"]), 
        V3TimeBlock(1, start + timedelta(hours=2), start + timedelta(hours=4), "stable", 7.6, 0.8, ["love"])
    ]

    pivots = detector.detect_v3(blocks, [])

    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.change_type == "recomposition" # Intensity jump < 2.5
    assert tp.previous_categories == ["work"]
    assert tp.next_categories == ["love"]

def test_detect_v3_excludes_midnight():
    detector = TurningPointDetector()
    # Midnight transition
    start = datetime(2026, 3, 11, 22, 0, tzinfo=UTC)
    midnight = datetime(2026, 3, 12, 0, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start, midnight, "stable", 2.0, 0.8, ["work"]),
        V3TimeBlock(1, midnight, midnight + timedelta(hours=2), "rising", 10.0, 0.8, ["work"])
    ]

    pivots = detector.detect_v3(blocks, [])

    # Should be excluded per AC4
    assert len(pivots) == 0

def test_primary_driver_selection_priority():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 12, 0, tzinfo=UTC)

    # Drivers: 1 public exact, 1 ingress, 1 generic
    drivers = [
        AstroEvent("generic_event", 0.0, start, "Mars", None, None, 0.0, 90, 1.0),       
        AstroEvent("moon_sign_ingress", 0.0, start, "Moon", "Aries", None, 0.0, 50, 1.0),
        AstroEvent("aspect_exact_to_personal", 0.0, start, "Sun", "Moon", "conjunction", 0.0, 70, 1.0),
    ]

    # Priority 1: public exact aspect should be chosen over public ingress
    primary = detector._select_primary_driver(drivers)
    assert primary.event_type == "aspect_exact_to_personal"

