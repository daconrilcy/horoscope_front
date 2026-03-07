from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.prediction.temporal_sampler import DayGrid, TemporalSampler

PARIS_COORDS = (48.8566, 2.3522)
PARIS_TZ = "Europe/Paris"


def build_paris_grid(local_date: date) -> DayGrid:
    sampler = TemporalSampler()
    latitude, longitude = PARIS_COORDS
    return sampler.build_day_grid(local_date, PARIS_TZ, latitude, longitude)


def test_standard_day_has_96_samples() -> None:
    grid = build_paris_grid(date(2026, 3, 7))

    assert isinstance(grid, DayGrid)
    assert len(grid.samples) == 96
    assert grid.local_date == date(2026, 3, 7)
    assert grid.timezone == PARIS_TZ


def test_sample_ut_local_coherent() -> None:
    sampler = TemporalSampler()
    grid = build_paris_grid(date(2026, 3, 7))

    for point in grid.samples:
        jd_check = sampler._datetime_to_jd(point.local_time)
        assert point.ut_time == pytest.approx(jd_check, abs=1e-9)


def test_ut_start_end_covers_full_day() -> None:
    sampler = TemporalSampler()
    local_date = date(2026, 3, 7)
    tz = ZoneInfo(PARIS_TZ)
    grid = build_paris_grid(local_date)

    expected_start = datetime.combine(local_date, time.min, tzinfo=tz)
    expected_end = datetime.combine(local_date, time(23, 59, 59), tzinfo=tz)

    assert grid.ut_start == pytest.approx(sampler._datetime_to_jd(expected_start))
    assert grid.ut_end == pytest.approx(sampler._datetime_to_jd(expected_end))
    assert grid.ut_start <= grid.samples[0].ut_time
    assert grid.ut_end >= grid.samples[-1].ut_time


def test_sunrise_sunset_present() -> None:
    grid = build_paris_grid(date(2026, 3, 7))

    assert grid.sunrise_ut is not None
    assert grid.sunset_ut is not None
    assert grid.sunrise_ut < grid.sunset_ut


def test_refine_around_yields_1min_steps_centered_on_target() -> None:
    sampler = TemporalSampler()
    target_jd = 2461100.5
    radius_minutes = 5
    one_minute_jd = 1 / (24 * 60)

    points = sampler.refine_around(target_jd, radius_minutes=radius_minutes)

    assert len(points) == 2 * radius_minutes
    assert points[0].ut_time == pytest.approx(target_jd - ((radius_minutes - 0.5) * one_minute_jd))
    assert points[-1].ut_time == pytest.approx(target_jd + ((radius_minutes - 0.5) * one_minute_jd))

    for current, nxt in zip(points, points[1:]):
        assert nxt.ut_time - current.ut_time == pytest.approx(one_minute_jd, abs=1e-10)


def test_dst_spring_forward_has_92_samples_and_stays_in_day() -> None:
    grid = build_paris_grid(date(2026, 3, 29))

    assert len(grid.samples) == 92
    assert all(point.local_time.date() == date(2026, 3, 29) for point in grid.samples)


def test_dst_fall_back_has_100_samples_and_stays_in_day() -> None:
    grid = build_paris_grid(date(2026, 10, 25))

    assert len(grid.samples) == 100
    assert all(point.local_time.date() == date(2026, 10, 25) for point in grid.samples)


def test_dst_days_keep_local_15_minute_spacing() -> None:
    for local_date in (date(2026, 3, 29), date(2026, 10, 25)):
        grid = build_paris_grid(local_date)

        for current, nxt in zip(grid.samples, grid.samples[1:]):
            assert nxt.local_time - current.local_time in (
                timedelta(minutes=15),
                timedelta(minutes=75),
                timedelta(minutes=-45),
            )
