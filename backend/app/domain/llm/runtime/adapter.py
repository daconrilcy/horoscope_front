"""Expose une facade minimale entre les services metier et le gateway LLM canonique."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.domain.llm.prompting.chat_opening import build_opening_chat_user_data_block
from app.domain.llm.prompting.context_compactor import estimate_tokens
from app.domain.llm.runtime.adapter_errors import (
    AIEngineAdapterError,
    handle_gateway_error,
)
from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionMessage,
    ExecutionUserInput,
    LLMExecutionRequest,
    NatalExecutionInput,
)
from app.domain.llm.runtime.errors import AIEngineError
from app.domain.llm.runtime.gateway import LLMGateway
from app.prediction.llm_narrator import NarratorResult
from app.services.llm_generation.horoscope_daily.narration_service import (
    generate_horoscope_narration_via_gateway,
)

logger = logging.getLogger(__name__)

__all__ = ["AIEngineAdapter", "AIEngineAdapterError"]


def _build_guidance_request(
    use_case: str,
    context: dict[str, str | None],
    locale: str,
    user_id: int,
    request_id: str,
    trace_id: str,
) -> LLMExecutionRequest:
    """Construit la requete canonique de guidance a partir du contexte metier."""
    normalized_context = dict(context)
    situation = (normalized_context.get("situation") or "").strip()
    objective = (normalized_context.get("objective") or "").strip()
    time_horizon = (normalized_context.get("time_horizon") or "").strip()

    if use_case == "guidance_daily" and not situation:
        situation = "Lecture astrologique quotidienne basee sur le profil natal du jour."
    elif use_case == "guidance_weekly" and not situation:
        situation = "Lecture astrologique hebdomadaire basee sur le profil natal de la semaine."

    if use_case == "guidance_contextual":
        if objective and time_horizon:
            question = f"{objective} Horizon: {time_horizon}."
        elif objective:
            question = objective
        else:
            question = situation or "Proposer une guidance contextuelle prudente."
    elif use_case == "guidance_weekly":
        question = "Quelle guidance astrologique ressort pour cette semaine ?"
    else:
        question = "Quelle guidance astrologique ressort pour aujourd hui ?"

    user_input = ExecutionUserInput(
        use_case=use_case,
        locale=locale,
        question=question,
        situation=situation if situation else None,
    )
    extra_context = {
        "objective": objective,
        "time_horizon": time_horizon,
        "context_lines": normalized_context.get("context_lines"),
    }
    extra_context = {key: value for key, value in extra_context.items() if value is not None}
    exec_context = ExecutionContext(
        natal_data=normalized_context.get("natal_data"),
        chart_json=normalized_context.get("chart_json"),
        astro_context=normalized_context.get("astro_context"),
        extra_context=extra_context,
    )
    return LLMExecutionRequest(
        user_input=user_input,
        context=exec_context,
        user_id=user_id,
        request_id=request_id,
        trace_id=trace_id,
    )


class AIEngineAdapter:
    """Facade stable qui adapte des cas d'usage metier vers `LLMGateway`."""

    @staticmethod
    async def generate_chat_reply(
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str = "fr-FR",
        db: Session | None = None,
        entitlement_result: Any = None,
    ) -> Any:
        """Construit une requete de chat canonique puis delegue l'execution au gateway."""
        logger.info(
            "chat_reply_path request_id=%s history_count=%d has_natal=%s conversation_id=%s",
            request_id,
            len(messages),
            bool(context.get("natal_chart_summary")),
            context.get("conversation_id", "none"),
        )
        gateway = LLMGateway()

        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        plan = "free"
        if entitlement_result and hasattr(entitlement_result, "plan_code"):
            plan = entitlement_result.plan_code

        user_input = ExecutionUserInput(
            use_case="chat_astrologer",
            feature="chat",
            subfeature="astrologer",
            plan=plan,
            locale=locale,
            message=last_user_msg,
            conversation_id=str(context.get("conversation_id"))
            if context.get("conversation_id")
            else None,
        )
        history = [ExecutionMessage(role=m["role"], content=m["content"]) for m in messages[:-1]]
        extra_context = {**context}
        for key in ["conversation_id", "history", "chat_turn_stage"]:
            extra_context.pop(key, None)
        if context.get("chat_turn_stage") == "opening":
            extra_context["user_data_block"] = build_opening_chat_user_data_block(
                last_user_msg=last_user_msg,
                context=context,
            )
            extra_context["chat_turn_stage"] = "opening"

        request = LLMExecutionRequest(
            user_input=user_input,
            context=ExecutionContext(
                history=history,
                natal_data=context.get("natal_data"),
                chart_json=context.get("chart_json"),
                astro_context=context.get("astro_context"),
                extra_context=extra_context,
            ),
            user_id=user_id,
            request_id=request_id,
            trace_id=trace_id,
        )

        try:
            result = await gateway.execute_request(request=request, db=db)
        except Exception as err:
            from app.domain.llm.runtime.contracts import GatewayError

            if isinstance(err, (AIEngineError, GatewayError)):
                handle_gateway_error(err, request_id, "chat")
            logger.error(
                "ai_engine_adapter_v2_unexpected_error request_id=%s error=%s",
                request_id,
                str(err),
            )
            raise ConnectionError("llm provider unavailable (v2)") from err

        if result.usage.output_tokens == 0 and result.raw_output:
            result.usage.output_tokens = estimate_tokens(result.raw_output)
            logger.warning(
                "chat_reply_token_fallback request_id=%s estimated_output=%d",
                request_id,
                result.usage.output_tokens,
            )
        return result

    @staticmethod
    async def generate_guidance(
        use_case: str,
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str = "fr-FR",
        db: Session | None = None,
        plan: str = "free",
    ) -> Any:
        """Construit une requete de guidance canonique puis delegue au gateway."""
        gateway = LLMGateway()
        request = _build_guidance_request(
            use_case=use_case,
            context=context,
            locale=locale,
            user_id=user_id,
            request_id=request_id,
            trace_id=trace_id,
        )
        request.user_input.feature = "guidance"
        if use_case.startswith("guidance_"):
            request.user_input.subfeature = use_case.replace("guidance_", "")
        elif use_case == "event_guidance":
            request.user_input.subfeature = "event"
        else:
            request.user_input.subfeature = use_case
        request.user_input.plan = plan

        try:
            return await gateway.execute_request(request=request, db=db)
        except Exception as err:
            from app.domain.llm.runtime.contracts import GatewayError

            if isinstance(err, (AIEngineError, GatewayError)):
                handle_gateway_error(err, request_id, use_case)
            logger.error(
                "ai_engine_adapter_v2_unexpected_error use_case=%s request_id=%s error=%s",
                use_case,
                request_id,
                str(err),
            )
            raise ConnectionError("llm provider unavailable (v2)") from err

    @staticmethod
    async def generate_natal_interpretation(
        natal_input: NatalExecutionInput,
        db: Session | None = None,
    ) -> Any:
        """Construit la requete de theme natal canonique puis la soumet au gateway."""
        gateway = LLMGateway()
        subfeature = natal_input.use_case_key
        if subfeature in {
            "natal_interpretation",
            "natal_interpretation_short",
            "natal_long_free",
            "natal-long-free",
        }:
            subfeature = "interpretation"

        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(
                use_case=natal_input.use_case_key,
                feature="natal",
                subfeature=subfeature,
                plan=natal_input.plan,
                locale=natal_input.locale,
                question=natal_input.question,
                persona_id_override=natal_input.persona_id,
            ),
            context=ExecutionContext(
                natal_data=natal_input.natal_data,
                chart_json=natal_input.chart_json,
                astro_context=natal_input.astro_context,
                extra_context={
                    "module": natal_input.module,
                    "variant_code": natal_input.variant_code,
                    "level": natal_input.level,
                },
            ),
            flags=ExecutionFlags(
                validation_strict=natal_input.validation_strict,
                evidence_catalog=natal_input.evidence_catalog,
            ),
            user_id=natal_input.user_id,
            request_id=natal_input.request_id,
            trace_id=natal_input.trace_id,
        )

        try:
            return await gateway.execute_request(request=request, db=db)
        except Exception as err:
            from app.domain.llm.runtime.contracts import GatewayError

            if isinstance(err, (AIEngineError, GatewayError)):
                handle_gateway_error(err, natal_input.request_id, natal_input.use_case_key)
            logger.error(
                "ai_engine_adapter_natal_unexpected_error use_case=%s request_id=%s error=%s",
                natal_input.use_case_key,
                natal_input.request_id,
                str(err),
            )
            raise ConnectionError("llm provider unavailable (natal)") from err

    @staticmethod
    async def generate_horoscope_narration(
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
        """Delegue la narration horoscope a la couche `prediction` dediee."""
        try:
            return await generate_horoscope_narration_via_gateway(
                variant_code=variant_code,
                time_windows=time_windows,
                common_context=common_context,
                user_id=user_id,
                request_id=request_id,
                trace_id=trace_id,
                db=db,
                astrologer_profile_key=astrologer_profile_key,
                lang=lang,
                day_climate=day_climate,
                best_window=best_window,
                turning_point=turning_point,
                domain_ranking=domain_ranking,
                astro_daily_events=astro_daily_events,
            )
        except Exception as err:
            from app.domain.llm.runtime.contracts import GatewayError

            if isinstance(err, (AIEngineError, GatewayError)):
                handle_gateway_error(err, request_id, "horoscope_daily")
            logger.error(
                "ai_engine_adapter_narration_failed request_id=%s error=%s",
                request_id,
                str(err),
            )
            raise
