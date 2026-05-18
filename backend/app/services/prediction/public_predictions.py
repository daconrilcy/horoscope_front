"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.prediction.persisted_snapshot import PersistedPredictionSnapshot
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
from app.services.llm_generation.horoscope_daily.narration_service import (
    generate_horoscope_narration_via_gateway,
)
from app.services.prediction.types import (
    DailyPredictionServiceError,
)

logger = logging.getLogger(__name__)


def load_public_projection_aspect_profiles_by_id(
    db: Session, reference_version_id: int
) -> dict[str, Any]:
    """Charge les profils d'aspects publics pour la version persistée du snapshot."""
    reference = db.get(ReferenceVersionModel, reference_version_id)
    if reference is None:
        raise ValueError(f"Reference version id '{reference_version_id}' not found")
    return PredictionReferenceRepository(db).get_aspect_profiles(reference_version_id)


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


async def enrich_public_prediction_with_horoscope_narration(
    assembled: dict[str, Any],
    *,
    snapshot: PersistedPredictionSnapshot,
    db: Session,
    prompt_context: Any | None,
    request_id: str,
    trace_id: str,
    variant_code: str | None,
    astrologer_profile_key: str = "standard",
    lang: str | None = None,
) -> dict[str, Any]:
    """Ajoute la narration horoscope via le service canonique sans modifier la projection."""
    if assembled.get("has_llm_narrative") or not settings.llm_narrator_enabled:
        return assembled
    if prompt_context is None:
        return assembled

    narrator_res = await generate_horoscope_narration_via_gateway(
        variant_code=variant_code,
        time_windows=assembled.get("time_windows") or [],
        common_context=prompt_context,
        user_id=snapshot.user_id,
        request_id=request_id,
        trace_id=trace_id,
        db=db,
        astrologer_profile_key=astrologer_profile_key,
        lang=lang,
        day_climate=assembled.get("day_climate"),
        best_window=assembled.get("best_window"),
        turning_point=assembled.get("turning_point"),
        domain_ranking=assembled.get("domain_ranking"),
        astro_daily_events=assembled.get("astro_daily_events"),
    )
    if narrator_res is None:
        return assembled

    assembled["has_llm_narrative"] = True
    assembled["daily_synthesis"] = narrator_res.daily_synthesis
    assembled["astro_events_intro"] = narrator_res.astro_events_intro
    if narrator_res.daily_advice:
        assembled["daily_advice"] = {
            "advice": narrator_res.daily_advice.advice,
            "emphasis": narrator_res.daily_advice.emphasis,
        }

    for window in assembled.get("time_windows") or []:
        if not isinstance(window, dict):
            continue
        period_key = window.get("period_key")
        if period_key in narrator_res.time_window_narratives:
            window["narrative"] = narrator_res.time_window_narratives[period_key]

    for index, turning_point in enumerate(assembled.get("turning_points") or []):
        if not isinstance(turning_point, dict):
            continue
        if index < len(narrator_res.turning_point_narratives):
            turning_point["narrative"] = narrator_res.turning_point_narratives[index]

    main_turning_point = assembled.get("turning_point")
    if isinstance(main_turning_point, dict) and narrator_res.main_turning_point_narrative:
        main_turning_point["narrative"] = narrator_res.main_turning_point_narrative

    return assembled
