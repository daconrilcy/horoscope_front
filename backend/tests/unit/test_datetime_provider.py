# Ce module valide le contrat public du provider DateTime backend.
"""Tests unitaires du provider centralise de date et heure."""

from __future__ import annotations

from datetime import UTC
from zoneinfo import ZoneInfo

from app.core.datetime_provider import DatetimeProvider


def test_utcnow_returns_timezone_aware_utc_datetime() -> None:
    """Verifie que l'horloge UTC retourne un datetime timezone-aware."""
    provider = DatetimeProvider()

    value = provider.utcnow()

    assert value.tzinfo == UTC


def test_now_accepts_timezone_name() -> None:
    """Verifie la resolution d'une timezone IANA passee sous forme de chaine."""
    provider = DatetimeProvider()

    value = provider.now("Europe/Paris")

    assert value.tzinfo is not None
    assert value.tzinfo.utcoffset(value) == ZoneInfo("Europe/Paris").utcoffset(value)


def test_today_accepts_timezone_object() -> None:
    """Verifie le calcul de date courante avec une timezone explicite."""
    provider = DatetimeProvider()

    value = provider.today(ZoneInfo("UTC"))

    assert value == provider.now(ZoneInfo("UTC")).date()
