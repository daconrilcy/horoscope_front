from datetime import UTC, date, datetime

import pytest

from app.prediction.persisted_baseline import PersistedUserBaseline
from app.prediction.relative_scoring_calculator import RelativeScoringCalculator


def create_mock_baseline(cat_code, mean, std, p10, p50, p90, g_type="day", g_val="all"):
    return PersistedUserBaseline(
        id=1,
        user_id=1,
        category_id=1,
        category_code=cat_code,
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        window_days=365,
        window_start_date=date(2025, 3, 11),
        window_end_date=date(2026, 3, 11),
        mean_raw_score=mean,
        std_raw_score=std,
        mean_note_20=10.0,
        std_note_20=2.0,
        p10=p10,
        p50=p50,
        p90=p90,
        sample_size_days=365,
        computed_at=datetime.now(UTC),
        granularity_type=g_type,
        granularity_value=g_val,
    )


def test_relative_scoring_nominal_granular():
    calculator = RelativeScoringCalculator()

    # 1.5 raw score
    # Day: mean 1.0, std 0.5 -> z_abs = 1.0
    # Slot: mean 2.0, std 0.5 -> z_slot = -1.0
    # Season: mean 0.5, std 0.5 -> z_season = 2.0
    baselines = {
        "work": {
            "day": create_mock_baseline("work", 1.0, 0.5, 0.5, 1.0, 1.5),
            "slot": create_mock_baseline(
                "work", 2.0, 0.5, 1.5, 2.0, 2.5, g_type="slot", g_val="morning"
            ),
            "season": create_mock_baseline(
                "work", 0.5, 0.5, 0.0, 0.5, 1.0, g_type="season", g_val="spring"
            ),
        },
    }
    raw_scores = {"work": 1.5}

    results = calculator.compute_all(raw_scores, baselines)

    score = results["work"]
    assert score.z_abs == pytest.approx(1.0)
    assert score.z_slot == pytest.approx(-1.0)
    assert score.z_season == pytest.approx(2.0)
    assert score.rarity > 0


def test_relative_scoring_ranking_by_intensity():
    calculator = RelativeScoringCalculator()

    # work: z_abs = 1.0
    # love: z_abs = -3.0 (intense negative)
    # money: z_abs = 0.5
    baselines = {
        "work": {"day": create_mock_baseline("work", 1.0, 1.0, 0.0, 1.0, 2.0)},
        "love": {"day": create_mock_baseline("love", 4.0, 1.0, 3.0, 4.0, 5.0)},
        "money": {"day": create_mock_baseline("money", 1.0, 1.0, 0.0, 1.0, 2.0)},
    }
    raw_scores = {"work": 2.0, "love": 1.0, "money": 1.5}

    results = calculator.compute_all(raw_scores, baselines)

    # Ranking should be: love (abs(z)=3), work (abs(z)=1), money (abs(z)=0.5)
    assert results["love"].relative_rank == 1
    assert results["work"].relative_rank == 2
    assert results["money"].relative_rank == 3


def test_relative_scoring_rarity_fallback():
    calculator = RelativeScoringCalculator()

    # Day: variance null -> z_abs is None
    baselines = {"work": {"day": create_mock_baseline("work", 1.0, 0.0, 1.0, 1.0, 1.0)}}
    raw_scores = {"work": 1.5}

    results = calculator.compute_all(raw_scores, baselines)

    score = results["work"]
    assert score.z_abs is None
    # Rarity should still be calculated from percentile
    assert score.rarity is not None
    assert score.rarity > 0
