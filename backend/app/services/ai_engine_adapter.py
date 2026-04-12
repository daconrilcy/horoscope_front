# CANONICAL LLM APPLICATION LAYER (nom legacy conservé post-epic-66 — renommage prévu)
# Rôle : construire LLMExecutionRequest, appeler gateway.execute_request(), mapper les erreurs.
# Renommage futur : LLMApplicationLayer ou équivalent — story dédiée à créer.

"""
CANONICAL LLM APPLICATION LAYER

Ce module constitue le point d'entrée unique pour les services métier (Chat, Guidance,
et prochainement Natal) souhaitant exécuter un appel LLM orchestré.

RESPONSABILITÉS :
1. Construire le contrat canonique LLMExecutionRequest à partir des entrées métier.
2. Appeler le LLMGateway via sa méthode execute_request().
3. Mapper les exceptions de plateforme (GatewayError, UpstreamError) en exceptions
   applicatives (AIEngineAdapterError) avec les codes HTTP appropriés.

NON-RÔLES :
- Ce module ne contient aucune logique d'orchestration (résolution de config, prompts).
- Ce module ne contient aucune logique de validation de schéma de sortie LLM.
- Ce module n'interagit pas directement avec les providers (OpenAI, etc.).

PATTERN POUR NOUVEAU USE CASE :
Créer une méthode generate_xxx() qui :
- Prend en entrée des types métier forts (modèles Pydantic ou types natifs clairs).
- Construit une LLMExecutionRequest.
- Appelle self.gateway.execute_request(request, db).
- Gère le mapping d'erreurs via _handle_gateway_error.
"""

from __future__ import annotations

__all__ = [
    "AIEngineAdapter",
    "AIEngineAdapterError",
    "assess_off_scope",
    "map_adapter_error_to_codes",
    "set_test_chat_generator",
    "set_test_guidance_generator",
    "reset_test_generators",
    "get_test_generators_state",
]

import logging
import re
from typing import Any, Awaitable, Callable, NoReturn, Optional

from sqlalchemy.orm import Session

from app.ai_engine.exceptions import (
    AIEngineError,
    ContextTooLargeError,
    ProviderNotConfiguredError,
    RateLimitExceededError,
    RetryBudgetExhaustedError,
    UpstreamAuthError,
    UpstreamBadRequestError,
    UpstreamCircuitOpenError,
    UpstreamConnectionError,
    UpstreamRateLimitError,
    UpstreamServerError,
    UpstreamTimeoutError,
)
from app.ai_engine.exceptions import (
    ValidationError as AIEngineValidationError,
)
from app.core.config import settings
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionMessage,
    ExecutionUserInput,
    GatewayResult,
    LLMExecutionRequest,
    NatalExecutionInput,
)
from app.prediction.llm_narrator import NarratorAdvice, NarratorResult

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "AUTO"
DEFAULT_PROVIDER = "openai"


def _looks_like_unclear_opening_message(message: str) -> bool:
    normalized = "".join(ch for ch in message.strip().lower() if ch.isalpha())
    if not normalized:
        return True
    if len(normalized) <= 4:
        return True
    if len(set(normalized)) <= 2 and len(normalized) <= 6:
        return True
    vowels = sum(1 for ch in normalized if ch in "aeiouyàâäéèêëîïôöùûü")
    if len(normalized) <= 6 and vowels == 0:
        return True
    return False


def _build_guidance_request(
    use_case: str,
    context: dict[str, str | None],
    locale: str,
    user_id: int,
    request_id: str,
    trace_id: str,
) -> LLMExecutionRequest:
    """
    Builds a canonical LLMExecutionRequest for guidance use cases.
    (Story 66.3 AC4)
    """
    normalized_context = dict(context)

    situation = (normalized_context.get("situation") or "").strip()
    objective = (normalized_context.get("objective") or "").strip()
    time_horizon = (normalized_context.get("time_horizon") or "").strip()

    # 1. Situation default logic (Legacy preservation)
    if use_case == "guidance_daily" and not situation:
        situation = "Lecture astrologique quotidienne basee sur le profil natal du jour."
    elif use_case == "guidance_weekly" and not situation:
        situation = "Lecture astrologique hebdomadaire basee sur le profil natal de la semaine."

    # 2. Question logic (Legacy preservation)
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

    # 3. ExecutionUserInput
    user_input = ExecutionUserInput(
        use_case=use_case,
        locale=locale,
        question=question,
        situation=situation if situation else None,
    )

    # 4. ExecutionContext
    # Story 66.3 AC4: time_horizon and objective in extra_context
    extra_context = {
        "objective": objective,
        "time_horizon": time_horizon,
        "context_lines": normalized_context.get("context_lines"),
    }
    # Clean None values from extra_context
    extra_context = {k: v for k, v in extra_context.items() if v is not None}

    # Add other context fields
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


