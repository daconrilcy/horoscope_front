from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_MONTH_NAMES_FR = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}


class SupportsCurrentContext(Protocol):
    current_timezone: str | None
    birth_timezone: str | None
    current_location_display: str | None
    birth_city: str | None
    birth_country: str | None
    birth_place: str | None


@dataclass(frozen=True, slots=True)
class CurrentPromptContext:
    current_datetime: str | None
    current_timezone: str | None
    current_location: str | None


def _resolve_timezone_name(profile: SupportsCurrentContext) -> str | None:
    candidate = (profile.current_timezone or profile.birth_timezone or "").strip()
    if not candidate:
        return None
    try:
        ZoneInfo(candidate)
    except ZoneInfoNotFoundError:
        return "UTC"
    return candidate


def _format_current_datetime(now: datetime, timezone_name: str) -> str:
    month_name = _MONTH_NAMES_FR[now.month]
    return (
        f"{now.day:02d} {month_name} {now.year} à {now.hour:02d}h{now.minute:02d} ({timezone_name})"
    )


def build_current_prompt_context(
    profile: SupportsCurrentContext,
    *,
    now: datetime | None = None,
) -> CurrentPromptContext:
    timezone_name = _resolve_timezone_name(profile)
    current_datetime = None
    if timezone_name is not None:
        tz = ZoneInfo(timezone_name)
        current_now = now.astimezone(tz) if now is not None else datetime.now(tz)
        current_datetime = _format_current_datetime(current_now, timezone_name)

    current_location = profile.current_location_display or (
        f"{profile.birth_city}, {profile.birth_country}"
        if profile.birth_city and profile.birth_country
        else profile.birth_place
    )

    return CurrentPromptContext(
        current_datetime=current_datetime,
        current_timezone=timezone_name,
        current_location=current_location,
    )
