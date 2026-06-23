"""Constantes de contrat partagées par l'API et les services applicatifs."""

from __future__ import annotations

import re

from app.core.sensitive_data import DataCategory

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

FEATURES_TO_QUERY: tuple[str, ...] = ("horoscope_daily",)

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
