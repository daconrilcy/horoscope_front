import pytest
from app.prediction.calibrator import PercentileCalibrator, DEFAULT_CALIBRATION
from app.prediction.aggregator import DayAggregation, CategoryAggregation
from app.infra.db.repositories.prediction_schemas import CalibrationData

def test_day_relative_gives_spread():
    calibrator = PercentileCalibrator()
    
    # 5 categories with varied raw_days
    categories = {
        "love": CategoryAggregation(category_code="love", raw_day=-0.3),
        "work": CategoryAggregation(category_code="work", raw_day=-0.1),
        "health": CategoryAggregation(category_code="health", raw_day=0.0),
        "money": CategoryAggregation(category_code="money", raw_day=0.2),
        "energy": CategoryAggregation(category_code="energy", raw_day=0.4),
    }
    day_agg = DayAggregation(categories=categories)
    
    # All provisional (no calibration data)
    calibrations = {cat: None for cat in categories}
    
    # Use the new method (to be implemented)
    results = calibrator.calibrate_all_provisional_aware(day_agg, calibrations)
    
    # We expect spread, not all 10/20
    assert results["love"] < 10
    assert results["energy"] > 10
    assert results["love"] < results["work"] < results["health"] < results["money"] < results["energy"]

def test_degenerate_day_fallback():
    calibrator = PercentileCalibrator()
    
    # All raw_day identical
    categories = {
        "love": CategoryAggregation(category_code="love", raw_day=0.0),
        "work": CategoryAggregation(category_code="work", raw_day=0.0),
        "health": CategoryAggregation(category_code="health", raw_day=0.0),
        "money": CategoryAggregation(category_code="money", raw_day=0.0),
        "energy": CategoryAggregation(category_code="energy", raw_day=0.0),
    }
    day_agg = DayAggregation(categories=categories)
    calibrations = {cat: None for cat in categories}
    
    results = calibrator.calibrate_all_provisional_aware(day_agg, calibrations)
    
    # Should fallback to DEFAULT_CALIBRATION -> 10/20 for raw_day=0.0
    for score in results.values():
        assert score == 10

def test_mixed_calibration():
    calibrator = PercentileCalibrator()
    
    # 2 calibrated + 4 provisional
    categories = {
        "love": CategoryAggregation(category_code="love", raw_day=1.0), # Calibrated
        "work": CategoryAggregation(category_code="work", raw_day=-1.0), # Calibrated
        "health": CategoryAggregation(category_code="health", raw_day=-0.1), # Provisional
        "money": CategoryAggregation(category_code="money", raw_day=0.0), # Provisional
        "energy": CategoryAggregation(category_code="energy", raw_day=0.1), # Provisional
        "mood": CategoryAggregation(category_code="mood", raw_day=0.2), # Provisional
    }
    day_agg = DayAggregation(categories=categories)
    
    real_cal = CalibrationData(p05=-2, p25=-1, p50=0, p75=1, p95=2, sample_size=100, calibration_label="real")
    
    calibrations = {
        "love": real_cal,
        "work": real_cal,
        "health": None,
        "money": None,
        "energy": None,
        "mood": None,
    }
    
    results = calibrator.calibrate_all_provisional_aware(day_agg, calibrations)
    
    # Real calibrated categories should use their calibration
    # raw_day=1.0 with p75=1.0 -> target 14
    assert results["love"] == 14
    # raw_day=-1.0 with p25=-1.0 -> target 6
    assert results["work"] == 6
    
    # Provisional categories should use day-relative (spread around 10)
    assert results["health"] < 10
    assert results["mood"] > 10

def test_too_few_provisional():
    calibrator = PercentileCalibrator()
    
    # Only 2 provisional categories
    categories = {
        "love": CategoryAggregation(category_code="love", raw_day=1.0),
        "work": CategoryAggregation(category_code="work", raw_day=-1.0),
        "health": CategoryAggregation(category_code="health", raw_day=0.5), # Provisional
        "money": CategoryAggregation(category_code="money", raw_day=-0.5), # Provisional
    }
    day_agg = DayAggregation(categories=categories)
    
    real_cal = CalibrationData(p05=-2, p25=-1, p50=0, p75=1, p95=2, sample_size=100, calibration_label="real")
    
    calibrations = {
        "love": real_cal,
        "work": real_cal,
        "health": None,
        "money": None,
    }
    
    results = calibrator.calibrate_all_provisional_aware(day_agg, calibrations)
    
    # Health raw_day=0.5 with DEFAULT_CALIBRATION (p75=0.5) -> target 14
    assert results["health"] == 14
    # Money raw_day=-0.5 with DEFAULT_CALIBRATION (p25=-0.5) -> target 6
    assert results["money"] == 6
