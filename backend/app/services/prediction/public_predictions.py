"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from app.services.prediction.types import (
    DailyPredictionServiceError,
)

logger = logging.getLogger(__name__)


def _resolve_daily_prediction_service_error(
    error: DailyPredictionServiceError,
    *,
    not_found_codes: set[str] | None = None,
) -> dict[str, str]:
    """Convertit une erreur de prédiction en détail applicatif stable."""
    if error.code in ("compute_failed", "timeout"):
        return {
            "code": error.code,
            "message": (
                "Service temporairement indisponible. Veuillez réessayer dans quelques minutes."
            ),
        }

    return {"code": error.code, "message": error.message}


def _extract_llm_narrative_payload(assembled: dict[str, Any]) -> dict[str, Any] | None:
    if not assembled.get("has_llm_narrative"):
        return None

    payload: dict[str, Any] = {}
    daily_synthesis = assembled.get("daily_synthesis")
    if isinstance(daily_synthesis, str) and daily_synthesis.strip():
        payload["daily_synthesis"] = daily_synthesis.strip()

    astro_events_intro = assembled.get("astro_events_intro")
    if isinstance(astro_events_intro, str) and astro_events_intro.strip():
        payload["astro_events_intro"] = astro_events_intro.strip()

    time_window_narratives = {}
    for window in assembled.get("time_windows") or []:
        if not isinstance(window, dict):
            continue
        period_key = window.get("period_key")
        narrative = window.get("narrative")
        if isinstance(period_key, str) and isinstance(narrative, str) and narrative.strip():
            time_window_narratives[period_key] = narrative.strip()
    if time_window_narratives:
        payload["time_window_narratives"] = time_window_narratives

    turning_point_narratives = []
    for turning_point in assembled.get("turning_points") or []:
        if not isinstance(turning_point, dict):
            continue
        narrative = turning_point.get("narrative")
        if isinstance(narrative, str) and narrative.strip():
            turning_point_narratives.append(narrative.strip())
    if turning_point_narratives:
        payload["turning_point_narratives"] = turning_point_narratives

    main_turning_point = assembled.get("turning_point")
    if isinstance(main_turning_point, dict):
        narrative = main_turning_point.get("narrative")
        if isinstance(narrative, str) and narrative.strip():
            payload["main_turning_point_narrative"] = narrative.strip()

    daily_advice = assembled.get("daily_advice")
    if isinstance(daily_advice, dict):
        advice = daily_advice.get("advice")
        emphasis = daily_advice.get("emphasis")
        if (isinstance(advice, str) and advice.strip()) or (
            isinstance(emphasis, str) and emphasis.strip()
        ):
            payload["daily_advice"] = {
                "advice": advice.strip() if isinstance(advice, str) else "",
                "emphasis": emphasis.strip() if isinstance(emphasis, str) else "",
            }

    return payload or None
