"""Tests de localisation des contextes natals LLM."""

from __future__ import annotations

from app.services.llm_generation.shared.natal_context import (
    AstrologyLabels,
    build_chat_natal_hint,
    build_natal_chart_summary,
)
from app.tests.helpers.natal_result_factory import make_natal_result


def test_natal_summary_uses_astrology_labels() -> None:
    """Le résumé natal humain consomme les libellés résolus."""
    labels = AstrologyLabels(
        effective_language_code="en",
        sign_labels={"gemini": "Gemini", "cancer": "Cancer", "libra": "Libra"},
    )

    summary = build_natal_chart_summary(
        natal_result=make_natal_result(),
        birth_place="Paris",
        birth_date="1990-06-15",
        birth_time="14:30",
        labels=labels,
    )

    assert "SOLEIL: Gemini" in summary
    assert "LUNE: Cancer" in summary
    assert "ASCENDANT: Libra" in summary


def test_chat_natal_hint_uses_astrology_labels() -> None:
    """Le hint de chat conserve les positions et localise les signes affichés."""
    labels = AstrologyLabels(
        effective_language_code="en",
        sign_labels={"gemini": "Gemini", "cancer": "Cancer", "libra": "Libra"},
    )

    hint = build_chat_natal_hint(make_natal_result(), labels=labels)

    assert "Soleil en Gemini" in hint
    assert "Lune en Cancer" in hint
    assert "Ascendant Libra" in hint
