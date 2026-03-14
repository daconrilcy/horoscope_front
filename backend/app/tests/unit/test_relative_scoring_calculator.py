from datetime import datetime

from app.prediction.persisted_baseline import PersistedUserBaseline
from app.prediction.relative_scoring_calculator import RelativeScoringCalculator


def test_calculate_nominal_z_score():
    calculator = RelativeScoringCalculator()

    raw_scores = {"love": 15.0}
    baselines = {
        "love": PersistedUserBaseline(
            id=1,
            user_id=1,
            category_id=1,
            category_code="love",
            reference_version_id=1,
            ruleset_id=1,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=None,
            window_end_date=None,
            mean_raw_score=10.0,
            std_raw_score=2.0,
            mean_note_20=12.0,
            std_note_20=1.0,
            p10=7.0,
            p50=10.0,
            p90=13.0,
            sample_size_days=365,
            computed_at=datetime.now(),
        )
    }

    results = calculator.compute_all(raw_scores, baselines)

    score = results["love"]
    assert score.is_available is True
    assert score.relative_z_score == 2.5  # (15 - 10) / 2
    assert score.relative_percentile > 0.9
    assert score.relative_rank == 1


def test_calculate_null_variance_fallback():
    calculator = RelativeScoringCalculator()

    raw_scores = {"love": 15.0}
    baselines = {
        "love": PersistedUserBaseline(
            id=1,
            user_id=1,
            category_id=1,
            category_code="love",
            reference_version_id=1,
            ruleset_id=1,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=None,
            window_end_date=None,
            mean_raw_score=10.0,
            std_raw_score=0.0,  # NULL VARIANCE
            mean_note_20=12.0,
            std_note_20=1.0,
            p10=7.0,
            p50=10.0,
            p90=13.0,
            sample_size_days=365,
            computed_at=datetime.now(),
        )
    }

    results = calculator.compute_all(raw_scores, baselines)

    score = results["love"]
    assert score.is_available is True
    assert score.relative_z_score is None
    assert score.fallback_reason == "variance_null"
    assert score.relative_percentile is not None  # Percentile should still work as approximation
    assert score.relative_rank == 1


def test_calculate_missing_baseline():
    calculator = RelativeScoringCalculator()

    raw_scores = {"love": 15.0}
    baselines = {}

    results = calculator.compute_all(raw_scores, baselines)

    score = results["love"]
    assert score.is_available is False
    assert score.fallback_reason == "baseline_missing"


def test_calculate_ranking():
    calculator = RelativeScoringCalculator()

    raw_scores = {"love": 15.0, "work": 12.0}
    baselines = {
        "love": PersistedUserBaseline(
            id=1,
            user_id=1,
            category_id=1,
            category_code="love",
            reference_version_id=1,
            ruleset_id=1,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=None,
            window_end_date=None,
            mean_raw_score=10.0,
            std_raw_score=5.0,  # Z = 1.0
            mean_note_20=12.0,
            std_note_20=1.0,
            p10=7.0,
            p50=10.0,
            p90=13.0,
            sample_size_days=365,
            computed_at=datetime.now(),
        ),
        "work": PersistedUserBaseline(
            id=1,
            user_id=1,
            category_id=2,
            category_code="work",
            reference_version_id=1,
            ruleset_id=1,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=None,
            window_end_date=None,
            mean_raw_score=5.0,
            std_raw_score=1.0,  # Z = 7.0
            mean_note_20=12.0,
            std_note_20=1.0,
            p10=3.0,
            p50=5.0,
            p90=7.0,
            sample_size_days=365,
            computed_at=datetime.now(),
        ),
    }

    results = calculator.compute_all(raw_scores, baselines)

    assert results["work"].relative_rank == 1
    assert results["love"].relative_rank == 2


def test_calculate_ranking_uses_alphabetical_tie_break():
    calculator = RelativeScoringCalculator()

    raw_scores = {"work": 8.0, "love": 8.0}
    baselines = {
        "love": PersistedUserBaseline(
            id=1,
            user_id=1,
            category_id=1,
            category_code="love",
            reference_version_id=1,
            ruleset_id=1,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=None,
            window_end_date=None,
            mean_raw_score=6.0,
            std_raw_score=2.0,
            mean_note_20=12.0,
            std_note_20=1.0,
            p10=4.0,
            p50=6.0,
            p90=8.0,
            sample_size_days=365,
            computed_at=datetime.now(),
        ),
        "work": PersistedUserBaseline(
            id=2,
            user_id=1,
            category_id=2,
            category_code="work",
            reference_version_id=1,
            ruleset_id=1,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=None,
            window_end_date=None,
            mean_raw_score=6.0,
            std_raw_score=2.0,
            mean_note_20=12.0,
            std_note_20=1.0,
            p10=4.0,
            p50=6.0,
            p90=8.0,
            sample_size_days=365,
            computed_at=datetime.now(),
        ),
    }

    results = calculator.compute_all(raw_scores, baselines)

    assert results["love"].relative_rank == 1
    assert results["work"].relative_rank == 2
