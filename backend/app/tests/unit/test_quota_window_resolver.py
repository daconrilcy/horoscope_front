from datetime import datetime, timezone

import pytest

from app.services.quota_window_resolver import QuotaWindowResolver

UTC = timezone.utc


def test_day_calendar_period_1():
    ref_dt = datetime(2026, 3, 15, 14, 30, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("day", 1, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 3, 15, 0, 0, tzinfo=UTC)
    assert window.window_end == datetime(2026, 3, 16, 0, 0, tzinfo=UTC)


def test_week_calendar_period_1():
    ref_dt = datetime(2026, 3, 18, 10, 0, tzinfo=UTC)  # Mercredi
    window = QuotaWindowResolver.compute_window("week", 1, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 3, 16, 0, 0, tzinfo=UTC)  # Lundi
    assert window.window_end == datetime(2026, 3, 23, 0, 0, tzinfo=UTC)


def test_month_calendar_period_1():
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("month", 1, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 3, 1, 0, 0, tzinfo=UTC)
    assert window.window_end == datetime(2026, 4, 1, 0, 0, tzinfo=UTC)


def test_year_calendar_period_1():
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("year", 1, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert window.window_end == datetime(2027, 1, 1, 0, 0, tzinfo=UTC)


def test_lifetime():
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("lifetime", 1, "lifetime", ref_dt)
    assert window.window_start == datetime(1970, 1, 1, 0, 0, tzinfo=UTC)
    assert window.window_end is None


def test_day_calendar_period_2():
    ref_dt1 = datetime(2026, 3, 14, 10, 0, tzinfo=UTC)
    ref_dt2 = datetime(2026, 3, 15, 23, 59, tzinfo=UTC)
    window1 = QuotaWindowResolver.compute_window("day", 2, "calendar", ref_dt1)
    window2 = QuotaWindowResolver.compute_window("day", 2, "calendar", ref_dt2)
    assert window1.window_start == window2.window_start
    assert window1.window_end == window2.window_end
    # Slot size is 2 days. 2026-03-14 is 20526 days since epoch. 20526 // 2 = 10263.
    # 10263 * 2 = 20526. 20526 days since epoch is 2026-03-14.
    assert window1.window_start == datetime(2026, 3, 14, 0, 0, tzinfo=UTC)
    assert window1.window_end == datetime(2026, 3, 16, 0, 0, tzinfo=UTC)


def test_month_calendar_period_3_q1():
    ref_dt = datetime(2026, 1, 15, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("month", 3, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert window.window_end == datetime(2026, 4, 1, 0, 0, tzinfo=UTC)


def test_month_calendar_period_3_q2():
    ref_dt = datetime(2026, 5, 10, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("month", 3, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 4, 1, 0, 0, tzinfo=UTC)
    assert window.window_end == datetime(2026, 7, 1, 0, 0, tzinfo=UTC)


def test_border_midnight():
    ref_dt1 = datetime(2026, 3, 15, 0, 0, 0, tzinfo=UTC)
    ref_dt2 = datetime(2026, 3, 15, 23, 59, 59, 999999, tzinfo=UTC)
    window1 = QuotaWindowResolver.compute_window("day", 1, "calendar", ref_dt1)
    window2 = QuotaWindowResolver.compute_window("day", 1, "calendar", ref_dt2)
    assert window1.window_start == window2.window_start == datetime(2026, 3, 15, 0, 0, tzinfo=UTC)


def test_border_next_day():
    ref_dt = datetime(2026, 3, 16, 0, 0, 0, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("day", 1, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 3, 16, 0, 0, tzinfo=UTC)


def test_ref_dt_paris_converted_to_utc():
    # Europe/Paris in March is UTC+1 (until last Sunday)
    import zoneinfo

    paris = zoneinfo.ZoneInfo("Europe/Paris")
    ref_dt = datetime(2026, 3, 15, 1, 0, tzinfo=paris)  # 2026-03-15 00:00 UTC
    window = QuotaWindowResolver.compute_window("day", 1, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 3, 15, 0, 0, tzinfo=UTC)


def test_naive_ref_dt_raises():
    ref_dt = datetime(2026, 3, 15, 10, 0)
    with pytest.raises(ValueError, match="ref_dt must be timezone-aware"):
        QuotaWindowResolver.compute_window("day", 1, "calendar", ref_dt)


def test_rolling_raises():
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    with pytest.raises(ValueError, match="rolling windows not supported"):
        QuotaWindowResolver.compute_window("day", 1, "rolling", ref_dt)


def test_week_calendar_period_2():
    # Deux ref_dt dans le même slot de 2 semaines → même window_start
    # WEEK_ANCHOR = 1969-12-29 (lundi)
    # 2026-03-16 → window [2026-03-09, 2026-03-23)
    # 2026-03-20 (vendredi de la même semaine) → même fenêtre
    ref_dt1 = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    ref_dt2 = datetime(2026, 3, 20, 10, 0, tzinfo=UTC)
    window1 = QuotaWindowResolver.compute_window("week", 2, "calendar", ref_dt1)
    window2 = QuotaWindowResolver.compute_window("week", 2, "calendar", ref_dt2)
    assert window1.window_start == window2.window_start
    assert window1.window_end == window2.window_end
    # La fenêtre doit faire 14 jours
    assert (window1.window_end - window1.window_start).days == 14


def test_month_calendar_period_3_invariant():
    # ref_dt=2026-03-31 et ref_dt=2026-01-01 → même window_start (même trimestre Q1)
    ref_dt1 = datetime(2026, 1, 1, tzinfo=UTC)
    ref_dt2 = datetime(2026, 3, 31, tzinfo=UTC)
    window1 = QuotaWindowResolver.compute_window("month", 3, "calendar", ref_dt1)
    window2 = QuotaWindowResolver.compute_window("month", 3, "calendar", ref_dt2)
    assert window1.window_start == window2.window_start
    assert window1.window_start == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)


def test_end_of_month():
    # ref_dt = 2026-01-31 → window_end = 2026-02-01 (pas de crash)
    ref_dt = datetime(2026, 1, 31, 23, 59, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("month", 1, "calendar", ref_dt)
    assert window.window_start == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert window.window_end == datetime(2026, 2, 1, 0, 0, tzinfo=UTC)


def test_all_datetimes_utc():
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    window = QuotaWindowResolver.compute_window("day", 1, "calendar", ref_dt)
    assert window.window_start.tzinfo == UTC
    assert window.window_end.tzinfo == UTC


def test_month_transition():
    # Test que le window_start change bien au passage du mois
    ref_dt_last_day = datetime(2026, 3, 31, 23, 59, 59, tzinfo=UTC)
    ref_dt_next_day = datetime(2026, 4, 1, 0, 0, 0, tzinfo=UTC)

    window_march = QuotaWindowResolver.compute_window("month", 1, "calendar", ref_dt_last_day)
    window_april = QuotaWindowResolver.compute_window("month", 1, "calendar", ref_dt_next_day)

    assert window_march.window_start == datetime(2026, 3, 1, 0, 0, tzinfo=UTC)
    assert window_april.window_start == datetime(2026, 4, 1, 0, 0, tzinfo=UTC)
    assert window_march.window_end == window_april.window_start
