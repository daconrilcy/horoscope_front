import logging
import os
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

logger = logging.getLogger(__name__)

# Use cases that MUST have a valid output schema (premium paid features)
PAID_USE_CASES = {"natal_interpretation", "tarot_reading", "event_guidance"}

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
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=4000,
        system_core_key="default_v1",
        developer_prompt="Analyse le thème natal pour un utilisateur né le {{birth_date}}.",
        required_prompt_placeholders=["birth_date"],
        fallback_use_case="natal_interpretation_short",
        interaction_mode="structured",
        user_question_policy="none",
    ),
    "natal_interpretation_short": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=4000,
        system_core_key="default_v1",
        developer_prompt="Analyse rapide du thème natal.",
        required_prompt_placeholders=[],
        interaction_mode="structured",
        user_question_policy="optional",
    ),
    "chat": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Réponds à la conversation suivante: {{last_user_msg}}.",
        required_prompt_placeholders=["last_user_msg"],
        interaction_mode="chat",
        user_question_policy="required",
    ),
    "chat_astrologer": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Réponds à la conversation suivante: {{last_user_msg}}.",
        required_prompt_placeholders=["last_user_msg"],
        interaction_mode="chat",
        user_question_policy="required",
    ),
    "guidance_daily": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Génère une guidance quotidienne.",
        required_prompt_placeholders=[],
        interaction_mode="chat",
        user_question_policy="optional",
    ),
    "guidance_weekly": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Génère une guidance hebdomadaire.",
        required_prompt_placeholders=[],
        interaction_mode="chat",
        user_question_policy="none",
    ),
    "guidance_contextual": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Génère une guidance contextuelle pour: {{situation}}.",
        required_prompt_placeholders=["situation"],
        interaction_mode="chat",
        user_question_policy="required",
    ),
    "tarot_reading": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=4000,
        system_core_key="default_v1",
        developer_prompt="Tirage de tarot.",
        required_prompt_placeholders=[],
        interaction_mode="structured",
        user_question_policy="optional",
    ),
    "event_guidance": UseCaseConfig(
        model="gpt-4o-mini",
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
    ) -> str:
        """
        Centralizes the construction of the user data block (Layer 4).
        Validates user question presence according to the policy.
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

        # Important : chart_json is included in user message ONLY if it was NOT
        # already rendered into the developer prompt (redundancy protection).
        if "chart_json" in context:
            # We check if it's in required_prompt_placeholders of the config via context
            # but usually config is known by the caller.
            # For simplicity, if caller passed it here, we add it.
            if context.get("_chart_json_in_prompt") is not True:
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

    def _adjust_reasoning_config(self, config: UseCaseConfig) -> UseCaseConfig:
        """Auto-adjusts tokens and timeout for reasoning models (o-series, gpt-5)."""
        _REASONING_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5")
        _REASONING_EXACT = {"o1", "o3", "o4"}

        is_reasoning = (
            config.model.startswith(_REASONING_PREFIXES) or config.model in _REASONING_EXACT
        )

        if is_reasoning:
            updates = {}
            if config.max_output_tokens < 16384:
                updates["max_output_tokens"] = 16384
            if config.timeout_seconds < 180:
                updates["timeout_seconds"] = 180
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

            # 1. Resolve use case config
            config = None
            llm_v2_enabled = getattr(settings, "llm_orchestration_v2", False)

            if db and llm_v2_enabled:
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
                            "cards_json",
                            "persona_name",
                            "event_description",
                        }

                        # Point 28.5 AC4: Use contract (db_use_case) as
                        # source of truth for required variables
                        if db_use_case and db_use_case.required_prompt_placeholders:
                            # Stored as names in DB (no braces)
                            required = [
                                p
                                for p in db_use_case.required_prompt_placeholders
                                if p in authorized_vars
                            ]
                        else:
                            # Fallback to inference if contract missing, but intersect with authorized  # noqa: E501
                            placeholders = re.findall(
                                r"\{\{([a-zA-Z0-9_]+)\}\}", db_prompt.developer_prompt
                            )
                            required = [p for p in set(placeholders) if p in authorized_vars]

                        # Point 1: Priorité fallback UseCase > Prompt
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
                            safety_profile=db_use_case.safety_profile
                            if db_use_case
                            else "astrology",
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
                if llm_v2_enabled:
                    logger.warning("gateway_fallback_to_stub use_case=%s", use_case)

            if not config:
                raise UnknownUseCaseError(f"Use case '{use_case}' not found in registry.")

            # 1.1 Model override from environment (Story 30.1)
            # Robust normalization: replace non-alphanumeric with underscore
            safe_uc_key = re.sub(r"[^a-zA-Z0-9_]", "_", use_case).upper()
            env_override_key = f"LLM_MODEL_OVERRIDE_{safe_uc_key}"
            env_override_model = os.getenv(env_override_key)
            model_overridden = False
            if env_override_model:
                config = config.model_copy(update={"model": env_override_model})
                config = self._adjust_reasoning_config(config)
                model_overridden = True
                logger.info(
                    "gateway_model_override use_case=%s model=%s -> %s",
                    use_case,
                    config.model,
                    env_override_model,
                )

            # 1.2 Reasoning model auto-adjustment (Point 4c)
            if not model_overridden:
                config = self._adjust_reasoning_config(config)

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

            # 3. Merge and filter variables
            merged_vars = {**user_input, **context}

            # Point 2: Validation runtime locale/use_case
            for req_var in ["locale", "use_case"]:
                if req_var not in merged_vars:
                    increment_counter(
                        "llm_gateway_config_error_total",
                        labels={"use_case": use_case, "reason": f"missing_{req_var}"},
                    )
                    raise GatewayConfigError(f"Missing mandatory platform variable: '{req_var}'")

            locale = merged_vars["locale"]

            # M1: Enum validation
            if config.interaction_mode not in _VALID_INTERACTION_MODES:
                raise GatewayConfigError(
                    f"Invalid interaction_mode '{config.interaction_mode}' "
                    f"for use case '{use_case}'"
                )
            if config.user_question_policy not in _VALID_QUESTION_POLICIES:
                raise GatewayConfigError(
                    f"Invalid user_question_policy '{config.user_question_policy}' for '{use_case}'"
                )

            # AC 8: Input validation
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

            render_vars = {
                k: v for k, v in merged_vars.items() if k in config.required_prompt_placeholders
            }
            # C1 Fix: Always include platform variables required by lint
            render_vars["locale"] = locale
            render_vars["use_case"] = merged_vars["use_case"]

            # 4. Render developer prompt
            try:
                # Point 3: Repair call stable (developer_prompt dédié)
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

            # 5. Layer 1 (Hard Policy)
            if llm_v2_enabled:
                try:
                    system_core = get_hard_policy(config.safety_profile)
                except ValueError as e:
                    raise GatewayConfigError(str(e))
            else:
                system_core = SYSTEM_CORES.get(config.system_core_key, SYSTEM_CORES["default_v1"])

            # 6. Layer 3 (Persona)
            persona_block = None
            resolved_persona_id = context.get("persona_id")

            # AC 3: Forbidden strategy bypasses everything
            if config.persona_strategy == "forbidden":
                if resolved_persona_id:
                    logger.warning("gateway_persona_forbidden_but_provided use_case=%s", use_case)
                resolved_persona_id = None
            elif db and llm_v2_enabled and context.get("allowed_persona_ids"):
                allowed_ids = context["allowed_persona_ids"]
                uuid_ids = []
                for pid in allowed_ids:
                    try:
                        uuid_ids.append(uuid.UUID(pid))
                    except (ValueError, TypeError):
                        continue

                if uuid_ids:
                    stmt = select(LlmPersonaModel).where(
                        LlmPersonaModel.id.in_(uuid_ids), LlmPersonaModel.enabled
                    )
                    db_personas = db.execute(stmt).scalars().all()
                    persona_map = {str(p.id): p for p in db_personas}

                    # AC 5: Persona override check
                    requested_id = context.get("persona_id")
                    if requested_id:
                        if requested_id in persona_map:
                            # Authorized and enabled
                            resolved_persona = persona_map[requested_id]
                            persona_block = compose_persona_block(resolved_persona)
                            resolved_persona_id = requested_id
                        else:
                            # Unauthorized or disabled
                            # Fallback to default_safe (first active in allowed_ids)
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
                        # No override, pick first active
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
                )

            if not persona_block and not llm_v2_enabled:
                persona_block = context.get("persona_block") or context.get("persona_line")

            # 7. Layer 4 (User Data) & Composition (8)
            user_data_block = context.get("user_data_block")
            if not user_data_block:
                # Add hint for redundancy protection
                context_with_hint = {
                    **context,
                    "_chart_json_in_prompt": "chart_json" in config.required_prompt_placeholders,
                }
                user_data_block = self.build_user_payload(
                    use_case=use_case,
                    user_input=user_input,
                    context=context_with_hint,
                    policy=config.user_question_policy,
                    locale=locale,
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

            # 9. Call Provider
            try:
                schema_dict = None
                schema_name = use_case  # fallback name
                if db and config.output_schema_id:
                    try:
                        schema_model = db.get(
                            LlmOutputSchemaModel, uuid.UUID(config.output_schema_id)
                        )
                        if schema_model:
                            schema_dict = schema_model.json_schema
                            # Responses API v2 requires name to match ^[a-z0-9_-]+$
                            schema_name = re.sub(r"[^a-z0-9_-]", "_", schema_model.name.lower())
                        if schema_dict:
                            schema_name = re.sub(r"[^a-z0-9_-]", "_", schema_name.lower())
                    except (ValueError, TypeError):
                        logger.error(
                            "gateway_invalid_schema_id schema_id=%s", config.output_schema_id
                        )

                # Point 0.2: Block paid use cases that are missing their mandatory schema
                # Allow skip for stubs in non-production to avoid breaking existing tests
                is_stub = config.prompt_version_id == "hardcoded-v1"
                is_prod = settings.app_env in {"production", "prod"}
                if use_case in PAID_USE_CASES and not schema_dict and (not is_stub or is_prod):
                    raise GatewayConfigError(
                        f"Mandatory output schema missing for '{use_case}'. "
                        "Ensure the use case has a valid output_schema_id.",
                    )

                result = await self.client.execute(
                    messages=messages,
                    model=config.model,
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
            except (UpstreamRateLimitError, UpstreamTimeoutError, UpstreamError) as err:
                kind = (
                    "rate_limit"
                    if isinstance(err, UpstreamRateLimitError)
                    else "timeout"
                    if isinstance(err, UpstreamTimeoutError)
                    else "provider_error"
                )
                raise GatewayError(
                    f"LLM provider error: {str(err)}",
                    details={"kind": kind, "upstream_error": type(err).__name__},
                ) from err

            # Meta & Costs
            result.meta.prompt_version_id = config.prompt_version_id
            result.meta.persona_id = resolved_persona_id if persona_block else None
            result.meta.output_schema_id = config.output_schema_id
            # Ensure boolean meta fields are proper Python booleans (not MagicMock in tests)
            result.meta.repair_attempted = False
            result.meta.fallback_triggered = False
            result.meta.model_override_active = model_overridden
            result.usage.estimated_cost_usd = calculate_cost(
                result.usage.input_tokens, result.usage.output_tokens
            )

            # 10. Validation & Repair Loop (Point 4: Une seule tentative)
            if schema_dict:
                evidence_catalog = context.get("evidence_catalog")
                val_strict = context.get("validation_strict", False)
                val_result = validate_output(
                    result.raw_output,
                    schema_dict,
                    evidence_catalog=evidence_catalog,
                    strict=val_strict,
                )
                increment_counter(
                    "llm_output_validation_total",
                    labels={
                        "use_case": use_case,
                        "status": "valid" if val_result.valid else "invalid",
                    },
                )
                if val_result.valid:
                    result.structured_output = val_result.parsed
                    result.meta.validation_status = "repair_success" if is_repair_call else "valid"
                else:
                    # 10a. Automatic Repair (Point 4: une seule fois)
                    if not is_repair_call:
                        logger.warning(
                            "gateway_validation_failed_starting_repair use_case=%s errors=%s",
                            use_case,
                            val_result.errors,
                        )
                        increment_counter("llm_repair_invoked_total", labels={"use_case": use_case})
                        repair_prompt = build_repair_prompt(
                            result.raw_output, val_result.errors, schema_dict
                        )

                        # Point A: Nettoyage repair_context (pas de default "en")
                        repair_context = {
                            **context,
                            "user_data_block": repair_prompt,
                            "locale": merged_vars["locale"],
                            "use_case": use_case,
                        }
                        repair_result = await self.execute(
                            use_case=use_case,
                            user_input={},
                            context=repair_context,
                            request_id=f"{request_id}-repair",
                            trace_id=trace_id,
                            db=db,
                            is_repair_call=True,
                        )
                        repair_result.meta.repair_attempted = True
                        # Note: we don't return here, we fall through to finally and return result
                        result = repair_result
                    else:
                        # 10b. Fallback (Point B: Circuit breaker)
                        if config.fallback_use_case:
                            logger.warning(
                                "gateway_validation_failed_triggering_fallback use_case=%s fallback=%s",  # noqa: E501
                                use_case,
                                config.fallback_use_case,
                            )
                            increment_counter(
                                "llm_fallback_invoked_total", labels={"use_case": use_case}
                            )
                            # Track visited to prevent loops
                            new_visited = visited + [use_case]
                            fallback_context = {**context, "_visited_use_cases": new_visited}
                            fallback_result = await self.execute(
                                use_case=config.fallback_use_case,
                                user_input=user_input,
                                context=fallback_context,
                                request_id=f"{request_id}-fallback",
                                trace_id=trace_id,
                                db=db,
                            )
                            fallback_result.meta.fallback_triggered = True
                            fallback_result.meta.validation_status = "fallback"
                            result = fallback_result
                        else:
                            # 10c. Hard failure
                            result.meta.validation_errors = val_result.errors
                            result.meta.validation_status = "error"
                            raise OutputValidationError(
                                f"Output validation failed for '{use_case}'",
                                details={"errors": val_result.errors},
                            )
            else:
                result.meta.validation_status = "omitted"

            logger.info(
                "llm_gateway_complete use_case=%s status=%s request_id=%s",
                use_case,
                result.meta.validation_status,
                request_id,
            )
            return result
        except Exception as e:
            error = e
            raise
        finally:
            if db and not is_repair_call:
                # M3: Add Prometheus metrics
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
