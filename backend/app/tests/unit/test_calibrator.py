import pytest

from app.infra.db.repositories.prediction_schemas import CalibrationData
from app.prediction.aggregator import CategoryAggregation, DayAggregation
from app.prediction.calibrator import PercentileCalibrator


@pytest.fixture
def calibrator():
    return PercentileCalibrator()

@pytest.fixture
def custom_cal():
    return CalibrationData(
        p05=-1.0,
        p25=-0.5,
        p50=0.0,
        p75=0.5,
        p95=1.0,
        sample_size=100
    )

def test_at_p5_returns_1(calibrator, custom_cal):
    # raw_day = P5 -> note = 1 (AC2)
    assert calibrator.calibrate(-1.0, custom_cal) == 1

def test_below_p5_returns_1(calibrator, custom_cal):
    # raw_day < P5 -> note = 1 (AC2)
    assert calibrator.calibrate(-1.5, custom_cal) == 1

def test_at_p95_returns_20(calibrator, custom_cal):
    # raw_day = P95 -> note = 20 (AC3)
    assert calibrator.calibrate(1.0, custom_cal) == 20

def test_above_p95_returns_20(calibrator, custom_cal):
    # raw_day > P95 -> note = 20 (AC3)
    assert calibrator.calibrate(1.5, custom_cal) == 20

def test_midpoint_p5_p25(calibrator, custom_cal):
    # Segment 1 : raw_day = (-1.0 + -0.5) / 2 = -0.75
    # y = 2 + 0.5 * (6 - 2) = 4
    assert calibrator.calibrate(-0.75, custom_cal) == 4

def test_midpoint_p50_p75(calibrator, custom_cal):
    # Segment 3 : raw_day = (0.0 + 0.5) / 2 = 0.25
    # y = 10 + 0.5 * (14 - 10) = 12
    assert calibrator.calibrate(0.25, custom_cal) == 12

def test_all_4_segments(calibrator, custom_cal):
    # Un point au milieu de chacun des 4 segments avec custom_cal
    # Seg 1 (P5→P25): -0.75 → 4
    assert calibrator.calibrate(-0.75, custom_cal) == 4
    # Seg 2 (P25→P50): -0.25 → 8
    assert calibrator.calibrate(-0.25, custom_cal) == 8
    # Seg 3 (P50→P75): 0.25 → 12
    assert calibrator.calibrate(0.25, custom_cal) == 12
    # Seg 4 (P75→P95): 0.75 → 16 (round(16.5) = 16, arrondi banquier)
    assert calibrator.calibrate(0.75, custom_cal) == 16

def test_none_calibration_uses_default(calibrator):
    # DEFAULT_CALIBRATION: p05=-1.5, p25=-0.5, p50=0.0, p75=0.5, p95=1.5
    # raw_day = 0.0 -> P50 -> note = 10
    assert calibrator.calibrate(0.0, None) == 10

def test_note_range(calibrator, custom_cal):
    # 100 valeurs uniformément distribuées dans [-3, +3]
    for i in range(100):
        val = -3.0 + i * 6.0 / 99
        note = calibrator.calibrate(val, custom_cal)
        assert 1 <= note <= 20

def test_deterministic(calibrator, custom_cal):
    val = 0.33
    notes = [calibrator.calibrate(val, custom_cal) for _ in range(10)]
    assert all(n == notes[0] for n in notes)

def test_calibrate_all(calibrator, custom_cal):
    day_agg = DayAggregation(categories={
        "cat1": CategoryAggregation(category_code="cat1", raw_day=-1.0),  # P5 → 1
        "cat2": CategoryAggregation(category_code="cat2", raw_day=0.0),   # P50 → 10
        "cat3": CategoryAggregation(category_code="cat3", raw_day=1.0),   # P95 → 20
    })
    calibrations = {"cat1": custom_cal, "cat2": custom_cal, "cat3": custom_cal}
    results = calibrator.calibrate_all(day_agg, calibrations)
    assert results == {"cat1": 1, "cat2": 10, "cat3": 20}

def test_calibrate_all_missing_category(calibrator):
    # Catégorie absente de calibrations → DEFAULT_CALIBRATION (AC6)
    # raw_day=0.0 avec DEFAULT_CALIBRATION (p50=0.0) → note=10
    day_agg = DayAggregation(categories={
        "cat1": CategoryAggregation(category_code="cat1", raw_day=0.0),
    })
    results = calibrator.calibrate_all(day_agg, {})
    assert results == {"cat1": 10}
