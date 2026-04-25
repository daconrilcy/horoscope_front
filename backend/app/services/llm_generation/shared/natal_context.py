"""Factorise la construction du contexte natal reutilise par guidance et consultation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.services.llm_generation.natal.prompt_context import build_natal_chart_summary
from app.services.user_natal_chart_service import UserNatalChartService, UserNatalChartServiceError

if TYPE_CHECKING:
    from app.domain.astrology.natal_calculation import NatalResult

logger = logging.getLogger(__name__)


def detect_degraded_natal_mode(
    *,
    birth_time: str | None,
    birth_place: str | None,
) -> str | None:
    """Retourne le mode degrade applicable quand l heure ou le lieu manquent."""
    no_time = birth_time is None or birth_time.strip() == ""
    no_location = birth_place is None or birth_place.strip() == ""
    if no_time and no_location:
        return "no_location_no_time"
    if no_time:
        return "no_time"
    if no_location:
        return "no_location"
    return None


def build_natal_chart_summary_with_defaults(
    *,
    natal_result: "NatalResult",
    birth_date: str,
    birth_time: str | None,
    birth_place: str | None,
) -> str:
    """Construit un resume natal robuste meme avec des donnees partielles."""
    return build_natal_chart_summary(
        natal_result=natal_result,
        birth_place=birth_place or "Non connu",
        birth_date=birth_date,
        birth_time=birth_time or "00:00",
        degraded_mode=detect_degraded_natal_mode(
            birth_time=birth_time,
            birth_place=birth_place,
        ),
    )


def build_user_natal_chart_summary_context(
    db: Session,
    *,
    user_id: int,
    birth_date: str,
    birth_time: str | None,
    birth_place: str | None,
    warning_event: str = "llm_natal_chart_context_unavailable",
) -> str | None:
    """Charge le theme natal persiste et retourne le resume LLM partage."""
    try:
        natal_chart = UserNatalChartService.get_latest_for_user(db, user_id=user_id)
    except UserNatalChartServiceError as error:
        if error.code == "natal_chart_not_found":
            return None
        logger.warning(
            "%s user_id=%s code=%s",
            warning_event,
            user_id,
            error.code,
        )
        return None

    return build_natal_chart_summary_with_defaults(
        natal_result=natal_chart.result,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
    )
