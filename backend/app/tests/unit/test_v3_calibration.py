import pytest
from app.prediction.calibrator import PercentileCalibrator
from app.prediction.schemas import V3DailyMetrics
from app.infra.db.repositories.prediction_schemas import CalibrationData

@pytest.fixture
def calibrator():
    return PercentileCalibrator()

@pytest.fixture
def default_cal():
    return CalibrationData(
        p05=-1.0, p25=-0.5, p50=0.0, p75=0.5, p95=1.0,
        sample_size=1000,
        calibration_label="test-v3"
    )

def test_calibrate_v3_flat_day(calibrator, default_cal):
    """A flat day with no relief should be exactly 10."""
    metrics = V3DailyMetrics(
        score_20=10.0,
        level_day=0.0,
        intensity_day=0.0,
        dominance_day=0.0,
        stability_day=20.0, # Very stable
        rarity_percentile=0.0,
        avg_score=1.0, # Neutral
        max_score=1.0,
        min_score=1.0,
        volatility=0.0
    )
    
    score = calibrator.calibrate_v3(metrics, default_cal)
    assert score == pytest.approx(10.0, abs=0.1)

def test_calibrate_v3_intense_ambivalent_day(calibrator, default_cal):
    """
    An intense day with high peaks and lows but avg=1.0
    should NOT be crushed if dominance exists.
    """
    # High intensity, but average is 1.0
    # max_score=2.0 (peak=+1.0), min_score=0.2 (low=-0.8)
    # dominance = 1.0 - 0.8 = 0.2
    metrics = V3DailyMetrics(
        score_20=10.0,
        level_day=0.0,
        intensity_day=15.0, # High intensity
        dominance_day=0.2,
        stability_day=10.0, 
        rarity_percentile=5.0,
        avg_score=1.0,
        max_score=2.0,
        min_score=0.2,
        volatility=0.8
    )
    
    score = calibrator.calibrate_v3(metrics, default_cal)
    assert score > 10.0

def test_calibrate_v3_intense_positive_day(calibrator, default_cal):
    """An intense positive day should have a high score."""
    # level = 1.4-1.0 = 0.4
    # pos_peak = 2.5-1.0 = 1.5
    # neg_peak = 1.0-0.8 = 0.2
    # dominance = 1.5-0.2 = 1.3
    metrics = V3DailyMetrics(
        score_20=10.0,
        level_day=0.4,
        intensity_day=18.0,
        dominance_day=1.3,
        stability_day=15.0,
        rarity_percentile=10.0,
        avg_score=1.4,
        max_score=2.5,
        min_score=0.8,
        volatility=0.5
    )
    
    score = calibrator.calibrate_v3(metrics, default_cal)
    assert score > 16.0 # Highly expressive score

def test_calibrate_v3_unstable_day(calibrator, default_cal):
    """An unstable day should be closer to 10 than a stable one."""
    metrics_stable = V3DailyMetrics(
        score_20=10.0,
        level_day=0.2,
        intensity_day=10.0,
        dominance_day=0.1,
        stability_day=20.0, # Max stability
        rarity_percentile=5.0,
        avg_score=1.2,
        max_score=1.5,
        min_score=0.9,
        volatility=0.2
    )
    
    metrics_unstable = V3DailyMetrics(
        score_20=10.0,
        level_day=0.2,
        intensity_day=10.0,
        dominance_day=0.1,
        stability_day=2.0, # Low stability
        rarity_percentile=5.0,
        avg_score=1.2,
        max_score=1.5,
        min_score=0.9,
        volatility=0.8
    )
    
    score_stable = calibrator.calibrate_v3(metrics_stable, default_cal)
    score_unstable = calibrator.calibrate_v3(metrics_unstable, default_cal)
    
    assert abs(score_stable - 10.0) > abs(score_unstable - 10.0)

def test_compare_v2_v3_calibration(calibrator, default_cal):
    """
    Compare V2 style (simple mean) vs V3 style.
    V2 on a slightly positive but intense day might be crushed.
    """
    # Raw level = 1.1 (slightly positive)
    # But high intensity and positive dominance
    metrics = V3DailyMetrics(
        score_20=10.0,
        level_day=0.1,
        intensity_day=15.0,
        dominance_day=0.2,
        stability_day=15.0,
        rarity_percentile=5.0,
        avg_score=1.1,
        max_score=2.0,
        min_score=0.8,
        volatility=0.4
    )
    
    # V2 style would be round(10 + (1.1-1.0)*5.0) = 10.5 -> 11
    # V3 should be more expressive
    score_v3 = calibrator.calibrate_v3(metrics, default_cal)
    
    # V2 simple linear calibration
    score_v2_linear = 10.0 + (metrics.avg_score - 1.0) * 5.0
    
    # V3 should deviate more from 10 because it's intense and positive dominant
    assert abs(score_v3 - 10.0) > abs(score_v2_linear - 10.0)
    assert score_v3 > 11.0 # Should be higher than just 10.5
