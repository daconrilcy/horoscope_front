from __future__ import annotations

from datetime import UTC
from zoneinfo import ZoneInfo

from app.core.datetime_provider import DatetimeProvider


def test_utcnow_returns_timezone_aware_utc_datetime() -> None:
    provider = DatetimeProvider()

    value = provider.utcnow()

    assert value.tzinfo == UTC


def test_now_accepts_timezone_name() -> None:
    provider = DatetimeProvider()

    value = provider.now("Europe/Paris")

    assert value.tzinfo is not None
    assert value.tzinfo.utcoffset(value) == ZoneInfo("Europe/Paris").utcoffset(value)


def test_today_accepts_timezone_object() -> None:
    provider = DatetimeProvider()

    value = provider.today(ZoneInfo("UTC"))

    assert value == provider.now(ZoneInfo("UTC")).date()
