"""Constantes partagées par plusieurs modules API v1."""

# ruff: noqa: F401

from __future__ import annotations

from app.core.api_constants import (
    ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER,
    ADMIN_MANUAL_EXECUTE_ROUTE_PATH,
    ADMIN_MANUAL_LLM_EXECUTE_SURFACE,
    BLOCKED_CATEGORIES,
    CONSULTATION_TYPE_ALIASES,
    DEFAULT_CONFIG_TEXTS,
    DEFAULT_DRILLDOWN_LIMIT,
    DEFAULT_EDITORIAL_TEMPLATES,
    FEATURES_TO_QUERY,
    LEGACY_USE_CASE_KEYS_REMOVED,
    LOCALE_PATTERN,
    MAX_PAGE_SIZE,
    PDF_TEMPLATE_CONFIG_DOC,
    VALID_RESOLUTION_SOURCES,
    VALID_VIEWS,
)

CHAT_TEMPORARY_UNAVAILABLE_MESSAGE = (
    "Je suis desole, je ne peux pas vous repondre pour l'instant. Revenez un peu plus tard."
)

VALID_ASTROLOGER_PROFILES: frozenset[str] = frozenset(
    {"standard", "vedique", "humaniste", "karmique", "psychologique"}
)
"""Profils d'astrologues acceptés par les routes publiques utilisateur."""

CALIBRATION_RULE_DESCRIPTIONS: dict[str, str] = {
    "turning_point.min_duration_minutes": "Duree minimale retenue pour un turning point.",
    "scores.rare_bonus_factor": "Bonus applique aux signaux juges rares.",
    "scores.flat_day_threshold": "Seuil en dessous duquel la journee est classee comme plate.",
}
