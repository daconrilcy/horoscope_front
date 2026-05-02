"""Gardes anti-retour pour les anciens chemins prompts LLM."""

from __future__ import annotations

import pytest

from app.domain.llm.prompting.catalog import (
    PROMPT_FALLBACK_CONFIGS,
    build_fallback_use_case_config,
)

SUPPORTED_FALLBACK_USE_CASE_KEYS = frozenset(
    {
        "astrologer_selection_help",
        "chat",
        "chat_astrologer",
        "event_guidance",
        "guidance_daily",
        "guidance_weekly",
        "guidance_contextual",
        "natal_interpretation",
        "natal_interpretation_short",
        "natal_long_free",
        "horoscope_daily",
    }
)


def test_supported_use_cases_are_absent_from_prompt_fallback_configs() -> None:
    """Bloque le retour de prompts runtime pour les familles gouvernees."""

    assert PROMPT_FALLBACK_CONFIGS.keys().isdisjoint(SUPPORTED_FALLBACK_USE_CASE_KEYS)


@pytest.mark.parametrize("use_case_key", sorted(SUPPORTED_FALLBACK_USE_CASE_KEYS))
def test_supported_use_cases_do_not_build_fallback_config(use_case_key: str) -> None:
    """Verifie que le builder ne recree pas de config fallback supportee."""

    assert build_fallback_use_case_config(use_case_key) is None
