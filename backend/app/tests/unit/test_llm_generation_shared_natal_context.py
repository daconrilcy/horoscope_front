"""Valide les helpers natals partages entre guidance et consultation."""

from types import SimpleNamespace

import pytest

from app.services.llm_generation.shared.natal_context import (
    build_natal_chart_summary_with_defaults,
    build_user_natal_chart_summary_context,
    detect_degraded_natal_mode,
)
from app.services.user_natal_chart_service import UserNatalChartServiceError


def test_detect_degraded_natal_mode_handles_missing_time_and_location() -> None:
    """Le helper partage doit detecter les trois variantes degradees attendues."""
    assert detect_degraded_natal_mode(birth_time="12:00", birth_place="Paris") is None
    assert detect_degraded_natal_mode(birth_time=None, birth_place="Paris") == "no_time"
    assert detect_degraded_natal_mode(birth_time="12:00", birth_place="") == "no_location"
    assert detect_degraded_natal_mode(birth_time=None, birth_place=None) == "no_location_no_time"


def test_build_natal_chart_summary_with_defaults_uses_safe_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le resume partage doit propager les fallbacks de date, heure et lieu."""
    captured_kwargs: dict[str, object] = {}

    def fake_build_natal_chart_summary(**kwargs):
        captured_kwargs.update(kwargs)
        return "resume partage"

    monkeypatch.setattr(
        "app.services.llm_generation.shared.natal_context.build_natal_chart_summary",
        fake_build_natal_chart_summary,
    )

    result = build_natal_chart_summary_with_defaults(
        natal_result=SimpleNamespace(),
        birth_date="1990-01-01",
        birth_time=None,
        birth_place=None,
    )

    assert result == "resume partage"
    assert captured_kwargs["birth_time"] == "00:00"
    assert captured_kwargs["birth_place"] == "Non connu"
    assert captured_kwargs["degraded_mode"] == "no_location_no_time"


def test_build_user_natal_chart_summary_context_returns_none_when_chart_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L absence de theme natal persiste ne doit pas produire d erreur applicative."""

    monkeypatch.setattr(
        "app.services.llm_generation.shared.natal_context.UserNatalChartService.get_latest_for_user",
        lambda db, user_id: (_ for _ in ()).throw(
            UserNatalChartServiceError("natal_chart_not_found", "missing chart")
        ),
    )

    result = build_user_natal_chart_summary_context(
        db=SimpleNamespace(),
        user_id=12,
        birth_date="1990-01-01",
        birth_time="12:00",
        birth_place="Paris",
    )

    assert result is None