def _is_non_production_env() -> bool:
    return settings.app_env not in {"production", "prod"}


def _build_test_chat_fallback(messages: list[dict[str, str]]) -> str:
    user_lines = [msg["content"].strip() for msg in messages if msg.get("role") == "user"]
    joined = " | ".join(line for line in user_lines if line)
    if joined:
        return f"Reponse test hors provider: {joined}"
    return "Reponse test hors provider."


def _build_test_guidance_fallback(use_case: str) -> str:
    return f"Guidance test hors provider pour {use_case}."


def build_opening_chat_user_data_block(
    last_user_msg: str,
    context: dict[str, str | None],
) -> str:
    persona_name = context.get("persona_name") or "Astrologue"
    persona_tone = context.get("persona_tone") or "direct"
    persona_style = context.get("persona_style_markers") or "non précisé"
    today_date = context.get("today_date") or "aujourd'hui"
    user_profile = context.get("user_profile_brief") or "Profil utilisateur non disponible"
    unclear_opening = _looks_like_unclear_opening_message(last_user_msg)

    return (
        f"Premier message utilisateur : {last_user_msg}\n\n"
        "Contexte initial minimal pour ce premier échange seulement:\n"
        f"- Astrologue: {persona_name}\n"
        f"- Ton astrologue: {persona_tone}\n"
        f"- Style astrologue: {persona_style}\n"
        f"- Date du jour: {today_date}\n"
        f"- Profil simple utilisateur: {user_profile}\n\n"
        "Consigne de réponse pour ce premier échange:\n"
        "- Réponds d'abord naturellement à la demande immédiate de l'utilisateur.\n"
        "- N'ouvre pas spontanément une lecture complète du thème natal "
        "ni de l'horoscope du jour.\n"
        "- Si ces éléments peuvent aider, propose ensuite simplement de regarder le thème natal, "
        "l'horoscope du jour ou les transits du moment, selon la demande.\n"
        + (
            "- Le premier message semble vague ou incompréhensible. "
            "Ne réponds pas avec une formule robotique ni une liste d'options. "
            "Dis simplement que tu n'as pas bien saisi et invite l'utilisateur "
            "à reformuler naturellement en une phrase.\n"
            if unclear_opening
            else "- Évite les salutations automatiques du type "
            '"Bonjour, comment puis-je vous aider ?" si elles n\'apportent rien.\n'
        )
        + "- Reste conversationnel, bref et humain."
    )


def _can_use_test_fallback(err: Exception) -> bool:
    if not _is_non_production_env():
        return False
    from app.llm_orchestration.models import GatewayError

    if isinstance(err, ProviderNotConfiguredError):
        return True

    # Search in message, details and causes
    texts = [str(err).lower()]
    if isinstance(err, GatewayError) and err.details:
        texts.append(str(err.details).lower())

    curr = err
    while curr.__cause__ or curr.__context__:
        curr = curr.__cause__ or curr.__context__
        texts.append(str(curr).lower())
        if hasattr(curr, "details") and getattr(curr, "details"):
            texts.append(str(getattr(curr, "details")).lower())

    markers = [
        "not configured",
        "api key",
        "auth",
        "invalid_api_key",
        "incorrect api key",
        "missing required variables",
        "missing mandatory platform variable",
        "mandatory assembly missing",
    ]
    for t in texts:
        if any(m in t for m in markers):
            return True
    return False


