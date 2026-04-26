"""Constantes partagées par plusieurs modules API v1."""

from __future__ import annotations

import re

from app.core.sensitive_data import DataCategory

ADMIN_MANUAL_LLM_EXECUTE_SURFACE = "admin_catalog_manual_execute_sample"
ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER = "X-Admin-Manual-Llm-Execute"
ADMIN_MANUAL_EXECUTE_ROUTE_PATH = "/catalog/{manifest_entry_id}/execute-sample"

VALID_VIEWS: frozenset[str] = frozenset({"user", "subscription", "feature"})
MAX_PAGE_SIZE = 100
DEFAULT_DRILLDOWN_LIMIT = 50

LOCALE_PATTERN = re.compile(r"^[a-z]{2}-[A-Z]{2}$")
BLOCKED_CATEGORIES: frozenset[DataCategory] = frozenset(
    {
        DataCategory.SECRET_CREDENTIAL,
        DataCategory.DIRECT_IDENTIFIER,
        DataCategory.CORRELABLE_BUSINESS_IDENTIFIER,
    }
)

PDF_TEMPLATE_CONFIG_DOC = (
    "Optional runtime config for PDF export. "
    "Supported keys: "
    "'max_paragraph_chars' (int, 200..5000) and "
    "'split_paragraphs_enabled' (bool), "
    "'page_budget_lines' (int, 24..60), "
    "'section_head_extra_lines' (int, 0..6), "
    "'paragraph_spacing_lines' (int, 0..3), "
    "'section_tail_spacing_lines' (int, 0..4), "
    "'sections_start_new_page_min_remaining_lines' (int, 0..30), "
    "'sections_start_new_page' (bool), "
    "'pagination_debug' (bool). "
    "Note: sections_start_new_page is best-effort and is applied only when "
    "remaining lines after intro are below sections_start_new_page_min_remaining_lines. "
    "Warning: when split_paragraphs_enabled=false, long text may be cut across pages more often."
)

CHAT_TEMPORARY_UNAVAILABLE_MESSAGE = (
    "Je suis desole, je ne peux pas vous repondre pour l'instant. Revenez un peu plus tard."
)

VALID_ASTROLOGER_PROFILES: frozenset[str] = frozenset(
    {"standard", "vedique", "humaniste", "karmique", "psychologique"}
)
"""Profils d'astrologues acceptés par les routes publiques utilisateur."""

VALID_RESOLUTION_SOURCES: frozenset[str] = frozenset(
    {
        "canonical_quota",
        "canonical_unlimited",
        "canonical_disabled",
        "settings_fallback",
    }
)

DEFAULT_CONFIG_TEXTS: tuple[dict[str, str], ...] = (
    {
        "key": "paywall.daily.locked_section",
        "value": "Passez premium pour debloquer l'analyse complete de la journee.",
        "category": "paywall",
    },
    {
        "key": "paywall.natal.upgrade_cta",
        "value": "Activez le theme complet et comparez plusieurs astrologues.",
        "category": "paywall",
    },
    {
        "key": "transactional.billing.success",
        "value": "Votre abonnement a bien ete mis a jour.",
        "category": "transactional",
    },
    {
        "key": "marketing.in_app.welcome",
        "value": "Explorez vos tendances du moment avec un guidage plus precis.",
        "category": "marketing",
    },
)

DEFAULT_EDITORIAL_TEMPLATES: tuple[dict[str, object], ...] = (
    {
        "template_code": "daily_overview",
        "title": "Daily overview",
        "content": "<intro>\n<momentum>\n<advice>",
        "expected_tags": ["intro", "momentum", "advice"],
        "example_render": "Intro concise puis momentum et un conseil actionnable.",
    },
    {
        "template_code": "natal_unlock",
        "title": "Natal unlock",
        "content": "<context>\n<insights>\n<next_step>",
        "expected_tags": ["context", "insights", "next_step"],
        "example_render": "Contexte natal suivi de deux insights et d'une recommandation.",
    },
)

CALIBRATION_RULE_DESCRIPTIONS: dict[str, str] = {
    "turning_point.min_duration_minutes": "Duree minimale retenue pour un turning point.",
    "scores.rare_bonus_factor": "Bonus applique aux signaux juges rares.",
    "scores.flat_day_threshold": "Seuil en dessous duquel la journee est classee comme plate.",
}

FEATURES_TO_QUERY: tuple[str, ...] = (
    "astrologer_chat",
    "thematic_consultation",
    "natal_chart_long",
    "natal_chart_short",
    "horoscope_daily",
)

CONSULTATION_TYPE_ALIASES: dict[str, str] = {
    "work": "career",
    "relation": "relationship",
}

LEGACY_USE_CASE_KEYS_REMOVED: frozenset[str] = frozenset(
    {
        "daily_prediction",
        "horoscope_daily_free",
        "horoscope_daily_full",
        "chat",
        "chat_astrologer",
    }
)
