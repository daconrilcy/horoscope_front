"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.llm.llm_observability import LlmCallLogModel

logger = logging.getLogger(__name__)
_AI_METRIC_CATEGORY_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "key": "natal_theme_short_free",
        "display_name": "Theme natal short free",
        "targets": ({"feature": "natal", "subfeature": "interpretation", "plan": "free"},),
    },
    {
        "key": "natal_theme_short_paid",
        "display_name": "Theme natal short basic/premium",
        "targets": (
            {"feature": "natal", "subfeature": "short", "plan": "basic"},
            {"feature": "natal", "subfeature": "short", "plan": "premium"},
        ),
    },
    {
        "key": "natal_theme_complete_paid",
        "display_name": "Theme natal complete basic/premium",
        "targets": (
            {"feature": "natal", "subfeature": "interpretation", "plan": "basic"},
            {"feature": "natal", "subfeature": "interpretation", "plan": "premium"},
        ),
    },
    {
        "key": "thematic_consultations",
        "display_name": "Consultations thematiques",
        "targets": (
            {"feature": "guidance", "subfeature": "event"},
            {"feature": "natal", "subfeature": "psy_profile"},
            {"feature": "natal", "subfeature": "shadow_integration"},
            {"feature": "natal", "subfeature": "leadership_workstyle"},
            {"feature": "natal", "subfeature": "creativity_joy"},
            {"feature": "natal", "subfeature": "relationship_style"},
            {"feature": "natal", "subfeature": "community_networks"},
            {"feature": "natal", "subfeature": "values_security"},
            {"feature": "natal", "subfeature": "evolution_path"},
        ),
    },
    {
        "key": "astrologer_chat",
        "display_name": "Chat astrologue",
        "targets": ({"feature": "chat", "subfeature": "astrologer"},),
    },
    {
        "key": "daily_horoscope",
        "display_name": "Horoscope du jour",
        "targets": ({"feature": "horoscope_daily", "subfeature": "narration"},),
    },
    {
        "key": "weekly_horoscope",
        "display_name": "Horoscope hebdomadaire",
        "targets": ({"feature": "guidance", "subfeature": "weekly"},),
    },
)
_AI_METRIC_CATEGORY_BY_KEY = {item["key"]: item for item in _AI_METRIC_CATEGORY_DEFINITIONS}
_REMOVED_LEGACY_USE_CASES = frozenset(
    {"daily_prediction", "horoscope_daily_free", "horoscope_daily_full", "chat", "chat_astrologer"}
)


def _build_target_filters(category: dict[str, Any]) -> list[Any]:
    target_filters: list[Any] = []
    for target in category.get("targets", ()):
        cond = [LlmCallLogModel.feature == target["feature"]]
        if target.get("subfeature") is not None:
            cond.append(LlmCallLogModel.subfeature == target["subfeature"])
        if target.get("plan") is not None:
            cond.append(LlmCallLogModel.plan == target["plan"])
        target_filters.append(and_(*cond))
    return target_filters


def _legacy_removed_filter() -> Any:
    return and_(
        LlmCallLogModel.feature.is_(None),
        LlmCallLogModel.use_case.in_(tuple(_REMOVED_LEGACY_USE_CASES)),
    )


def _matches_target(log: LlmCallLogModel, target: dict[str, str | None]) -> bool:
    if log.feature != target.get("feature"):
        return False
    target_subfeature = target.get("subfeature")
    if target_subfeature is not None and log.subfeature != target_subfeature:
        return False
    target_plan = target.get("plan")
    if target_plan is not None and log.plan != target_plan:
        return False
    return True


def _resolve_metric_category(log: LlmCallLogModel) -> dict[str, Any]:
    # Legacy keys are no longer nominal axes: isolate them in a dedicated bucket.
    if not log.feature and log.use_case in _REMOVED_LEGACY_USE_CASES:
        return {
            "key": "legacy_removed",
            "display_name": "Legacy removed (blocked)",
            "targets": tuple(),
            "classification": "legacy_removed",
        }

    for category in _AI_METRIC_CATEGORY_DEFINITIONS:
        for target in category.get("targets", ()):
            if _matches_target(log, target):
                return category

    return {
        "key": log.feature or "unknown_feature",
        "display_name": log.feature or "unknown_feature",
        "targets": tuple(),
        "classification": "derived_feature",
    }


def _derive_failed_call_error_code(log: LlmCallLogModel) -> str:
    if log.fallback_triggered:
        return "FALLBACK_TRIGGERED"
    if log.repair_attempted:
        return "REPAIR_FAILED"
    if log.evidence_warnings_count > 0:
        return "VALIDATION_ERROR"
    return "LLM_CALL_ERROR"


def _resolve_start_date(period: str) -> datetime:
    if period == "7d":
        return datetime_provider.utcnow() - timedelta(days=7)
    return datetime_provider.utcnow() - timedelta(days=30)


def _empty_metric_row(category: dict[str, Any]) -> dict[str, Any]:
    return {
        "use_case": category["key"],
        "display_name": category["display_name"],
        "call_count": 0,
        "total_tokens": 0,
        "estimated_cost_usd": 0.0,
        "avg_latency_ms": 0,
        "error_rate": 0.0,
        "retry_rate": 0.0,
    }


def _resolve_metric_category_or_raw(use_case: str) -> tuple[dict[str, Any], tuple[str, ...]]:
    category = _AI_METRIC_CATEGORY_BY_KEY.get(use_case)
    if category is not None:
        return category, tuple()
    if use_case == "legacy_removed":
        return (
            {
                "key": "legacy_removed",
                "display_name": "Legacy removed (blocked)",
                "targets": tuple(),
                "classification": "legacy_removed",
            },
            tuple(_REMOVED_LEGACY_USE_CASES),
        )
    fallback_category = {
        "key": use_case,
        "display_name": use_case,
        "targets": ({"feature": use_case},),
    }
    return fallback_category, (use_case,)
