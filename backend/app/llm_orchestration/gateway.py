from __future__ import annotations

import logging
import re
import uuid
from typing import Any, Dict, Optional

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
        max_output_tokens=1800,
        system_core_key="default_v1",
        developer_prompt="Analyse le thème natal pour un utilisateur né le {{birth_date}}. "
        "Utilise les positions planétaires suivantes: {{chart_json}}.",
        required_prompt_placeholders=["birth_date", "chart_json"],
        fallback_use_case="natal_interpretation_short",
    ),
    "chat": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=1000,
        system_core_key="default_v1",
        developer_prompt="Réponds à la conversation suivante: {{last_user_msg}}.",
        required_prompt_placeholders=["last_user_msg"],
    ),
    "guidance_daily": UseCaseConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=1000,
        system_core_key="default_v1",
        developer_prompt="Génère une guidance quotidienne basée sur le contexte: {{situation}}.",
        required_prompt_placeholders=["situation"],
    ),
}


class LLMGateway:
    """
    Main entry point for LLM orchestration.
    """

    def __init__(self, responses_client: Optional[ResponsesClient] = None) -> None:
        self.client = responses_client or ResponsesClient()
        self.renderer = PromptRenderer()

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
                    raise GatewayConfigError(f"Missing mandatory platform variable: '{req_var}'")

            # AC 8: Input validation
            if config.input_schema:
                input_val = validate_input(user_input, config.input_schema)
                if not input_val.valid:
                    raise InputValidationError(
                        f"Input validation failed for '{use_case}'",
                        details={"errors": input_val.errors},
                    )

            render_vars = {
                k: v for k, v in merged_vars.items() if k in config.required_prompt_placeholders
            }

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
                raise GatewayConfigError(
                    f"No active persona available for required use case '{use_case}'"
                )

            if not persona_block and not llm_v2_enabled:
                persona_block = context.get("persona_block") or context.get("persona_line")

            # 7. Layer 4 (User Data)
            user_data_block = context.get("user_data_block")
            if not user_data_block:
                parts = []
                if "natal_chart_summary" in context:
                    parts.append(f"Natal Chart: {context['natal_chart_summary']}")
                if "situation" in context:
                    parts.append(f"Situation: {context['situation']}")
                if "chart_json" in context:
                    parts.append(f"Chart Data: {context['chart_json']}")
                user_data_block = "\n".join(parts) if parts else "User context data provided."

            # 8. Compose Messages
            messages = [
                {"role": "system", "content": system_core},
                {"role": "developer", "content": rendered_developer_prompt},
            ]
            if persona_block:
                messages.append({"role": "developer", "content": persona_block})
            messages.append({"role": "user", "content": user_data_block})

            # 9. Call Provider
            try:
                schema_dict = None
                if db and config.output_schema_id:
                    try:
                        schema_model = db.get(
                            LlmOutputSchemaModel, uuid.UUID(config.output_schema_id)
                        )
                        if schema_model:
                            schema_dict = schema_model.json_schema
                    except (ValueError, TypeError):
                        logger.error(
                            "gateway_invalid_schema_id schema_id=%s", config.output_schema_id
                        )

                result = await self.client.execute(
                    messages=messages,
                    model=config.model,
                    temperature=config.temperature,
                    max_output_tokens=config.max_output_tokens,
                    request_id=request_id,
                    trace_id=trace_id,
                    use_case=use_case,
                    response_format={"type": "json_schema", "json_schema": schema_dict}
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
            result.usage.estimated_cost_usd = calculate_cost(
                result.usage.input_tokens, result.usage.output_tokens
            )

            # 10. Validation & Repair Loop (Point 4: Une seule tentative)
            if schema_dict:
                val_result = validate_output(result.raw_output, schema_dict)
                if val_result.valid:
                    result.structured_output = val_result.parsed
                    result.meta.validation_status = "repaired" if is_repair_call else "valid"
                else:
                    # 10a. Automatic Repair (Point 4: une seule fois)
                    if not is_repair_call:
                        logger.warning(
                            "gateway_validation_failed_starting_repair use_case=%s errors=%s",
                            use_case,
                            val_result.errors,
                        )
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
                await log_call(
                    db=db,
                    use_case=use_case,
                    request_id=request_id,
                    trace_id=trace_id,
                    user_input=user_input,
                    result=result,
                    error=error,
                )