def _handle_ai_engine_error(
    err: Exception,
    request_id: str,
    error_code_prefix: str,
) -> NoReturn:
    """
    Handle AI Engine errors and convert them to appropriate exceptions.

    Args:
        err: The original exception from AI Engine.
        request_id: Request identifier for logging.
        error_code_prefix: Prefix for error codes (e.g., "chat" or "guidance").

    Raises:
        AIEngineAdapterError: For rate limit, context size, or validation errors.
        ConnectionError: For upstream/generic AI engine errors.
    """
    if isinstance(err, RateLimitExceededError):
        raise AIEngineAdapterError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            status_code=429,
            details={"retry_after_ms": str(err.retry_after_ms or 60000)},
        ) from err
    if isinstance(err, ContextTooLargeError):
        raise AIEngineAdapterError(
            code="context_too_large",
            message="context exceeds maximum tokens",
            status_code=400,
            details=err.details,
        ) from err
    if isinstance(err, AIEngineValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{error_code_prefix}_input",
            message=err.message,
            status_code=400,
            details=err.details,
        ) from err
    logger.error(
        "ai_engine_adapter_error request_id=%s error=%s",
        request_id,
        str(err),
    )
    raise ConnectionError("llm provider unavailable") from err


def _handle_gateway_error(
    err: Exception,
    request_id: str,
    use_case: str,
) -> NoReturn:
    """Handle LLM Gateway errors and map them to adapter exceptions."""
    from app.llm_orchestration.models import (
        GatewayConfigError,
        GatewayError,
        InputValidationError,
        OutputValidationError,
        PromptRenderError,
        UnknownUseCaseError,
    )

    # 1. Handle explicit Upstream Taxonomy (Finding High)
    if isinstance(err, UpstreamRateLimitError):
        raise AIEngineAdapterError(
            code="rate_limit_exceeded",
            message=err.message,
            status_code=429,
            details={"retry_after_ms": str(err.retry_after_ms or 60000), **err.details},
        ) from err

    if isinstance(err, UpstreamTimeoutError):
        raise AIEngineAdapterError(
            code="upstream_timeout",
            message="llm provider timeout",
            status_code=504,
            details=err.details,
        ) from err

    if isinstance(err, UpstreamConnectionError):
        raise AIEngineAdapterError(
            code="upstream_connection_error",
            message="llm provider connection failed",
            status_code=502,
            details=err.details,
        ) from err

    if isinstance(err, UpstreamCircuitOpenError):
        raise AIEngineAdapterError(
            code="upstream_circuit_open",
            message=err.message,
            status_code=503,
            details=err.details,
        ) from err

    if isinstance(err, RetryBudgetExhaustedError):
        raise AIEngineAdapterError(
            code="retry_budget_exhausted",
            message=err.message,
            status_code=502,
            details=err.details,
        ) from err

    if isinstance(err, (UpstreamAuthError, UpstreamBadRequestError, UpstreamServerError)):
        status = 502
        if isinstance(err, UpstreamBadRequestError):
            status = 400
        raise AIEngineAdapterError(
            code="upstream_error",
            message=f"llm provider error: {err.error_type}",
            status_code=status,
            details=err.details,
        ) from err

    # 2. Handle Gateway-level logical errors
    if isinstance(err, PromptRenderError):
        raise AIEngineAdapterError(
            code="prompt_render_error",
            message=f"failed to render prompt for {use_case}",
            status_code=400,
            details=err.details,
        ) from err
    if isinstance(err, UnknownUseCaseError):
        raise AIEngineAdapterError(
            code="unknown_use_case",
            message=f"use case {use_case} is not configured",
            status_code=400,
            details=err.details,
        ) from err
    if isinstance(err, GatewayConfigError):
        code = "gateway_config_error"
        if err.error_code:
            code = err.error_code
        raise AIEngineAdapterError(
            code=code,
            message=str(err),
            status_code=500,
            details=err.details,
        ) from err
    if isinstance(err, InputValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{use_case}_input",
            message="Input validation failed",
            status_code=400,
            details=err.details,
        ) from err
    if isinstance(err, OutputValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{use_case}_output",
            message="Output validation failed",
            status_code=422,
            details=err.details,
        ) from err

    # 3. Legacy mapping for provider-originated GatewayError kinds
    if isinstance(err, GatewayError):
        kind = err.details.get("kind")
        if kind == "timeout":
            raise AIEngineAdapterError(
                code="upstream_timeout",
                message="llm provider timeout",
                status_code=504,
            ) from err
        if kind == "rate_limit":
            raise AIEngineAdapterError(
                code="rate_limit_exceeded",
                message="rate limit exceeded",
                status_code=429,
                details={"retry_after_ms": "60000"},
            ) from err

    logger.error(
        "ai_engine_adapter_gateway_error use_case=%s request_id=%s error=%s",
        use_case,
        request_id,
        str(err),
    )
    raise ConnectionError(f"llm provider unavailable (v2: {use_case})") from err


