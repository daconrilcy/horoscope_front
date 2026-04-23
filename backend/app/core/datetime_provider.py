from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, tzinfo
from zoneinfo import ZoneInfo


@dataclass(frozen=True, slots=True)
class DatetimeProvider:
    """Centralise les accès à l'horloge système backend."""

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    def now(self, tz: tzinfo | str | None = None) -> datetime:
        resolved_tz = self._resolve_timezone(tz)
        return datetime.now(resolved_tz) if resolved_tz is not None else datetime.now()

    def today(self, tz: tzinfo | str | None = None) -> date:
        resolved_tz = self._resolve_timezone(tz)
        return self.now(resolved_tz).date() if resolved_tz is not None else date.today()

    def utc_isoformat(self) -> str:
        return self.utcnow().isoformat()

    @staticmethod
    def _resolve_timezone(tz: tzinfo | str | None) -> tzinfo | None:
        if tz is None:
            return None
        if isinstance(tz, str):
            return ZoneInfo(tz)
        return tz


datetime_provider = DatetimeProvider()


def utc_now() -> datetime:
    return datetime_provider.utcnow()


def current_datetime(tz: tzinfo | str | None = None) -> datetime:
    return datetime_provider.now(tz)


def current_date(tz: tzinfo | str | None = None) -> date:
    return datetime_provider.today(tz)
