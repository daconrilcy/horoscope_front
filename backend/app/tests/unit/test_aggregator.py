import pytest

from app.prediction.aggregator import RAW_DAY_MAX, RAW_STEP_MAX, TemporalAggregator


@pytest.fixture
def aggregator():
    return TemporalAggregator()


def test_raw_step_value_stored_correctly(aggregator):
    # The caller pre-sums contributions per step; the aggregator stores and clamps the result.
    data = [{"love": 1.0}]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].raw_steps[0] == 1.0


def test_raw_step_clamped_max(aggregator):
    data = [{"love": 5.0}]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].raw_steps[0] == RAW_STEP_MAX


def test_raw_step_clamped_min(aggregator):
    data = [{"love": -5.0}]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].raw_steps[0] == -RAW_STEP_MAX


def test_mean_correct(aggregator):
    data = [{"love": 1.0}, {"love": 2.0}, {"love": 3.0}]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].mean == 2.0


def test_peak90_identifies_peak(aggregator):
    # Peak of 6 steps in a series
    steps = [0.0] * 10
    for i in range(2, 8):
        steps[i] = 1.0
    # Mean of steps[2:8] is 1.0. Others are lower.
    data = [{"love": s} for s in steps]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].peak90 == 1.0


def test_close_last_2h(aggregator):
    # Close = mean of last 8 steps
    steps = [0.0] * 10 + [1.0] * 8
    data = [{"love": s} for s in steps]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].close == 1.0


def test_raw_day_formula(aggregator):
    # Mean=1.0, Peak90=1.0, Close=1.0 -> RawDay = 0.7*1 + 0.2*1 + 0.1*1 = 1.0
    data = [{"love": 1.0}] * 10
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].raw_day == pytest.approx(1.0)


def test_raw_day_clamped_max(aggregator):
    # RawStep clamped to 3.0. Mean=3, Peak=3, Close=3. Formula gives 3.0.
    data = [{"love": 3.0}] * 10
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].raw_day == RAW_DAY_MAX


def test_raw_day_clamped_min(aggregator):
    data = [{"love": -3.0}] * 10
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].raw_day == -RAW_DAY_MAX


def test_power_max_abs(aggregator):
    data = [{"love": -2.0}, {"love": 1.0}, {"love": 0.5}]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].power == 2.0


def test_volatility_nonzero(aggregator):
    data = [{"love": 1.0}, {"love": -1.0}, {"love": 1.0}, {"love": -1.0}]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].volatility > 0


def test_no_events_zero(aggregator):
    data = []
    result = aggregator.aggregate(data, ["love"])
    agg = result.categories["love"]
    assert agg.power == 0.0
    assert agg.volatility == 0.0
    assert agg.raw_day == 0.0


def test_multiple_categories_isolated(aggregator):
    # Data for two categories: "love" positive, "career" negative — must not bleed into each other.
    data = [{"love": 2.0, "career": -2.0}, {"love": 2.0, "career": -2.0}]
    result = aggregator.aggregate(data, ["love", "career"])
    assert result.categories["love"].mean == 2.0
    assert result.categories["love"].raw_day > 0
    assert result.categories["career"].mean == -2.0
    assert result.categories["career"].raw_day < 0


def test_category_absent_from_steps_defaults_to_zero(aggregator):
    # "career" is in category_codes but never appears in any step dict → all metrics = 0.0
    data = [{"love": 1.0}, {"love": 1.0}]
    result = aggregator.aggregate(data, ["love", "career"])
    career = result.categories["career"]
    assert career.mean == 0.0
    assert career.power == 0.0
    assert career.volatility == 0.0
    assert career.raw_day == 0.0


def test_peak90_exactly_window_size(aggregator):
    # L1: exactly PEAK90_WINDOW=6 steps — enters the max() branch with a single window
    data = [{"love": s} for s in [1.0, 2.0, 3.0, 2.0, 1.0, 0.0]]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].peak90 == pytest.approx(9.0 / 6)


def test_peak90_detects_mid_series_peak(aggregator):
    # L2: peak is in the middle; surrounding steps are lower — must identify the correct window
    steps = [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0]
    data = [{"love": s} for s in steps]
    result = aggregator.aggregate(data, ["love"])
    # Best window of 6 is steps[2:8] → mean = 1.0; other windows have lower means
    assert result.categories["love"].peak90 == pytest.approx(1.0)


def test_close_fewer_than_close_window_steps(aggregator):
    # L3: fewer than 8 total steps → close = mean of all available steps
    data = [{"love": 1.0}, {"love": 2.0}, {"love": 3.0}]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].close == pytest.approx(2.0)


def test_peak90_single_step(aggregator):
    # L4: 1 step < PEAK90_WINDOW → returns mean([x]) = x
    data = [{"love": 2.5}]
    result = aggregator.aggregate(data, ["love"])
    assert result.categories["love"].peak90 == pytest.approx(2.5)
