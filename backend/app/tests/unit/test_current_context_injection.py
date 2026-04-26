from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.llm_generation.guidance.current_context import build_current_prompt_context
from app.services.user_profile.birth_profile_service import UserBirthProfileData


def _build_profile(**overrides: object) -> UserBirthProfileData:
    payload: dict[str, object] = {
        "birth_date": "1990-01-15",
        "birth_time": "10:30",
        "birth_place": "Paris, France",
        "birth_timezone": "Europe/Paris",
        "birth_city": "Paris",
        "birth_country": "France",
    }
    payload.update(overrides)
    return UserBirthProfileData.model_validate(payload)


def test_current_context_uses_current_timezone_when_available() -> None:
    profile = _build_profile(
        current_timezone="America/New_York",
        current_location_display="New York, United States",
    )

    context = build_current_prompt_context(
        profile,
        now=datetime(2026, 3, 7, 14, 30, tzinfo=timezone.utc),
    )

    assert context.current_timezone == "America/New_York"
    assert context.current_datetime == "07 mars 2026 à 09h30 (America/New_York)"
    assert context.current_location == "New York, United States"


def test_current_context_falls_back_to_birth_timezone() -> None:
    profile = _build_profile(current_timezone=None)

    context = build_current_prompt_context(
        profile,
        now=datetime(2026, 3, 7, 14, 30, tzinfo=timezone.utc),
    )

    assert context.current_timezone == "Europe/Paris"
    assert context.current_datetime == "07 mars 2026 à 15h30 (Europe/Paris)"


def test_current_context_falls_back_to_birth_place_when_no_current_location() -> None:
    profile = _build_profile(current_timezone=None, current_location_display=None)

    context = build_current_prompt_context(profile)

    assert context.current_location == "Paris, France"


def test_current_context_returns_none_when_timezones_are_missing() -> None:
    profile = SimpleNamespace(
        birth_timezone="",
        current_timezone=None,
        current_location_display=None,
        birth_city=None,
        birth_country=None,
        birth_place=None,
    )

    context = build_current_prompt_context(profile)

    assert context.current_timezone is None
    assert context.current_datetime is None
    assert context.current_location is None


def test_current_context_uses_utc_when_timezone_is_invalid() -> None:
    profile = _build_profile(current_timezone="Invalid/Timezone")

    context = build_current_prompt_context(
        profile,
        now=datetime(2026, 3, 7, 14, 30, tzinfo=timezone.utc),
    )

    assert context.current_timezone == "UTC"
    assert context.current_datetime == "07 mars 2026 à 14h30 (UTC)"
