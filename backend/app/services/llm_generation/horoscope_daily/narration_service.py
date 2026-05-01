"""Déporte la narration horoscope hors de la façade applicative LLM."""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy.orm import Session

from app.domain.llm.prompting.context_compactor import estimate_tokens
from app.domain.llm.prompting.narrator_contract import NarratorAdvice, NarratorResult
from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayResult,
    LLMExecutionRequest,
)
from app.domain.llm.runtime.gateway import LLMGateway

logger = logging.getLogger(__name__)


def map_gateway_result_to_narrator_result(result: GatewayResult) -> NarratorResult | None:
    """Mappe le résultat structuré du gateway vers le contrat narratif historique."""
    if not result.structured_output:
        return None

    data = result.structured_output
    synthesis = _as_string(data.get("daily_synthesis"))
    if not synthesis:
        return None

    advice_data = data.get("daily_advice")
    daily_advice = None
    if isinstance(advice_data, dict):
        advice = _as_string(advice_data.get("advice"))
        emphasis = _as_string(advice_data.get("emphasis"))
        if advice or emphasis:
            daily_advice = NarratorAdvice(advice=advice, emphasis=emphasis)

    tw_raw = data.get("time_window_narratives")
    time_window_narratives: dict[str, str] = {}
    if isinstance(tw_raw, dict):
        allowed_keys = {"nuit", "matin", "apres_midi", "soiree"}
        time_window_narratives = {
            key: _as_string(value)
            for key, value in tw_raw.items()
            if key in allowed_keys and _as_string(value)
        }

    tp_raw = data.get("turning_point_narratives")
    turning_point_narratives = []
    if isinstance(tp_raw, list):
        turning_point_narratives = [text for item in tp_raw if (text := _as_string(item))]

    return NarratorResult(
        daily_synthesis=synthesis,
        astro_events_intro=_as_string(data.get("astro_events_intro")),
        time_window_narratives=time_window_narratives,
        turning_point_narratives=turning_point_narratives,
        daily_advice=daily_advice,
        main_turning_point_narrative=_as_string(data.get("main_turning_point_narrative")) or None,
    )


async def generate_horoscope_narration_via_gateway(
    *,
    variant_code: str | None,
    time_windows: list[dict[str, Any]],
    common_context: Any,
    user_id: int,
    request_id: str,
    trace_id: str,
    db: Session,
    astrologer_profile_key: str = "standard",
    lang: str = "fr",
    day_climate: dict[str, Any] | None = None,
    best_window: dict[str, Any] | None = None,
    turning_point: dict[str, Any] | None = None,
    domain_ranking: list[dict[str, Any]] | None = None,
    astro_daily_events: dict[str, Any] | None = None,
) -> NarratorResult | None:
    """Génère la narration horoscope en réutilisant le pipeline canonique du gateway."""
    from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder

    gateway = LLMGateway()
    feature = "horoscope_daily"
    subfeature = "narration"
    if variant_code == "summary_only":
        plan = "free"
    elif variant_code == "full":
        plan = "premium"
    elif variant_code is None:
        plan = "free"
        logger.info(
            "ai_engine_adapter_legacy_daily_prediction_route_used request_id=%s",
            request_id,
        )
    else:
        raise ValueError(f"Invalid variant_code for daily narration: {variant_code}")

    min_sentences = 7 if plan == "free" else 10
    base_question = AstrologerPromptBuilder().build(
        common_context=common_context,
        time_windows=time_windows,
        astro_daily_events=astro_daily_events,
        astrologer_profile_key=astrologer_profile_key,
        lang=lang,
        day_climate=day_climate,
        best_window=best_window,
        turning_point=turning_point,
        domain_ranking=domain_ranking,
        variant_code=variant_code,
    )

    final_result: NarratorResult | None = None
    for attempt in range(1, 3):
        question = (
            base_question
            if attempt == 1
            else (
                base_question + f"\n\nCORRECTION OBLIGATOIRE : daily_synthesis trop courte. "
                f"Assure-toi d'au moins {min_sentences} phrases complètes."
            )
        )

        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(
                use_case=feature,
                feature=feature,
                subfeature=subfeature,
                plan=plan,
                locale="fr-FR" if lang == "fr" else "en-US",
                question=question,
            ),
            context=ExecutionContext(
                extra_context={
                    "variant_code": variant_code,
                    "astrologer_profile_key": astrologer_profile_key,
                }
            ),
            user_id=user_id,
            request_id=request_id,
            trace_id=trace_id,
        )

        result = await gateway.execute_request(request=request, db=db)
        if result.usage.output_tokens == 0 and result.raw_output:
            result.usage.output_tokens = estimate_tokens(result.raw_output)

        final_result = map_gateway_result_to_narrator_result(result)
        if final_result and _count_sentences(final_result.daily_synthesis) >= min_sentences:
            return final_result

    return final_result


def _count_sentences(text: str) -> int:
    """Compte grossièrement les phrases pour la vérification métier de narration."""
    if not text:
        return 0
    return len([part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()])


def _as_string(value: Any) -> str:
    """Normalise un champ narratif vers une chaîne propre."""
    if isinstance(value, str):
        return value.strip()
    return ""
