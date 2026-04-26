"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/admin/pdf-templates", tags=["admin-pdf-templates"])
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
from app.api.v1.schemas.routers.admin.pdf_templates import *


def _normalize_pdf_template_config(config: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(config)

    int_specs = {
        "max_paragraph_chars": (200, 5000),
        "page_budget_lines": (24, 60),
        "section_head_extra_lines": (0, 6),
        "paragraph_spacing_lines": (0, 3),
        "section_tail_spacing_lines": (0, 4),
        "sections_start_new_page_min_remaining_lines": (0, 30),
    }
    for key_name, (min_value, max_value) in int_specs.items():
        if key_name not in normalized:
            continue
        raw_value = normalized[key_name]
        try:
            parsed_value = int(raw_value)
        except (TypeError, ValueError):
            raise ValueError(f"config_json.{key_name} must be an integer")
        if parsed_value < min_value:
            parsed_value = min_value
        if parsed_value > max_value:
            parsed_value = max_value
        normalized[key_name] = parsed_value

    bool_keys = {
        "split_paragraphs_enabled",
        "sections_start_new_page",
        "pagination_debug",
    }
    for key in bool_keys:
        if key not in normalized:
            continue
        raw = normalized[key]
        if isinstance(raw, bool):
            continue
        if isinstance(raw, str):
            lowered = raw.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                normalized[key] = True
                continue
            if lowered in {"0", "false", "no", "off"}:
                normalized[key] = False
                continue
        if isinstance(raw, (int, float)) and raw in {0, 1}:
            normalized[key] = bool(raw)
            continue
        raise ValueError(
            f"config_json.{key} must be a boolean (accepted: true/false, 1/0, yes/no, on/off)"
        )

    return normalized
