# Ce module fournit le point d'entree unique pour acceder a l'horloge backend.
"""Provider centralise pour les dates et heures courantes du backend."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, tzinfo
from zoneinfo import ZoneInfo


@dataclass(frozen=True, slots=True)
class DatetimeProvider:
    """Centralise les accès à l'horloge système backend."""

    def utcnow(self) -> datetime:
        """Retourne l'instant courant en UTC avec timezone explicite."""
        return datetime.now(UTC)

    def now(self, tz: tzinfo | str | None = None) -> datetime:
        """Retourne l'instant courant dans la timezone demandee."""
        resolved_tz = self._resolve_timezone(tz)
        return datetime.now(resolved_tz) if resolved_tz is not None else datetime.now()

    def today(self, tz: tzinfo | str | None = None) -> date:
        """Retourne la date courante dans la timezone demandee."""
        resolved_tz = self._resolve_timezone(tz)
        return self.now(resolved_tz).date() if resolved_tz is not None else date.today()

    def utc_isoformat(self) -> str:
        """Retourne l'instant UTC courant au format ISO 8601."""
        return self.utcnow().isoformat()

    @staticmethod
    def _resolve_timezone(tz: tzinfo | str | None) -> tzinfo | None:
        """Normalise une timezone fournie sous forme d'objet ou de nom IANA."""
        if tz is None:
            return None
        if isinstance(tz, str):
            return ZoneInfo(tz)
        return tz


datetime_provider = DatetimeProvider()


def utc_now() -> datetime:
    """Expose l'instant UTC courant pour les appels legacy migrables."""
    return datetime_provider.utcnow()


def current_datetime(tz: tzinfo | str | None = None) -> datetime:
    """Expose l'instant courant dans la timezone demandee."""
    return datetime_provider.now(tz)


def current_date(tz: tzinfo | str | None = None) -> date:
    """Expose la date courante dans la timezone demandee."""
    return datetime_provider.today(tz)