def assess_off_scope(content: str) -> tuple[bool, float, str | None]:
    """
    Assess if a response is off-scope with a confidence score.

    Args:
        content: The response content to evaluate.

    Returns:
        Tuple of (is_off_scope, confidence_score, reason).
        - is_off_scope: True if the response appears off-scope.
        - confidence_score: 0.0 to 1.0, higher means more confident it's off-scope.
        - reason: Short string explaining why it was flagged, or None if not off-scope.
    """
    normalized = content.strip().lower()
    if not normalized:
        return True, 1.0, "empty_response"
    if "[off_scope]" in normalized:
        return True, 0.95, "explicit_marker"
    if normalized.startswith("hors_scope:"):
        return True, 0.9, "explicit_prefix"
    return False, 0.0, None


def map_adapter_error_to_codes(
    err: AIEngineAdapterError | TimeoutError | ConnectionError,
) -> tuple[str, str]:
    """
    Map AI Engine adapter errors to standardized error codes and messages.

    Args:
        err: The exception to map.

    Returns:
        Tuple of (error_code, error_message) for service-level error handling.
    """
    if isinstance(err, AIEngineAdapterError):
        if err.code == "rate_limit_exceeded":
            return "rate_limit_exceeded", "rate limit exceeded"
        if err.code == "context_too_large":
            return "context_too_large", "context too large"
        return err.code, err.message
    if isinstance(err, TimeoutError):
        return "llm_timeout", "llm provider timeout"
    if isinstance(err, ConnectionError):
        return "llm_unavailable", "llm provider is unavailable"
    return "llm_unavailable", "llm provider is unavailable"


ChatGeneratorFunc = Callable[
    [list[dict[str, str]], dict[str, str | None], int, str, str, str],
    Awaitable[
        Any
    ],  # Returns GatewayResult (Any to avoid circular import if needed, but it's imported now)
]
GuidanceGeneratorFunc = Callable[
    [str, dict[str, str | None], int, str, str, str],
    Awaitable[Any],  # Returns GatewayResult
]

_test_chat_generator: ChatGeneratorFunc | None = None
_test_guidance_generator: GuidanceGeneratorFunc | None = None


def set_test_chat_generator(generator: ChatGeneratorFunc | None) -> None:
    """Set a test generator for chat (for unit testing)."""
    global _test_chat_generator
    _test_chat_generator = generator


def set_test_guidance_generator(generator: GuidanceGeneratorFunc | None) -> None:
    """Set a test generator for guidance (for unit testing)."""
    global _test_guidance_generator
    _test_guidance_generator = generator


def reset_test_generators() -> None:
    """Reset all test generators (for cleanup after tests)."""
    global _test_chat_generator, _test_guidance_generator
    _test_chat_generator = None
    _test_guidance_generator = None


def get_test_generators_state() -> tuple[bool, bool]:
    """Return state of test generators (for testing reset behavior)."""
    return (_test_chat_generator is not None, _test_guidance_generator is not None)


class AIEngineAdapterError(AIEngineError):
    """Exception raised by the AI Engine adapter."""

    def __init__(
        self, code: str, message: str, status_code: int = 400, details: dict[str, str] | None = None
    ) -> None:
        self.code = code
        self.message = message  # Compatibility with map_adapter_error_to_codes
        super().__init__(
            error_type=f"ADAPTER_{code.upper()}",
            message=message,
            status_code=status_code,
            details=details,
        )


