import logging
import re
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai_engine.exceptions import (
    UpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)
from app.ai_engine.services.log_sanitizer import sanitize_request_for_logging
from app.ai_engine.services.utils import calculate_cost
from app.core.config import settings
from app.infra.db.models import LlmOutputSchemaModel, LlmPersonaModel, LlmUseCaseConfigModel
from app.infra.observability.metrics import increment_counter
from app.llm_orchestration.models import (
    GatewayConfigError,
    GatewayError,
    GatewayResult,
    InputValidationError,
    OutputValidationError,
    PromptRenderError,
    UnknownUseCaseError,
    UseCaseConfig,
    is_reasoning_model,
)
from app.llm_orchestration.policies.hard_policy import get_hard_policy
from app.llm_orchestration.providers.responses_client import ResponsesClient
from app.llm_orchestration.services.input_validator import validate_input
from app.llm_orchestration.services.observability_service import log_call
from app.llm_orchestration.services.output_validator import validate_output
from app.llm_orchestration.services.persona_composer import compose_persona_block
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2
from app.llm_orchestration.services.prompt_renderer import PromptRenderer
from app.llm_orchestration.services.repair_prompter import build_repair_prompt
from app.prompts.catalog import resolve_model

logger = logging.getLogger(__name__)

# Use cases that MUST have a valid output schema (premium paid features)
PAID_USE_CASES = {"natal_interpretation", "event_guidance"}

_VALID_INTERACTION_MODES = {"structured", "chat"}
_VALID_QUESTION_POLICIES = {"none", "optional", "required"}

# Locale-aware fallback messages for structured-data-only calls
_FALLBACK_USER_MSG = {
    "fr": "Interprète les données astrologiques fournies.",
    "en": "Analyze the provided astrological data.",
}

# Stub system cores (fallback if V2 disabled)
SYSTEM_CORES = {
    "default_v1": "Tu es un assistant astrologique expert, éthique et précis. "
    "Tu respectes les consignes de sécurité et ne prédis pas la mort ou les maladies graves.",
}

# Stub use cases
USE_CASE_STUBS = {
    "natal_interpretation": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=4000,
        system_core_key="default_v1",
        developer_prompt="Analyse le thème natal pour un utilisateur né le {{birth_date}}. "
        "Données: {{chart_json}}.",
        required_prompt_placeholders=["birth_date", "chart_json"],
    ),
    "natal_interpretation_short": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=4000,
        system_core_key="default_v1",
        developer_prompt="Analyse rapide du thème natal.",
        required_prompt_placeholders=[],
        interaction_mode="structured",
        user_question_policy="optional",
    ),
    "chat": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Réponds à la conversation suivante: {{last_user_msg}}.",
        required_prompt_placeholders=["last_user_msg"],
        interaction_mode="chat",
        user_question_policy="required",
    ),
    "chat_astrologer": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Réponds à la conversation suivante: {{last_user_msg}}.",
        required_prompt_placeholders=["last_user_msg"],
        interaction_mode="chat",
        user_question_policy="required",
    ),
    "guidance_daily": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Génère une guidance quotidienne basée sur le contexte: {{situation}}.",
        required_prompt_placeholders=["situation"],
        interaction_mode="chat",
        user_question_policy="optional",
    ),
    "guidance_weekly": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Génère une guidance hebdomadaire.",
        required_prompt_placeholders=[],
        interaction_mode="chat",
        user_question_policy="none",
    ),
    "guidance_contextual": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Génère une guidance contextuelle pour: {{situation}}.",
        required_prompt_placeholders=["situation"],
        interaction_mode="chat",
        user_question_policy="required",
    ),
    "event_guidance": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=4000,
        system_core_key="default_v1",
        developer_prompt="Guidance pour un événement: {{event_description}}.",
        required_prompt_placeholders=["event_description"],
        interaction_mode="chat",
        user_question_policy="required",
    ),
}


