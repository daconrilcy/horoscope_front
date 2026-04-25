"""Expose les helpers natals partages via le chemin de prompt canonique."""

from app.services.llm_generation.shared.natal_context import (
    ASPECT_NAMES_FR,
    MAJOR_ASPECTS,
    PLANET_NAMES_FR,
    SIGN_NAMES_FR,
    UNKNOWN_BIRTH_TIME_SENTINEL,
    UNKNOWN_LOCATION_SENTINELS,
    _detect_degraded_mode,
    _format_longitude,
    _longitude_to_sign,
    build_chat_natal_hint,
    build_natal_chart_summary,
)

__all__ = [
    "ASPECT_NAMES_FR",
    "MAJOR_ASPECTS",
    "PLANET_NAMES_FR",
    "SIGN_NAMES_FR",
    "UNKNOWN_BIRTH_TIME_SENTINEL",
    "UNKNOWN_LOCATION_SENTINELS",
    "_detect_degraded_mode",
    "_format_longitude",
    "_longitude_to_sign",
    "build_chat_natal_hint",
    "build_natal_chart_summary",
]