class AIEngineAdapter:
    """
    Adapter for integrating the AI Engine into existing services.

    Provides a simplified interface for chat and guidance with
    error mapping to service exceptions.
    """

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count for a given text as per AC4."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    @staticmethod
    async def generate_chat_reply(
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str = "fr-FR",
        db: Optional[Session] = None,
        entitlement_result: Any = None,  # Story 66.15: passing entitlement to get plan
    ) -> Any:  # Returns GatewayResult
        """
        Generate a chat reply via the AI Engine.
        (Story 66.3: Refactored to LLMExecutionRequest)
        """
        if _test_chat_generator is not None:
            # ... (unchanged)
            result_raw = await _test_chat_generator(
                messages, context, user_id, request_id, trace_id, locale
            )
            from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo

            if isinstance(result_raw, GatewayResult):
                return result_raw

            raw_text = str(result_raw)
            return GatewayResult(
                use_case="chat_astrologer",
                request_id=request_id,
                trace_id=trace_id,
                raw_output=raw_text,
                usage=UsageInfo(
                    input_tokens=AIEngineAdapter.estimate_tokens(
                        " ".join([m["content"] for m in messages])
                    ),
                    output_tokens=AIEngineAdapter.estimate_tokens(raw_text),
                    total_tokens=0,
                ),
                meta=GatewayMeta(latency_ms=0, model="test-model"),
            )

        logger.info(
            "chat_reply_path request_id=%s history_count=%d has_natal=%s conversation_id=%s",
            request_id,
            len(messages),
            bool(context.get("natal_chart_summary")),
            context.get("conversation_id", "none"),
        )

        try:
            gateway = LLMGateway()

            # 1. Prepare User Input
            last_user_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break

            # Story 66.15 AC3: pass feature and subfeature
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

            # 2. Prepare Context
            history = [
                ExecutionMessage(role=m["role"], content=m["content"]) for m in messages[:-1]
            ]

            extra_context = {**context}
            # Remove keys already handled in request or not relevant for extra_context
            for key in ["conversation_id", "history", "chat_turn_stage"]:
                extra_context.pop(key, None)

            # Story 66.3 AC2: chat_turn_stage handled via extra_context or flags
            if context.get("chat_turn_stage") == "opening":
                extra_context["user_data_block"] = build_opening_chat_user_data_block(
                    last_user_msg=last_user_msg,
                    context=context,
                )
                # We could also use flags here if we had a dedicated flag for 'opening'
                # but for now we follow the instruction to use extra_context["chat_turn_stage"]
                extra_context["chat_turn_stage"] = "opening"

            exec_context = ExecutionContext(
                history=history,
                natal_data=context.get("natal_data"),
                chart_json=context.get("chart_json"),
                astro_context=context.get("astro_context"),
                extra_context=extra_context,
            )

            # 3. Build Request
            request = LLMExecutionRequest(
                user_input=user_input,
                context=exec_context,
                user_id=user_id,
                request_id=request_id,
                trace_id=trace_id,
            )

            # 4. Execute
            result = await gateway.execute_request(request=request, db=db)

            # Fallback estimation if usage is zero but output exists
            if result.usage.output_tokens == 0 and result.raw_output:
                result.usage.output_tokens = AIEngineAdapter.estimate_tokens(result.raw_output)
                logger.warning(
                    "chat_reply_token_fallback request_id=%s estimated_output=%d",
                    request_id,
                    result.usage.output_tokens,
                )

            return result
        except Exception as err:
            if _can_use_test_fallback(err):
                from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo

                fallback_text = _build_test_chat_fallback(messages)
                return GatewayResult(
                    use_case="chat_astrologer",
                    request_id=request_id,
                    trace_id=trace_id,
                    raw_output=fallback_text,
                    usage=UsageInfo(
                        input_tokens=AIEngineAdapter.estimate_tokens(
                            " ".join([m["content"] for m in messages])
                        ),
                        output_tokens=AIEngineAdapter.estimate_tokens(fallback_text),
                    ),
                    meta=GatewayMeta(latency_ms=0, model="test-model"),
                )

            # Combined handler for all LLM-related errors (Finding High)
            from app.llm_orchestration.models import GatewayError

            if isinstance(err, (AIEngineError, GatewayError)):
                _handle_gateway_error(err, request_id, "chat")

            logger.error(
                "ai_engine_adapter_v2_unexpected_error request_id=%s error=%s",
                request_id,
                str(err),
            )
            raise ConnectionError("llm provider unavailable (v2)") from err

    @staticmethod
    async def generate_guidance(
        use_case: str,
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str = "fr-FR",
        db: Optional[Session] = None,
        plan: str = "free",  # Story 66.15: passing plan
    ) -> Any:
        """
        Generate guidance via the AI Engine.
        """
        if _test_guidance_generator is not None:
            # ...
            text = await _test_guidance_generator(
                use_case, context, user_id, request_id, trace_id, locale
            )
            from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo

            return GatewayResult(
                use_case=use_case,
                request_id=request_id,
                trace_id=trace_id,
                raw_output=text,
                usage=UsageInfo(),
                meta=GatewayMeta(latency_ms=0, model="test-model"),
            )

        try:
            gateway = LLMGateway()
            request = _build_guidance_request(
                use_case=use_case,
                context=context,
                locale=locale,
                user_id=user_id,
                request_id=request_id,
                trace_id=trace_id,
            )

            # Story 66.15 AC2: populate feature, subfeature, plan
            request.user_input.feature = "guidance"
            # subfeature is the part after 'guidance_'
            if use_case.startswith("guidance_"):
                request.user_input.subfeature = use_case.replace("guidance_", "")
            elif use_case == "event_guidance":
                request.user_input.subfeature = "event"
            else:
                request.user_input.subfeature = use_case

            request.user_input.plan = plan

            result = await gateway.execute_request(request=request, db=db)
            return result
        except Exception as err:
            if _can_use_test_fallback(err):
                from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo

                return GatewayResult(
                    use_case=use_case,
                    request_id=request_id,
                    trace_id=trace_id,
                    raw_output=_build_test_guidance_fallback(use_case),
                    usage=UsageInfo(),
                    meta=GatewayMeta(latency_ms=0, model="test-model"),
                )

            # Combined handler for all LLM-related errors (Finding High)
            from app.llm_orchestration.models import GatewayError

            if isinstance(err, (AIEngineError, GatewayError)):
                _handle_gateway_error(err, request_id, use_case)

            logger.error(
                "ai_engine_adapter_v2_unexpected_error use_case=%s request_id=%s error=%s",
                use_case,
                request_id,
                str(err),
            )
            raise ConnectionError("llm provider unavailable (v2)") from err

    @staticmethod
    async def generate_natal_interpretation(
        natal_input: NatalExecutionInput, db: Optional[Session] = None
    ) -> Any:  # Returns GatewayResult
        """
        Generate a natal interpretation via the AI Engine.
        (Story 66.7: Natal migration to canonical entry point)
        """
        try:
            gateway = LLMGateway()

            # 1. Prepare User Input
            subfeature = natal_input.use_case_key
            if subfeature == "natal_interpretation_short":
                subfeature = "natal_interpretation"

            user_input = ExecutionUserInput(
                use_case=natal_input.use_case_key,
                feature="natal",
                subfeature=subfeature,
                plan=natal_input.plan,
                locale=natal_input.locale,
                question=natal_input.question,
                persona_id_override=natal_input.persona_id,
            )

            # 2. Prepare Context (AC4: only fields not in common context)
            exec_context = ExecutionContext(
                natal_data=natal_input.natal_data,
                chart_json=natal_input.chart_json,
                astro_context=natal_input.astro_context,
                extra_context={
                    "module": natal_input.module,
                    "variant_code": natal_input.variant_code,
                    "level": natal_input.level,
                },
            )

            # 3. Prepare Flags
            flags = ExecutionFlags(
                validation_strict=natal_input.validation_strict,
                evidence_catalog=natal_input.evidence_catalog,
            )

            # 4. Build Request
            request = LLMExecutionRequest(
                user_input=user_input,
                context=exec_context,
                flags=flags,
                user_id=natal_input.user_id,
                request_id=natal_input.request_id,
                trace_id=natal_input.trace_id,
            )

            # 5. Execute
            result = await gateway.execute_request(request=request, db=db)
            return result

        except Exception as err:
            # Combined handler for all LLM-related errors (Finding High)
            from app.llm_orchestration.models import GatewayError

            if isinstance(err, (AIEngineError, GatewayError)):
                _handle_gateway_error(err, natal_input.request_id, natal_input.use_case_key)

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
        """
        Génère la narration d'horoscope via le pipeline canonique (Story 66.19).
        Remplace LLMNarrator.narrate().
        """
        from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder

        try:
            gateway = LLMGateway()

            # 1. Routage canonique (D1) - Story 66.28 Absorption de daily_prediction
            feature = "horoscope_daily"
            subfeature = "narration"
            if variant_code == "summary_only":
                plan = "free"
            elif variant_code == "full":
                plan = "premium"
            elif variant_code is None:
                # Anciennement daily_prediction / plan=None
                # Story 66.28 AC3 : plan explicite cohérent avec normalisation gateway
                plan = "free"
                logger.info(
                    "ai_engine_adapter_legacy_daily_prediction_route_used request_id=%s",
                    request_id,
                )
            else:
                # AC de Story 66.28 : Ne pas laisser de chemin non validé
                raise ValueError(f"Invalid variant_code for daily narration: {variant_code}")

            # 2. Validation métier de longueur (D4)
            min_sentences = 7 if plan == "free" else 10

            # 3. Construction du prompt via le builder existant (D2)
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

            # 4. Boucle de retry métier (D4)
            final_narrator_result: NarratorResult | None = None

            for attempt in range(1, 3):  # MAX_NARRATION_ATTEMPTS = 2
                question = (
                    base_question
                    if attempt == 1
                    else (
                        base_question
                        + f"\n\nCORRECTION OBLIGATOIRE : daily_synthesis trop courte. "
                        f"Assure-toi d'au moins {min_sentences} phrases complètes."
                    )
                )

                # 5. Build Request
                user_input = ExecutionUserInput(
                    use_case=feature,  # feature as use_case for now
                    feature=feature,
                    subfeature=subfeature,
                    plan=plan,
                    locale="fr-FR" if lang == "fr" else "en-US",
                    question=question,
                )

                exec_context = ExecutionContext(
                    natal_data=None,  # Already in common_context -> question
                    chart_json=None,  # Already in common_context -> question
                    extra_context={
                        "variant_code": variant_code,
                        "astrologer_profile_key": astrologer_profile_key,
                    },
                )

                request = LLMExecutionRequest(
                    user_input=user_input,
                    context=exec_context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                )

                # 6. Execute
                result = await gateway.execute_request(request=request, db=db)

                # Fallback estimation if usage is zero but output exists
                if result.usage.output_tokens == 0 and result.raw_output:
                    result.usage.output_tokens = AIEngineAdapter.estimate_tokens(result.raw_output)

                # 7. Map to legacy NarratorResult (D3)
                final_narrator_result = AIEngineAdapter._map_gateway_result_to_narrator_result(
                    result
                )

                if (
                    final_narrator_result
                    and AIEngineAdapter._count_sentences(final_narrator_result.daily_synthesis)
                    >= min_sentences
                ):
                    return final_narrator_result

            return final_narrator_result

        except Exception as err:
            # Combined handler for all LLM-related errors (Finding High)
            from app.llm_orchestration.models import GatewayError

            if isinstance(err, (AIEngineError, GatewayError)):
                _handle_gateway_error(err, request_id, "horoscope_daily")

            logger.error(
                "ai_engine_adapter_narration_failed request_id=%s error=%s",
                request_id,
                str(err),
            )
            raise

    @staticmethod
    def _map_gateway_result_to_narrator_result(result: GatewayResult) -> NarratorResult | None:
        """
        Mappe GatewayResult vers le contrat legacy NarratorResult (T5).
        """
        if not result.structured_output:
            return None

        data = result.structured_output
        synthesis = data.get("daily_synthesis", "")
        if not synthesis:
            return None

        advice_data = data.get("daily_advice")
        daily_advice = None
        if isinstance(advice_data, dict):
            advice = str(advice_data.get("advice", "")).strip()
            emphasis = str(advice_data.get("emphasis", "")).strip()
            if advice or emphasis:
                daily_advice = NarratorAdvice(advice=advice, emphasis=emphasis)

        # Normalization logic from LLMNarrator
        def as_string(v: Any) -> str:
            return str(v).strip() if v is not None else ""

        tw_raw = data.get("time_window_narratives")
        time_window_narratives = {}
        if isinstance(tw_raw, dict):
            allowed_keys = {"nuit", "matin", "apres_midi", "soiree"}
            time_window_narratives = {
                k: as_string(v) for k, v in tw_raw.items() if k in allowed_keys and as_string(v)
            }

        tp_raw = data.get("turning_point_narratives")
        turning_point_narratives = []
        if isinstance(tp_raw, list):
            turning_point_narratives = [as_string(item) for item in tp_raw if as_string(item)]

        return NarratorResult(
            daily_synthesis=as_string(synthesis),
            astro_events_intro=as_string(data.get("astro_events_intro")),
            time_window_narratives=time_window_narratives,
            turning_point_narratives=turning_point_narratives,
            daily_advice=daily_advice,
            main_turning_point_narrative=as_string(data.get("main_turning_point_narrative"))
            or None,
        )

    @staticmethod
    def _count_sentences(text: str) -> int:
        if not text:
            return 0
        return len([part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()])