class LLMGateway:
    """
    Main entry point for LLM orchestration.
    """

    def __init__(self, responses_client: Optional[ResponsesClient] = None) -> None:
        self.client = responses_client or ResponsesClient()
        self.renderer = PromptRenderer()

    def build_user_payload(
        self,
        use_case: str,
        user_input: Dict[str, Any],
        context: Dict[str, Any],
        policy: str,
        locale: str,
        chart_json_in_prompt: bool = False,
    ) -> str:
        """
        Centralizes the construction of the user data block (Layer 4).
        Validates user question presence according to the policy.

        Args:
            chart_json_in_prompt: When True, chart_json has already been rendered
                into the developer prompt template and must NOT be duplicated here.
        """
        # Search for question in multiple fields
        question = (
            user_input.get("question")
            or user_input.get("message")
            or user_input.get("last_user_msg")
            or context.get("last_user_msg")
        )

        # 1. Enforce user_question_policy
        if policy == "required" and not question:
            raise InputValidationError(
                f"User question is required for use case '{use_case}'",
                details={"policy": policy},
            )

        # 2. Build parts
        parts: List[str] = []

        if policy != "none" and question:
            parts.append(question)

        if "natal_chart_summary" in context:
            parts.append(f"Natal Chart Summary: {context['natal_chart_summary']}")
        if "situation" in context:
            parts.append(f"Context: {context['situation']}")

        # chart_json is included in user message ONLY if it was NOT already rendered
        # into the developer prompt (redundancy protection).
        if "chart_json" in context and not chart_json_in_prompt:
            parts.append(f"Technical Data: {context['chart_json']}")

        if not parts:
            return _FALLBACK_USER_MSG.get(locale, _FALLBACK_USER_MSG["fr"])

        return "\n".join(parts)

    def compose_chat_messages(
        self,
        system_core: str,
        dev_prompt: str,
        persona_block: Optional[str],
        history: List[Dict[str, Any]],
        user_payload: str,
        locale: str,
    ) -> List[Dict[str, Any]]:
        """Composition layer for 'chat' mode (Layer 1+2+3 + History + 4)."""
        messages = [
            {"role": "system", "content": system_core},
            {"role": "developer", "content": dev_prompt},
        ]
        if persona_block:
            messages.append({"role": "developer", "content": persona_block})

        # Inject conversation history
        for msg in history:
            if "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})
            else:
                logger.warning("gateway_malformed_history_item msg=%s", msg)

        # If user_payload was built from empty parts, use locale-aware fallback
        effective_user = user_payload or _FALLBACK_USER_MSG.get(locale, _FALLBACK_USER_MSG["fr"])
        messages.append({"role": "user", "content": effective_user})
        return messages

    def compose_structured_messages(
        self,
        system_core: str,
        dev_prompt: str,
        persona_block: Optional[str],
        user_payload: str,
    ) -> List[Dict[str, Any]]:
        """Composition layer for 'structured' mode (Layer 1+2+3+4)."""
        messages = [
            {"role": "system", "content": system_core},
            {"role": "developer", "content": dev_prompt},
        ]
        if persona_block:
            messages.append({"role": "developer", "content": persona_block})

        messages.append({"role": "user", "content": user_payload})
        return messages

    async def _resolve_config(
        self, db: Optional[Session], use_case: str, context: Dict[str, Any]
    ) -> UseCaseConfig:
        """Resolves use case configuration from DB or stubs."""
        config = None
        if db:
            try:
                # Replay support: override prompt version if requested in context
                override_id = context.get("_override_prompt_version_id")
                if override_id:
                    from app.infra.db.models import LlmPromptVersionModel

                    db_prompt = db.get(LlmPromptVersionModel, uuid.UUID(override_id))
                else:
                    db_prompt = PromptRegistryV2.get_active_prompt(db, use_case)

                use_case_stmt = select(LlmUseCaseConfigModel).where(
                    LlmUseCaseConfigModel.key == use_case
                )
                db_use_case = db.execute(use_case_stmt).scalar_one_or_none()

                if db_prompt:
                    authorized_vars = {
                        # Use-case specific vars
                        "locale",
                        "use_case",
                        "natal_chart_summary",
                        "last_user_msg",
                        "situation",
                        "birth_date",
                        "birth_time",
                        "birth_timezone",
                        "chart_json",
                        "tone",
                        "persona_name",
                        "event_description",
                        # Story 59.4 — astro context
                        "astro_context",
                        # Story 59.5 — common context (PromptCommonContext fields)
                        "natal_interpretation",
                        "natal_data",
                        "precision_level",
                        "astrologer_profile",
                        "period_covered",
                        "today_date",
                        "use_case_name",
                        "use_case_key",
                    }

                    # Point 28.5 AC4: Use contract (db_use_case) as
                    # source of truth for required variables
                    if db_use_case and db_use_case.required_prompt_placeholders:
                        required = [
                            p
                            for p in db_use_case.required_prompt_placeholders
                            if p in authorized_vars
                        ]
                    else:
                        placeholders = re.findall(
                            r"\{\{([a-zA-Z0-9_]+)\}\}", db_prompt.developer_prompt
                        )
                        required = [p for p in set(placeholders) if p in authorized_vars]

                    resolved_fallback = None
                    if db_use_case and db_use_case.fallback_use_case_key:
                        resolved_fallback = db_use_case.fallback_use_case_key
                    elif db_prompt.fallback_use_case_key:
                        resolved_fallback = db_prompt.fallback_use_case_key

                    config = UseCaseConfig(
                        model=db_prompt.model,
                        temperature=db_prompt.temperature,
                        max_output_tokens=db_prompt.max_output_tokens,
                        system_core_key="default_v1",
                        developer_prompt=db_prompt.developer_prompt,
                        prompt_version_id=str(db_prompt.id),
                        required_prompt_placeholders=required,
                        fallback_use_case=resolved_fallback,
                        persona_strategy=db_use_case.persona_strategy
                        if db_use_case
                        else "optional",
                        safety_profile=db_use_case.safety_profile if db_use_case else "astrology",
                        output_schema_id=db_use_case.output_schema_id if db_use_case else None,
                        input_schema=db_use_case.input_schema if db_use_case else None,
                        reasoning_effort=db_prompt.reasoning_effort,
                        verbosity=db_prompt.verbosity,
                        interaction_mode=db_use_case.interaction_mode
                        if db_use_case
                        else "structured",
                        user_question_policy=db_use_case.user_question_policy
                        if db_use_case
                        else "none",
                    )
                    if db_use_case and "allowed_persona_ids" not in context:
                        context["allowed_persona_ids"] = db_use_case.allowed_persona_ids
            except Exception as e:
                logger.error(
                    "gateway_db_prompt_resolve_failed use_case=%s error=%s", use_case, str(e)
                )

        if not config:
            config = USE_CASE_STUBS.get(use_case)
            logger.warning("gateway_fallback_to_stub use_case=%s", use_case)

        if not config:
            raise UnknownUseCaseError(f"Use case '{use_case}' not found in registry.")

        # 1.1 Centralized model resolution (Story 59.3)
        # Order: OS Granular > OS Legacy > config.model (DB/Stub) > settings.default
        resolved_model = resolve_model(use_case, fallback_model=config.model)

        if resolved_model != config.model:
            config = config.model_copy(update={"model": resolved_model})
            logger.info(
                "gateway_model_resolved use_case=%s model=%s (override active)",
                use_case,
                resolved_model,
            )

        # 1.2 Auto-adjust for reasoning models (o1, etc.)
        config = self._adjust_reasoning_config(config)

        return config

    async def _resolve_persona(
        self, db: Optional[Session], config: UseCaseConfig, context: Dict[str, Any], use_case: str
    ) -> tuple[Optional[str], Optional[str]]:
        """Resolves persona and returns (persona_block, persona_id)."""
        persona_block = None
        resolved_persona_id = context.get("persona_id")

        if config.persona_strategy == "forbidden":
            if resolved_persona_id:
                logger.warning("gateway_persona_forbidden_but_provided use_case=%s", use_case)
            return None, None

        if db and context.get("allowed_persona_ids"):
            allowed_ids = context["allowed_persona_ids"]
            uuid_ids = []
            for pid in allowed_ids:
                try:
                    uuid_ids.append(uuid.UUID(pid))
                except (ValueError, TypeError):
                    logger.warning(
                        "gateway_malformed_persona_uuid pid=%s use_case=%s", pid, use_case
                    )  # noqa: E501
                    continue

            if uuid_ids:
                stmt = select(LlmPersonaModel).where(
                    LlmPersonaModel.id.in_(uuid_ids), LlmPersonaModel.enabled
                )
                db_personas = db.execute(stmt).scalars().all()
                persona_map = {str(p.id): p for p in db_personas}

                requested_id = context.get("persona_id")
                if requested_id:
                    if requested_id in persona_map:
                        resolved_persona = persona_map[requested_id]
                        persona_block = compose_persona_block(resolved_persona)
                        resolved_persona_id = requested_id
                    else:
                        default_persona = None
                        for pid in allowed_ids:
                            if pid in persona_map:
                                default_persona = persona_map[pid]
                                break
                        if default_persona:
                            persona_block = compose_persona_block(default_persona)
                            applied_id = str(default_persona.id)
                        else:
                            applied_id = None
                        increment_counter(
                            "llm_persona_override_rejected_total", labels={"use_case": use_case}
                        )
                        logger.warning(
                            "persona_override_rejected use_case=%s requested=%s applied=%s",
                            use_case,
                            requested_id,
                            applied_id,
                        )
                        resolved_persona_id = applied_id
                else:
                    for pid in allowed_ids:
                        if pid in persona_map:
                            resolved_persona = persona_map[pid]
                            persona_block = compose_persona_block(resolved_persona)
                            resolved_persona_id = pid
                            break

        if not persona_block and config.persona_strategy == "required":
            increment_counter(
                "llm_gateway_config_error_total",
                labels={"use_case": use_case, "reason": "no_persona"},
            )
            raise GatewayConfigError(
                f"No active persona available for required use case '{use_case}'"
            )  # noqa: E501

        if not persona_block:
            persona_block = context.get("persona_block") or context.get("persona_line")

        return persona_block, resolved_persona_id

    def _resolve_schema(
        self, db: Optional[Session], config: UseCaseConfig, use_case: str
    ) -> tuple[Optional[Dict[str, Any]], str, Optional[str]]:
        """Resolves output schema and returns (schema_dict, schema_name, schema_version)."""
        schema_dict = None
        schema_name = use_case
        schema_version = "v1"

        if db and config.output_schema_id:
            try:
                schema_model = db.get(LlmOutputSchemaModel, uuid.UUID(config.output_schema_id))
                if schema_model:
                    schema_dict = schema_model.json_schema
                    schema_name = re.sub(r"[^a-z0-9_-]", "_", schema_model.name.lower())
                    # Story 30-8: Robust version detection from schema name or model version
                    if schema_model.version == 3 or "v3" in schema_name:
                        schema_version = "v3"
                    elif schema_model.version == 2 or "v2" in schema_name:
                        schema_version = "v2"
                    else:
                        schema_version = f"v{schema_model.version}"
            except (ValueError, TypeError):
                logger.error("gateway_invalid_schema_id schema_id=%s", config.output_schema_id)

        is_stub = config.prompt_version_id == "hardcoded-v1"
        is_prod = getattr(settings, "app_env", "development") in {"production", "prod"}
        if use_case in PAID_USE_CASES and not schema_dict and (not is_stub or is_prod):
            raise GatewayConfigError(
                f"Mandatory output schema missing for '{use_case}'. "
                "Ensure the use case has a valid output_schema_id.",
            )

        return schema_dict, schema_name, schema_version

    async def _handle_validation(
        self,
        db: Optional[Session],
        use_case: str,
        result: GatewayResult,
        schema_dict: Optional[Dict[str, Any]],
        context: Dict[str, Any],
        user_input: Dict[str, Any],
        request_id: str,
        trace_id: str,
        user_id: Optional[int],
        is_repair_call: bool,
        visited: List[str],
    ) -> GatewayResult:
        """Handles output validation, automatic repair, and fallback."""
        if not schema_dict:
            result.meta.validation_status = "omitted"
            return result

        evidence_catalog = context.get("evidence_catalog")
        val_strict = context.get("validation_strict")
        if val_strict is None:
            val_strict = use_case in PAID_USE_CASES

        val_result = validate_output(
            result.raw_output,
            schema_dict,
            evidence_catalog=evidence_catalog,
            strict=val_strict,
            use_case=use_case,
            schema_version=result.meta.schema_version,
        )

        increment_counter(
            "llm_output_validation_total",
            labels={
                "use_case": use_case,
                "status": "valid" if val_result.valid else "invalid",
                "schema_version": result.meta.schema_version,
            },
        )

        if val_result.valid:
            result.structured_output = val_result.parsed
            result.meta.validation_status = "repair_success" if is_repair_call else "valid"
            return result

        # Validation failed
        if not is_repair_call:
            logger.warning(
                "gateway_validation_failed_starting_repair use_case=%s errors=%s",
                use_case,
                val_result.errors,
            )
            increment_counter(
                "llm_repair_invoked_total",
                labels={"use_case": use_case, "schema_version": result.meta.schema_version},
            )
            if use_case.startswith("natal"):
                increment_counter(
                    "natal_repair_total",
                    labels={"use_case": use_case, "schema_version": result.meta.schema_version},
                )
            repair_prompt = build_repair_prompt(result.raw_output, val_result.errors, schema_dict)

            repair_context = {
                **context,
                "user_data_block": repair_prompt,
                "locale": context.get("locale"),
                "use_case": use_case,
            }
            repair_result = await self.execute(
                use_case=use_case,
                user_input={},
                context=repair_context,
                request_id=f"{request_id}-repair",
                trace_id=trace_id,
                user_id=user_id,
                db=db,
                is_repair_call=True,
            )
            repair_result.meta.repair_attempted = True
            return repair_result

        # Repair call failed or already a repair call
        if is_repair_call and use_case.startswith("natal"):
            increment_counter(
                "natal_repair_fail_total",
                labels={"use_case": use_case, "schema_version": result.meta.schema_version},
            )
        # Fallback support
        config = await self._resolve_config(db, use_case, context)
        if config.fallback_use_case:
            logger.warning(
                "gateway_validation_failed_triggering_fallback use_case=%s fallback=%s",
                use_case,
                config.fallback_use_case,
            )
            increment_counter(
                "llm_fallback_invoked_total",
                labels={"use_case": use_case, "schema_version": result.meta.schema_version},
            )
            new_visited = visited + [use_case]
            fallback_context = {**context, "_visited_use_cases": new_visited}
            fallback_result = await self.execute(
                use_case=config.fallback_use_case,
                user_input=user_input,
                context=fallback_context,
                request_id=f"{request_id}-fallback",
                trace_id=trace_id,
                user_id=user_id,
                db=db,
            )
            fallback_result.meta.fallback_triggered = True
            fallback_result.meta.validation_status = "fallback"
            return fallback_result

        # Hard failure
        result.meta.validation_errors = val_result.errors
        result.meta.validation_status = "error"
        raise OutputValidationError(
            f"Output validation failed for '{use_case}'",
            details={"errors": val_result.errors},
        )

    def _adjust_reasoning_config(self, config: UseCaseConfig) -> UseCaseConfig:
        """Auto-adjusts tokens, timeout, and reasoning_effort for reasoning models."""
        if is_reasoning_model(config.model):
            updates = {}
            if config.max_output_tokens < 16384:
                updates["max_output_tokens"] = 16384
            if config.timeout_seconds < 180:
                updates["timeout_seconds"] = 180
            # AC7 (Story 30-8): reasoning.effort must always be set for GPT-5/o-series.
            # Default to "medium" to ensure high-quality premium outputs.
            if not config.reasoning_effort:
                updates["reasoning_effort"] = "medium"
            if updates:
                return config.model_copy(update=updates)
        return config

    async def execute(
        self,
        use_case: str,
        user_input: Dict[str, Any],
        context: Dict[str, Any],
        request_id: str,
        trace_id: str,
        user_id: Optional[int] = None,
        db: Optional[Session] = None,
        is_repair_call: bool = False,
    ) -> GatewayResult:
        """
        Execute the LLM gateway for a given use case.
        """
        result: GatewayResult | None = None
        error: Exception | None = None
        config: UseCaseConfig | None = None

        try:
            # 0. Anti-loop protection (circuit breaker)
            visited = context.get("_visited_use_cases", [])
            if use_case in visited and not is_repair_call:
                raise GatewayError(
                    f"Infinite fallback loop detected for use case '{use_case}'",
                    details={"visited": visited},
                )

            # 1. Resolve config
            config = await self._resolve_config(db, use_case, context)

            # Story 59.5: Build and merge common context
            if db and user_id is not None:
                try:
                    from app.prompts.common_context import CommonContextBuilder

                    # Detect period from context or use_case
                    period = "daily"
                    if "weekly" in use_case or context.get("period") == "weekly":
                        period = "weekly"

                    common_ctx = CommonContextBuilder.build(
                        user_id=user_id, use_case_key=use_case, period=period, db=db
                    )
                    # Merge common context (use_case context has priority)
                    context = {**common_ctx.model_dump(), **context}
                except Exception as e:
                    logger.warning(
                        "gateway_common_context_failed use_case=%s error=%s", use_case, e
                    )

            # 2. Log start
            if not is_repair_call:
                log_payload = sanitize_request_for_logging(
                    use_case=use_case,
                    user_id="unknown",
                    request_id=request_id,
                    trace_id=trace_id,
                    input_data=user_input,
                    context=context,
                )
                logger.info("llm_gateway_start %s", log_payload)

            # 3. Validation runtime locale/use_case
            merged_vars = {**user_input, **context}
            for req_var in ["locale", "use_case"]:
                if req_var not in merged_vars:
                    increment_counter(
                        "llm_gateway_config_error_total",
                        labels={"use_case": use_case, "reason": f"missing_{req_var}"},
                    )
                    raise GatewayConfigError(f"Missing mandatory platform variable: '{req_var}'")

            locale = merged_vars["locale"]

            # 4. Mode & Policy check
            if config.interaction_mode not in _VALID_INTERACTION_MODES:
                raise GatewayConfigError(
                    f"Invalid interaction_mode '{config.interaction_mode}' for '{use_case}'"
                )
            if config.user_question_policy not in _VALID_QUESTION_POLICIES:
                raise GatewayConfigError(
                    f"Invalid user_question_policy '{config.user_question_policy}' for '{use_case}'"
                )

            # 5. Input validation
            if config.input_schema:
                input_val = validate_input(user_input, config.input_schema)
                if not input_val.valid:
                    increment_counter(
                        "llm_input_validation_errors_total", labels={"use_case": use_case}
                    )
                    raise InputValidationError(
                        f"Input validation failed for '{use_case}'",
                        details={"errors": input_val.errors},
                    )

            # 6. Render prompts
            render_vars = {
                k: v for k, v in merged_vars.items() if k in config.required_prompt_placeholders
            }
            render_vars["locale"] = locale
            render_vars["use_case"] = merged_vars["use_case"]

            try:
                if is_repair_call:
                    rendered_developer_prompt = (
                        "Tu es un assistant technique. Ta seule mission est de corriger le format JSON "  # noqa: E501
                        "d'une réponse précédente pour qu'elle respecte strictement le schéma fourni. "  # noqa: E501
                        "Ne modifie pas le sens profond. Réponds EXCLUSIVEMENT avec le bloc JSON."
                    )
                else:
                    rendered_developer_prompt = self.renderer.render(
                        config.developer_prompt,
                        render_vars,
                        required_variables=config.required_prompt_placeholders,
                    )
            except PromptRenderError as err:
                increment_counter("llm_prompt_render_error_total", labels={"use_case": use_case})
                logger.error(
                    "gateway_prompt_render_error use_case=%s request_id=%s error=%s",
                    use_case,
                    request_id,
                    str(err),
                )
                raise

            # 7. Layer 1 (Hard Policy)
            try:
                system_core = get_hard_policy(config.safety_profile)
            except ValueError as e:
                raise GatewayConfigError(str(e))

            # 8. Layer 3 (Persona)
            persona_block, resolved_persona_id = await self._resolve_persona(
                db, config, context, use_case
            )

            # 9. Layer 4 (User Data) & Composition
            user_data_block = context.get("user_data_block")
            if not user_data_block:
                user_data_block = self.build_user_payload(
                    use_case=use_case,
                    user_input=user_input,
                    context=context,
                    policy=config.user_question_policy,
                    locale=locale,
                    chart_json_in_prompt="{{chart_json}}" in config.developer_prompt,
                )

            if config.interaction_mode == "chat":
                messages = self.compose_chat_messages(
                    system_core=system_core,
                    dev_prompt=rendered_developer_prompt,
                    persona_block=persona_block,
                    history=context.get("history", []),
                    user_payload=user_data_block,
                    locale=locale,
                )
            else:
                messages = self.compose_structured_messages(
                    system_core=system_core,
                    dev_prompt=rendered_developer_prompt,
                    persona_block=persona_block,
                    user_payload=user_data_block,
                )

            # 10. Call Provider
            schema_dict, schema_name, schema_version = self._resolve_schema(db, config, use_case)

            try:
                result = await self.client.execute(
                    messages=messages,
                    model=config.model,  # Story 59.3: Final resolved model from config
                    temperature=config.temperature,
                    max_output_tokens=config.max_output_tokens,
                    timeout_seconds=config.timeout_seconds,
                    request_id=request_id,
                    trace_id=trace_id,
                    use_case=use_case,
                    reasoning_effort=config.reasoning_effort,
                    verbosity=config.verbosity,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name,
                            "schema": schema_dict,
                            "strict": True,
                        },
                    }
                    if schema_dict
                    else None,
                )
            except (UpstreamRateLimitError, UpstreamTimeoutError, UpstreamError):
                # Preserve upstream exception types so API routers can map
                # precise HTTP status codes (429/503/504).
                raise

            # 11. Finalize Metadata
            result.meta.prompt_version_id = config.prompt_version_id
            result.meta.persona_id = resolved_persona_id
            result.meta.output_schema_id = config.output_schema_id
            result.meta.schema_version = schema_version
            result.meta.model_override_active = (
                config.model != USE_CASE_STUBS.get(use_case, config).model
            )
            result.usage.estimated_cost_usd = calculate_cost(
                result.usage.input_tokens, result.usage.output_tokens
            )

            # 12. Validation & Repair
            return await self._handle_validation(
                db=db,
                use_case=use_case,
                result=result,
                schema_dict=schema_dict,
                context=context,
                user_input=user_input,
                request_id=request_id,
                trace_id=trace_id,
                user_id=user_id,
                is_repair_call=is_repair_call,
                visited=visited,
            )

        except Exception as e:
            error = e
            raise
        finally:
            if db and not is_repair_call:
                final_status = "error"
                model_name = "unknown"
                if result:
                    final_status = result.meta.validation_status
                    model_name = result.meta.model or "unknown"
                elif error:
                    final_status = "error"

                increment_counter(
                    "llm_gateway_requests_total",
                    labels={
                        "use_case": use_case,
                        "model": model_name,
                        "status": final_status,
                        "mode": config.interaction_mode if config else "unknown",
                    },
                )

                await log_call(
                    db=db,
                    use_case=use_case,
                    request_id=request_id,
                    trace_id=trace_id,
                    user_input=user_input,
                    result=result,
                    error=error,
                )
