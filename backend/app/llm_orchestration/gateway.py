import logging
import os
import re
import time
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models import LlmOutputSchemaModel, LlmPersonaModel, LlmUseCaseConfigModel
from app.infra.observability.metrics import increment_counter
from app.llm_orchestration.admin_models import ResolvedAssembly
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionMessage,
    ExecutionUserInput,
    GatewayConfigError,
    GatewayError,
    GatewayResult,
    InputValidationError,
    LLMExecutionRequest,
    OutputValidationError,
    RecoveryResult,
    ResolvedExecutionPlan,
    ResponseFormatConfig,
    UnknownUseCaseError,
    UseCaseConfig,
    is_reasoning_model,
)
from app.llm_orchestration.policies.hard_policy import get_hard_policy
from app.llm_orchestration.providers.responses_client import ResponsesClient
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.assembly_resolver import (
    assemble_developer_prompt,
    resolve_assembly,
)
from app.llm_orchestration.services.input_validator import validate_input
from app.llm_orchestration.services.observability_service import log_call
from app.llm_orchestration.services.output_validator import ValidationResult, validate_output
from app.llm_orchestration.services.persona_composer import compose_persona_block
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2
from app.llm_orchestration.services.prompt_renderer import PromptRenderer
from app.llm_orchestration.services.repair_prompter import build_repair_prompt
from app.prompts.catalog import PROMPT_CATALOG, resolve_model
from app.prompts.common_context import CommonContextBuilder, QualifiedContext

logger = logging.getLogger(__name__)

# Use cases that MUST have a valid output schema (premium paid features)
PAID_USE_CASES = {"natal_interpretation", "event_guidance", "natal_interpretation_short"}

_VALID_INTERACTION_MODES = {"structured", "chat"}
_VALID_QUESTION_POLICIES = {"none", "optional", "required"}

# Locale-aware fallback messages for structured-data-only calls
_FALLBACK_USER_MSG = {
    "fr": "Interprète les données astrologiques fournies.",
    "en": "Analyze the provided astrological data.",
}

# ComposedMessages type alias (Story 66.4 AC3)
ComposedMessages = List[Dict[str, Any]]


# Stub system cores
SYSTEM_CORES = {
    "default_v1": "Tu es un assistant astrologique expert, éthique et précis. "
    "Tu respectes les consignes de sécurité et ne prédis pas la mort ou les maladies graves.",
}

# Stub use cases
USE_CASE_STUBS = {
    "natal_long_free": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=1000,
        system_core_key="default_v1",
        developer_prompt=(
            "Langue de reponse : francais ({{locale}}). Contexte : use_case={{use_case}}.\n\n"
            "Interpretez le theme natal fourni de facon claire, chaleureuse et non fataliste, "
            "strictement a partir des donnees techniques suivantes :\n"
            "{{chart_json}}\n\n"
            "Retourne uniquement un JSON valide with exactly :\n"
            '- "title" : une phrase courte et fluide qui synthétise le profil natal '
            "dans un style éditorial, rédigée au vouvoiement, sans deux-points ni guillemets.\n"
            '- "summary" : un portrait natal en 5 a 7 phrases fluides, redige au vouvoiement, '
            "avec un peu plus de matiere qu'un simple resume.\n"
            '- "accordion_titles" : une liste de 2 a 4 titres courts, concrets et distincts '
            "pour les sections premium verrouillees.\n\n"
            "Contraintes :\n"
            "- N'invente aucun placement, aspect ou maison absent des donnees.\n"
            "- Utilisez toujours 'vous' et 'votre', jamais 'il', 'elle' ou 'cette personne'.\n"
            "- Le champ 'title' doit ressembler a une accroche premium concise, "
            "pas a un label generique.\n"
            "- Donnez un portrait nuance, utile et incarné, sans jargon inutile.\n"
            "- Pas de promesse absolue, pas de fatalisme.\n"
            "- Aucun markdown, aucun texte hors JSON."
        ),
        required_prompt_placeholders=["chart_json", "locale", "use_case"],
        interaction_mode="structured",
        user_question_policy="none",
    ),
    "natal-long-free": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=1000,
        system_core_key="default_v1",
        developer_prompt="Génère un horoscope natal long (stub).",
        required_prompt_placeholders=[],
        interaction_mode="structured",
        user_question_policy="none",
    ),
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
        interaction_mode="structured",
        user_question_policy="none",
    ),
    "horoscope_daily": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=3000,
        system_core_key="default_v1",
        developer_prompt="Génère un horoscope quotidien (stub). Question: {{question}}",
        required_prompt_placeholders=["question"],
        interaction_mode="structured",
        user_question_policy="none",
    ),
    "daily_prediction": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=1600,
        system_core_key="default_v1",
        developer_prompt="Génère des prédictions quotidiennes (stub). Question: {{question}}",
        required_prompt_placeholders=["question"],
        interaction_mode="structured",
        user_question_policy="none",
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
    "astrologer_selection_help": UseCaseConfig(
        model=settings.openai_model_default,
        temperature=0.7,
        max_output_tokens=2000,
        system_core_key="default_v1",
        developer_prompt="Aide l'utilisateur à choisir un astrologue.",
        required_prompt_placeholders=[],
        interaction_mode="chat",
        user_question_policy="optional",
    ),
}


class LLMGateway:
    """
    Main entry point for LLM orchestration.
    Refactored into a 6-stage pipeline (Story 66.4).
    Enriched with telemetry and qualified context (Story 66.6).
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

        if "natal_chart_summary" in context and context["natal_chart_summary"]:
            parts.append(f"Natal Chart Summary: {context['natal_chart_summary']}")
        if "situation" in context and context["situation"]:
            parts.append(f"Context: {context['situation']}")

        if "chart_json" in context and context["chart_json"] and not chart_json_in_prompt:
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
    ) -> ComposedMessages:
        """Composition layer for 'chat' mode (Layer 1+2+3 + History + 4)."""
        messages = [
            {"role": "system", "content": system_core},
            {"role": "developer", "content": dev_prompt},
        ]
        if persona_block:
            messages.append({"role": "developer", "content": persona_block})

        for msg in history:
            if "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})
            else:
                logger.warning("gateway_malformed_history_item msg=%s", msg)

        effective_user = user_payload or _FALLBACK_USER_MSG.get(locale, _FALLBACK_USER_MSG["fr"])
        messages.append({"role": "user", "content": effective_user})
        return messages

    def compose_structured_messages(
        self,
        system_core: str,
        dev_prompt: str,
        persona_block: Optional[str],
        user_payload: str,
    ) -> ComposedMessages:
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
                
                if db_use_case and "allowed_persona_ids" not in context:
                    context["allowed_persona_ids"] = db_use_case.allowed_persona_ids

                if db_prompt:
                    logger.debug(
                        "gateway_db_prompt_found use_case=%s model=%s effort=%s verbosity=%s", 
                        use_case, db_prompt.model, db_prompt.reasoning_effort, db_prompt.verbosity
                    )
                    authorized_vars = {
                        "locale", "use_case", "natal_chart_summary", "last_user_msg",
                        "situation", "birth_date", "birth_time", "birth_timezone",
                        "chart_json", "tone", "persona_name", "event_description",
                        "astro_context", "natal_interpretation", "natal_data",
                        "precision_level", "astrologer_profile", "period_covered",
                        "today_date", "use_case_name", "use_case_key",
                        "current_datetime", "current_timezone", "current_location",
                    }

                    if db_use_case and db_use_case.required_prompt_placeholders:
                        required = [
                            p for p in db_use_case.required_prompt_placeholders
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
                        prompt_version_id=(
                            str(db_prompt.id) if hasattr(db_prompt, "id") else "hardcoded-v1"
                        ),
                        required_prompt_placeholders=required,
                        fallback_use_case=resolved_fallback,
                        persona_strategy=(
                            db_use_case.persona_strategy if db_use_case else "optional"
                        ),
                        safety_profile=(
                            db_use_case.safety_profile if db_use_case else "astrology"
                        ),
                        output_schema_id=(
                            db_use_case.output_schema_id if db_use_case else None
                        ),
                        input_schema=db_use_case.input_schema if db_use_case else None,
                        reasoning_effort=db_prompt.reasoning_effort,
                        verbosity=db_prompt.verbosity,
                        interaction_mode=(
                            db_use_case.interaction_mode if db_use_case else "structured"
                        ),
                        user_question_policy=(
                            db_use_case.user_question_policy if db_use_case else "none"
                        ),
                    )
            except Exception as e:
                logger.error(
                    "gateway_db_prompt_resolve_failed use_case=%s error=%s", 
                    use_case, str(e)
                )

        if not config:
            config = USE_CASE_STUBS.get(use_case)
            if db and config:
                # Still try to merge DB use case config even if prompt is stubbed
                use_case_stmt = select(LlmUseCaseConfigModel).where(
                    LlmUseCaseConfigModel.key == use_case
                )
                try:
                    db_use_case = db.execute(use_case_stmt).scalar_one_or_none()
                    if db_use_case:
                        new_data = config.model_dump()
                        new_data.update({
                            "input_schema": db_use_case.input_schema,
                            "output_schema_id": db_use_case.output_schema_id,
                            "persona_strategy": db_use_case.persona_strategy,
                            "interaction_mode": db_use_case.interaction_mode,
                            "user_question_policy": db_use_case.user_question_policy,
                        })
                        config = UseCaseConfig(**new_data)
                        if "allowed_persona_ids" not in context:
                            context["allowed_persona_ids"] = db_use_case.allowed_persona_ids
                except Exception as e:
                    logger.error("gateway_db_use_case_merge_failed error=%s", str(e))
            logger.warning("gateway_fallback_to_stub use_case=%s", use_case)

        if not config:
            raise UnknownUseCaseError(f"Use case '{use_case}' not found in registry.")

        resolved_model = resolve_model(use_case, fallback_model=config.model)
        if resolved_model != config.model:
            config = config.model_copy(update={"model": resolved_model})
            logger.info(
                "gateway_model_resolved use_case=%s model=%s (override active)", 
                use_case, resolved_model
            )

        config = self._adjust_reasoning_config(config)
        return config

    async def _resolve_persona(
        self, db: Optional[Session], config: UseCaseConfig, context: Dict[str, Any], use_case: str
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Resolves persona and returns (persona_block, persona_id, persona_name)."""
        persona_block = None
        resolved_persona_id = context.get("persona_id")
        persona_name = None
        allowed_ids = context.get("allowed_persona_ids")
        
        logger.debug(
            "gateway_resolve_persona start use_case=%s allowed_ids=%s", 
            use_case, allowed_ids
        )

        if config.persona_strategy == "forbidden":
            return None, None, None

        if db and allowed_ids:
            uuid_ids = []
            for pid in allowed_ids:
                try:
                    if isinstance(pid, str) and pid.startswith("["):
                        # Handle potential double-encoded list
                        import ast
                        actual_list = ast.literal_eval(pid)
                        for apid in actual_list:
                            uuid_ids.append(uuid.UUID(apid))
                    else:
                        uuid_ids.append(uuid.UUID(pid))
                except (ValueError, TypeError, SyntaxError):
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
                        persona_name = resolved_persona.name
                    else:
                        default_persona = None
                        for pid in allowed_ids:
                            if pid in persona_map:
                                default_persona = persona_map[pid]
                                break
                        if default_persona:
                            persona_block = compose_persona_block(default_persona)
                            resolved_persona_id = str(default_persona.id)
                            persona_name = default_persona.name
                        else:
                            resolved_persona_id = None
                else:
                    for pid in allowed_ids:
                        if pid in persona_map:
                            resolved_persona = persona_map[pid]
                            persona_block = compose_persona_block(resolved_persona)
                            resolved_persona_id = pid
                            persona_name = resolved_persona.name
                            break

        if not persona_block and config.persona_strategy == "required":
            raise GatewayConfigError(
                f"No active persona available for required use case '{use_case}'"
            )

        if not persona_block:
            persona_block = context.get("persona_block") or context.get("persona_line")
            persona_name = context.get("persona_name")

        return persona_block, resolved_persona_id, persona_name

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
                    if schema_model.version == 3 or "v3" in schema_name:
                        schema_version = "v3"
                    elif schema_model.version == 2 or "v2" in schema_name:
                        schema_version = "v2"
                    else:
                        schema_version = f"v{schema_model.version}"
            except (ValueError, TypeError):
                logger.error("gateway_invalid_schema_id schema_id=%s", config.output_schema_id)

        if not schema_dict and use_case not in PAID_USE_CASES:
            catalog_entry = PROMPT_CATALOG.get(use_case)
            if catalog_entry and catalog_entry.output_schema:
                schema_dict = catalog_entry.output_schema
                schema_name = re.sub(r"[^a-z0-9_-]", "_", catalog_entry.name.lower())

        is_stub = config.prompt_version_id == "hardcoded-v1"
        is_prod = getattr(settings, "app_env", "development") in {"production", "prod"}
        if use_case in PAID_USE_CASES and not schema_dict and (not is_stub or is_prod):
            raise GatewayConfigError(f"Mandatory output schema missing for '{use_case}'.")

        return schema_dict, schema_name, schema_version

    def _adjust_reasoning_config(self, config: UseCaseConfig) -> UseCaseConfig:
        """Auto-adjusts tokens, timeout, and reasoning_effort for reasoning models."""
        if is_reasoning_model(config.model):
            logger.warning(
                "gateway_adjust_reasoning model=%s effort=%s", 
                config.model, config.reasoning_effort
            )
            updates = {}
            if config.max_output_tokens < 16384:
                updates["max_output_tokens"] = 16384
            if config.timeout_seconds < 180:
                updates["timeout_seconds"] = 180
            if config.reasoning_effort is None:
                updates["reasoning_effort"] = "medium"
            if updates:
                return config.model_copy(update=updates)
        return config

    @staticmethod
    def _legacy_dicts_to_request(
        use_case: str,
        user_input: Dict[str, Any],
        context: Dict[str, Any],
        request_id: str,
        trace_id: str,
        user_id: Optional[int] = None,
        is_repair_call: bool = False,
    ) -> LLMExecutionRequest:
        """Maps legacy dict-based parameters to the canonical LLMExecutionRequest."""
        locale = user_input.get("locale") or context.get("locale") or "fr-FR"
        user_input_model = ExecutionUserInput(
            use_case=use_case,
            locale=locale,
            message=user_input.get("message") or user_input.get("last_user_msg"),
            question=user_input.get("question"),
            situation=user_input.get("situation"),
            conversation_id=user_input.get("conversation_id") or context.get("conversation_id"),
            persona_id_override=user_input.get("persona_id") or context.get("persona_id"),
        )

        history = []
        for m in context.get("history", []):
            if isinstance(m, dict) and "role" in m and "content" in m:
                history.append(ExecutionMessage(**m))

        structuring_keys = {
            "history", "natal_data", "chart_json", "precision_level", "astro_context",
            "locale", "conversation_id", "persona_id", "_visited_use_cases",
            "evidence_catalog", "validation_strict", "_override_prompt_version_id",
        }
        extra_context = {k: v for k, v in context.items() if k not in structuring_keys}

        context_model = ExecutionContext(
            history=history,
            natal_data=context.get("natal_data"),
            chart_json=context.get("chart_json"),
            precision_level=context.get("precision_level"),
            astro_context=context.get("astro_context"),
            extra_context=extra_context,
        )

        flags_model = ExecutionFlags(
            is_repair_call=is_repair_call,
            skip_common_context=context.get("skip_common_context", False),
            test_fallback_active=context.get("test_fallback_active", False),
            validation_strict=context.get("validation_strict", False),
            evidence_catalog=context.get("evidence_catalog"),
            prompt_version_id_override=context.get("_override_prompt_version_id"),
            visited_use_cases=context.get("_visited_use_cases", []),
        )

        return LLMExecutionRequest(
            user_input=user_input_model,
            context=context_model,
            flags=flags_model,
            user_id=user_id,
            request_id=request_id,
            trace_id=trace_id,
        )

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
        """Legacy entry point for LLM orchestration."""
        request = self._legacy_dicts_to_request(
            use_case=use_case,
            user_input=user_input,
            context=context,
            request_id=request_id,
            trace_id=trace_id,
            user_id=user_id,
            is_repair_call=is_repair_call,
        )
        return await self.execute_request(request, db=db)

    # --- PIPELINE STAGES (Story 66.4) ---

    async def _resolve_plan(
        self, request: LLMExecutionRequest, db: Optional[Session], 
        config_override: Optional[UseCaseConfig] = None,
        context_override: Optional[Dict[str, Any]] = None
    ) -> tuple[ResolvedExecutionPlan, Optional[QualifiedContext]]:
        # Stage 1: Orchestrates the resolution of all configuration artifacts into a single plan.
        use_case = request.user_input.use_case
        user_id = request.user_id
        resolved_assembly = None

        # 0. Compatibility fallback for deprecated use cases (Story 66.9 AC5, 66.20)
        is_legacy_compatibility = False
        from app.prompts.catalog import DEPRECATED_USE_CASE_MAPPING
        if use_case in DEPRECATED_USE_CASE_MAPPING and not request.user_input.feature:
            is_legacy_compatibility = True
            mapping = DEPRECATED_USE_CASE_MAPPING[use_case]
            request.user_input.feature = mapping["feature"]
            request.user_input.subfeature = mapping.get("subfeature")
            request.user_input.plan = mapping["plan"]
            logger.warning(
                "DEPRECATION WARNING: Use case '%s' is deprecated. "
                "Please use canonical taxonomy: feature='%s', subfeature='%s', plan='%s'.",
                use_case, mapping["feature"], mapping.get("subfeature"), mapping["plan"]
            )

        # Use provided context_dict or build from request
        if context_override is not None:
            context_dict = context_override
        else:
            context_dict = request.context.model_dump()
            extra = context_dict.pop("extra_context", {})
            context_dict.update(extra)

        # 0. Common context resolution (Story 66.6)
        qualified_ctx = None
        if db and user_id is not None and not request.flags.skip_common_context:
            try:
                period = "daily"
                if "weekly" in use_case or context_dict.get("period") == "weekly":
                    period = "weekly"
                
                qualified_ctx = CommonContextBuilder.build(
                    user_id=user_id, use_case_key=use_case, period=period, db=db
                )
                # Merge into context dict for resolution
                context_dict = {**qualified_ctx.payload.model_dump(), **context_dict}
            except Exception as e:
                logger.warning("gateway_common_context_failed use_case=%s error=%s", use_case, e)

        if config_override:
            config = config_override
            source_base = "config" if config.prompt_version_id != "hardcoded-v1" else "stub"
        else:
            source_base = "config"
            config = None
            if db:
                try:
                    # 0.5 Assembly resolution (Story 66.8 AC10 / D3)
                    registry = AssemblyRegistry(db)
                    
                    assembly_db = None
                    if request.user_input.assembly_config_id:
                        # Absolute priority (D3)
                        assembly_db = await registry.get_config_by_id(
                            request.user_input.assembly_config_id
                        )
                        if not assembly_db:
                            raise GatewayConfigError(
                                f"Assembly config {request.user_input.assembly_config_id} not found"
                            )
                    elif request.user_input.feature:
                        # AssemblyRegistry.get_active_config now handles both sync/async sessions
                        assembly_db = await registry.get_active_config(
                            feature=request.user_input.feature,
                            subfeature=request.user_input.subfeature,
                            plan=request.user_input.plan,
                            locale=request.user_input.locale
                        )

                    # Story 66.20: Enforce mandatory assembly for nominal families
                    CANONICAL_FAMILIES = {"chat", "guidance", "natal", "horoscope_daily"}
                    if (
                        not assembly_db 
                        and not is_legacy_compatibility
                        and request.user_input.feature in CANONICAL_FAMILIES
                    ):
                        raise GatewayConfigError(
                            f"Mandatory assembly missing for nominal {request.user_input.feature} family. "
                            f"Taxonomy: {request.user_input.feature}/{request.user_input.subfeature}/{request.user_input.plan}"
                        )

                    if assembly_db:
                        # Assembly found! Override everything (AC10)
                        resolved_assembly = resolve_assembly(assembly_db)
                        
                        # Map ResolvedAssembly to UseCaseConfig for compatibility with Stage 1.5+
                        config = UseCaseConfig(
                            model=resolved_assembly.execution_config.model,
                            temperature=resolved_assembly.execution_config.temperature or 0.7,
                            max_output_tokens=resolved_assembly.execution_config.max_output_tokens,
                            timeout_seconds=resolved_assembly.execution_config.timeout_seconds,
                            system_core_key="default_v1",  # Hard policy handled later
                            developer_prompt=assemble_developer_prompt(
                                resolved_assembly, assembly_db
                            ),
                            prompt_version_id=str(assembly_db.id),
                            persona_strategy="forbidden",  # Persona already handled in assembly
                            interaction_mode=assembly_db.interaction_mode,
                            user_question_policy=assembly_db.user_question_policy,
                            output_schema_id=resolved_assembly.output_contract_ref,
                            reasoning_effort=resolved_assembly.execution_config.reasoning_effort,
                            verbosity=resolved_assembly.execution_config.verbosity,
                            fallback_use_case=resolved_assembly.execution_config.fallback_use_case,
                        )
                        source_base = "assembly"
                        # CRITICAL FIX: ensure model_id is updated from this config
                        model_id = config.model
                        # We also inject persona_block directly to bypass _resolve_persona
                        persona_block = resolved_assembly.persona_block
                        persona_id = (
                            str(resolved_assembly.persona_ref) 
                            if resolved_assembly.persona_ref else None
                        )
                        persona_name = None 
                        
                        # Store assembly metadata for ResolvedExecutionPlan
                        context_dict["_assembly_resolved"] = resolved_assembly
                        context_dict["_assembly_db_id"] = str(assembly_db.id)
                except GatewayConfigError:
                    raise
                except Exception as e:
                    logger.warning(
                        "gateway_assembly_resolution_failed use_case=%s error=%s", 
                        use_case, e
                    )

            if not config:
                if db:
                    try:
                        config = await self._resolve_config(db, use_case, context_dict)
                        if config.prompt_version_id == "hardcoded-v1":
                            source_base = "stub"
                    except Exception:
                        source_base = "stub"
                
                if not config:
                    config = await self._resolve_config(db, use_case, context_dict)
                    source_base = "stub"
            else:
                # config was set by assembly
                pass

        # 0.7 Execution Profile resolution (Story 66.11)
        profile_db = None
        profile_source = None
        if db:
            try:
                from app.llm_orchestration.services.execution_profile_registry import (
                    ExecutionProfileRegistry,
                )
                
                # 1. Try from assembly if present
                if source_base == "assembly" and context_dict.get("_assembly_db_id"):
                    # We need the actual assembly model to get execution_profile_ref
                    from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
                    stmt = select(PromptAssemblyConfigModel).where(
                        PromptAssemblyConfigModel.id == uuid.UUID(context_dict["_assembly_db_id"])
                    )
                    assembly_model = db.execute(stmt).scalar_one_or_none()
                    if assembly_model and assembly_model.execution_profile_ref:
                        profile_db = ExecutionProfileRegistry.get_profile_by_id(
                            db, assembly_model.execution_profile_ref
                        )
                        if profile_db:
                            profile_source = "assembly_ref"

                # 2. Waterfall resolution (D2)
                if not profile_db and request.user_input.feature:
                    profile_db = ExecutionProfileRegistry.get_active_profile(
                        db,
                        feature=request.user_input.feature,
                        subfeature=request.user_input.subfeature,
                        plan=request.user_input.plan
                    )
                    if profile_db:
                        profile_source = "waterfall"
            except Exception as e:
                logger.warning(
                    "gateway_execution_profile_resolution_failed use_case=%s error=%s", 
                    use_case, e
                )

        # 0.8 Final Model & Provider merge (Story 66.11 D4, D6, 66.18)
        provider = "openai"
        timeout_seconds = config.timeout_seconds
        max_output_tokens = config.max_output_tokens
        max_output_tokens_source = "config"
        translated_params = {}
        verbosity_instruction = ""
        
        if profile_db:
            from app.llm_orchestration.services.provider_parameter_mapper import (
                ProviderParameterMapper,
            )
            
            # Profile overrides config/assembly model
            model_id = profile_db.model
            provider = profile_db.provider
            timeout_seconds = profile_db.timeout_seconds
            
            # Resolve max_output_tokens priority (Story 66.18 D4)
            # 1. Length Budget (highest)
            if (
                resolved_assembly and resolved_assembly.length_budget 
                and resolved_assembly.length_budget.global_max_tokens
            ):
                max_output_tokens = resolved_assembly.length_budget.global_max_tokens
                max_output_tokens_source = "length_budget"
            # 2. Execution Profile
            elif profile_db.max_output_tokens:
                max_output_tokens = profile_db.max_output_tokens
                max_output_tokens_source = "execution_profile"
            # 3. Verbosity default (lowest)
            else:
                verbosity_instruction, rec_tokens = (
                    ProviderParameterMapper.resolve_verbosity_instruction(
                        profile_db.verbosity_profile
                    )
                )
                if rec_tokens:
                    max_output_tokens = rec_tokens
                    max_output_tokens_source = "verbosity_default"
            
            # Map profiles to provider-specific params (Story 66.18)
            try:
                translated_params = ProviderParameterMapper.map(
                    provider=provider,
                    reasoning_profile=profile_db.reasoning_profile,
                    verbosity_profile=profile_db.verbosity_profile,
                    output_mode=profile_db.output_mode,
                    tool_mode=profile_db.tool_mode
                )
            except NotImplementedError as e:
                # High #1 & #2: Fallback if provider/params mapping not implemented
                logger.warning(
                    "gateway_provider_mapping_not_implemented provider=%s error=%s. "
                    "Falling back to resolve_model/openai.", 
                    provider, e
                )
                model_id = resolve_model(use_case, fallback_model=config.model)
                profile_source = "fallback_resolve_model"
                provider = "openai"  # High #2 Fix: Reset to supported provider
                translated_params = {}

            if provider == "anthropic":
                logger.warning(
                    "gateway_provider_not_supported_yet provider=%s model=%s. "
                    "Falling back to resolve_model/openai.",
                    provider,
                    model_id,
                )
                model_id = resolve_model(use_case, fallback_model=config.model)
                profile_source = "fallback_resolve_model"
                provider = "openai"
                translated_params = {}
            
            # If we didn't get verbosity_instruction yet, get it now
            if not verbosity_instruction:
                verbosity_instruction, _ = (
                    ProviderParameterMapper.resolve_verbosity_instruction(
                        profile_db.verbosity_profile
                    )
                )

            logger.info(
                "gateway_execution_profile_applied profile_id=%s source=%s "
                "model=%s provider=%s max_tokens=%s source=%s",
                str(profile_db.id), profile_source, model_id, provider, 
                max_output_tokens, max_output_tokens_source
            )
        else:
            # Legacy/Fallback resolution
            model_id = resolve_model(use_case, fallback_model=config.model)
            profile_source = "fallback_resolve_model"
            
            # Story 66.18 AC6: Compatibility for raw ExecutionConfigAdmin
            if config.reasoning_effort or config.verbosity:
                logger.info(
                    "gateway_legacy_execution_config_used use_case=%s "
                    "reasoning=%s verbosity=%s", 
                    use_case, config.reasoning_effort, config.verbosity
                )
                # We could infer a profile here for telemetry
            
            # For legacy, we still apply LengthBudget if present
            if (
                resolved_assembly and resolved_assembly.length_budget 
                and resolved_assembly.length_budget.global_max_tokens
            ):
                max_output_tokens = resolved_assembly.length_budget.global_max_tokens
                max_output_tokens_source = "length_budget"

        # Apply translated params to config if applicable
        if translated_params:
            if "reasoning_effort" in translated_params:
                config.reasoning_effort = translated_params["reasoning_effort"]
            if "response_format" in translated_params:
                # config doesn't have response_format yet, it's in ResolvedExecutionPlan
                pass

        # Final Stage 1 resolution

        model_source = source_base
        entry = PROMPT_CATALOG.get(use_case)
        if entry and os.environ.get(entry.engine_env_key):
            model_source = "os_granular"
        else:
            safe_uc_key = re.sub(r"[^a-zA-Z0-9_]", "_", use_case).upper()
            if os.environ.get(f"LLM_MODEL_OVERRIDE_{safe_uc_key}"):
                model_source = "os_legacy"

        system_core = get_hard_policy(config.safety_profile)

        if source_base != "assembly":
            if request.user_input.persona_id_override:
                context_dict["persona_id"] = request.user_input.persona_id_override
            
            persona_block, persona_id, persona_name = await self._resolve_persona(
                db, config, context_dict, use_case
            )

        output_schema, schema_name, schema_version = self._resolve_schema(db, config, use_case)

        cq_level = qualified_ctx.context_quality if qualified_ctx else "unknown"
        context_quality_injected = False

        if request.flags.is_repair_call:
            rendered_developer_prompt = (
                "Tu es un assistant technique. Ta seule mission est de corriger le format JSON "
                "d'une réponse précédente pour qu'elle respecte strictement le schéma fourni. "
                "Ne modifie pas le sens profond. Réponds EXCLUSIVEMENT avec le bloc JSON."
            )
        else:
            # STORY 66.14 & 66.18: CANONICAL TRANSFORMATIONS ORDER
            
            # Base prompt from config (already contains blocks if assembly)
            current_prompt = config.developer_prompt
            
            # 1. & 2. context_quality blocks and compensation (handled in order in gateway/renderer)
            if request.user_input.feature:
                from app.llm_orchestration.services.context_quality_injector import (
                    ContextQualityInjector,
                )
                current_prompt, context_quality_injected = ContextQualityInjector.inject(
                    current_prompt,
                    request.user_input.feature,
                    cq_level
                )
            
            # 3. verbosity_profile instruction (Story 66.18 AC1)
            if verbosity_instruction:
                current_prompt = (
                    f"{current_prompt}\n\n[CONSIGNE DE VERBOSITÉ] {verbosity_instruction}"
                )

            # 4. & 5. render placeholders and final validation
            # Initial vars from user_input
            render_vars = request.user_input.model_dump()
            
            # Universal placeholders (Story 66.13 AC6) - set as defaults
            render_vars.setdefault("locale", request.user_input.locale)
            render_vars.setdefault("use_case", use_case)
            render_vars.setdefault("last_user_msg", request.user_input.last_user_msg)
            if request.user_input.question:
                render_vars.setdefault("question", request.user_input.question)
            if request.user_input.situation:
                render_vars.setdefault("situation", request.user_input.situation)

            # Overlay context_dict (priority to context)
            render_vars.update(context_dict)
            
            # Re-apply persona info if resolved
            if persona_block:
                render_vars.setdefault("persona_name", persona_name or persona_id)
                if not render_vars.get("last_user_msg"):
                    render_vars["last_user_msg"] = request.user_input.message

            render_vars["context_quality"] = cq_level # For conditional blocks
            
            rendered_developer_prompt = self.renderer.render(
                current_prompt,
                render_vars,
                required_variables=config.required_prompt_placeholders,
                feature=request.user_input.feature or "unknown"
            )

        interaction_mode = config.interaction_mode
        user_question_policy = config.user_question_policy
        overrides_applied = {}
        if request.overrides:
            if request.overrides.interaction_mode:
                interaction_mode = request.overrides.interaction_mode
                overrides_applied["interaction_mode"] = interaction_mode
            if request.overrides.user_question_policy:
                user_question_policy = request.overrides.user_question_policy
                overrides_applied["user_question_policy"] = user_question_policy

        response_format = None
        if output_schema:
            response_format = ResponseFormatConfig(type="json_schema", schema=output_schema)
        elif translated_params.get("response_format"):
            translated_response_format = translated_params["response_format"]
            response_format = ResponseFormatConfig(type=translated_response_format["type"])

        # Build plan with assembly metadata (AC10)
        assembly_id = context_dict.get("_assembly_db_id")
        resolved_assembly: Optional[ResolvedAssembly] = context_dict.get("_assembly_resolved")

        plan = ResolvedExecutionPlan(
            assembly_id=assembly_id,
            feature=request.user_input.feature,
            subfeature=request.user_input.subfeature,
            plan=request.user_input.plan,
            feature_template_id=(
                str(resolved_assembly.feature_template_id) if resolved_assembly else None
            ),
            subfeature_template_id=(
                str(resolved_assembly.subfeature_template_id) 
                if resolved_assembly and resolved_assembly.subfeature_template_id else None
            ),
            template_source=resolved_assembly.template_source if resolved_assembly else None,
            model_id=model_id,
            model_source=model_source,
            model_override_active=model_source in ["os_granular", "os_legacy"],
            execution_profile_id=str(profile_db.id) if profile_db else None,
            execution_profile_source=profile_source,
            reasoning_profile=profile_db.reasoning_profile if profile_db else None,
            verbosity_profile=profile_db.verbosity_profile if profile_db else None,
            output_mode=profile_db.output_mode if profile_db else None,
            tool_mode=profile_db.tool_mode if profile_db else None,
            provider=provider,
            translated_provider_params=translated_params,
            timeout_seconds=timeout_seconds,
            prompt_version_id=config.prompt_version_id,
            rendered_developer_prompt=rendered_developer_prompt,
            system_core=system_core,
            persona_id=persona_id,
            persona_name=persona_name,
            persona_block=persona_block,
            output_schema_id=config.output_schema_id,
            output_schema=output_schema,
            output_schema_version=schema_version,
            input_schema=config.input_schema,
            interaction_mode=interaction_mode,
            user_question_policy=user_question_policy,
            overrides_applied=overrides_applied,
            temperature=config.temperature,
            max_output_tokens=max_output_tokens,
            max_output_tokens_source=max_output_tokens_source,
            response_format=response_format,
            reasoning_effort=config.reasoning_effort,
            verbosity=config.verbosity,
            context_quality=cq_level,
            context_quality_instruction_injected=context_quality_injected
        )
        return plan, qualified_ctx

    def _build_messages(
        self, 
        request: LLMExecutionRequest, 
        plan: ResolvedExecutionPlan, 
        qualified_ctx: Optional[QualifiedContext]
    ) -> ComposedMessages:
        """Stage 2: Composes the final message list for the LLM."""
        use_case = request.user_input.use_case
        user_input_dict = request.user_input.model_dump()
        context_dict = request.context.model_dump()
        extra = context_dict.pop("extra_context", {})
        context_dict.update(extra)
        
        # Merge qualified context payload if present
        if qualified_ctx:
            context_dict.update(qualified_ctx.payload.model_dump())

        user_data_block = extra.get("user_data_block")
        if not user_data_block:
            if extra.get("chat_turn_stage") == "opening":
                from app.services.ai_engine_adapter import build_opening_chat_user_data_block

                user_data_block = build_opening_chat_user_data_block(
                    last_user_msg=request.user_input.message or "",
                    context=context_dict,
                )
            else:
                user_data_block = self.build_user_payload(
                    use_case=use_case,
                    user_input=user_input_dict,
                    context=context_dict,
                    policy=plan.user_question_policy,
                    locale=request.user_input.locale,
                    chart_json_in_prompt="{{chart_json}}" in plan.rendered_developer_prompt,
                )

        if plan.interaction_mode == "chat":
            return self.compose_chat_messages(
                system_core=plan.system_core,
                dev_prompt=plan.rendered_developer_prompt,
                persona_block=plan.persona_block,
                history=[m.model_dump() for m in request.context.history],
                user_payload=user_data_block,
                locale=request.user_input.locale,
            )
        else:
            return self.compose_structured_messages(
                system_core=plan.system_core,
                dev_prompt=plan.rendered_developer_prompt,
                persona_block=plan.persona_block,
                user_payload=user_data_block,
            )

    async def _call_provider(
        self, 
        messages: ComposedMessages, 
        plan: ResolvedExecutionPlan, 
        request: LLMExecutionRequest
    ) -> GatewayResult:
        """Stage 3: Executes the actual call to the LLM provider."""
        # Story 66.18: Resolve final response_format (High 2 fix)
        # 1. Start with profile-translated params (can force JSON even without schema)
        response_format = plan.translated_provider_params.get("response_format")
        
        # 2. If plan has an explicit output_schema, it takes precedence for Structured Outputs
        if plan.response_format and plan.response_format.type == "json_schema":
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": request.user_input.use_case,
                    "schema": plan.response_format.json_schema,
                    "strict": True,
                },
            }
        elif plan.response_format and plan.response_format.type == "json_object":
            response_format = {"type": "json_object"}

        # High #1 Fix: Provider routing
        if plan.provider == "openai":
            return await self.client.execute(
                messages=messages,
                model=plan.model_id,
                temperature=plan.temperature,
                max_output_tokens=plan.max_output_tokens,
                request_id=request.request_id,
                trace_id=request.trace_id,
                use_case=request.user_input.use_case,
                reasoning_effort=plan.reasoning_effort,
                verbosity=plan.verbosity,
                response_format=response_format,
            )
        
        raise ValueError(f"Unsupported provider: {plan.provider}")

    def _validate_and_normalize(
        self, raw_output: str, plan: ResolvedExecutionPlan, request: LLMExecutionRequest
    ) -> ValidationResult:
        """Stage 4: Validates the LLM output against the resolved schema."""
        if not plan.output_schema:
            return ValidationResult(valid=True, parsed=None, errors=[])

        return validate_output(
            raw_output,
            plan.output_schema,
            evidence_catalog=request.flags.evidence_catalog,
            strict=request.flags.validation_strict,
            use_case=request.user_input.use_case,
            schema_version=plan.output_schema_version,
        )

    async def _handle_repair_or_fallback(
        self,
        validation_result: ValidationResult,
        request: LLMExecutionRequest,
        plan: ResolvedExecutionPlan,
        provider_result: GatewayResult,
        db: Optional[Session] = None,
    ) -> RecoveryResult:
        """Stage 5: Orchestrates repair calls or use case fallbacks on validation failure."""
        use_case = request.user_input.use_case
        is_repair_call = request.flags.is_repair_call

        if not validation_result.valid and not is_repair_call:
            logger.warning(
                "gateway_step:repair_invoked use_case=%s errors=%s", 
                use_case, validation_result.errors
            )
            increment_counter(
                "llm_repair_invoked_total",
                labels={"use_case": use_case, "schema_version": plan.output_schema_version},
            )
            if use_case.startswith("natal"):
                increment_counter(
                    "natal_repair_total",
                    labels={"use_case": use_case, "schema_version": plan.output_schema_version},
                )

            repair_prompt = build_repair_prompt(
                provider_result.raw_output, validation_result.errors, plan.output_schema
            )
            repair_request = request.model_copy(deep=True)
            repair_request.flags.is_repair_call = True
            repair_request.flags.visited_use_cases = request.flags.visited_use_cases + [use_case]
            repair_request.context.extra_context["user_data_block"] = repair_prompt

            try:
                repair_result = await self.execute_request(repair_request, db=db)
                return RecoveryResult(result=repair_result, repair_attempts=1, fallback_reason=None)
            except Exception as e:
                logger.warning("gateway_repair_failed use_case=%s error=%s", use_case, str(e))

        context_dict = request.context.model_dump()
        extra = context_dict.pop("extra_context", {})
        context_dict.update(extra)
        config = await self._resolve_config(db, use_case, context_dict)

        if not validation_result.valid and config.fallback_use_case:
            logger.warning(
                "gateway_step:fallback_invoked use_case=%s fallback=%s", 
                use_case, config.fallback_use_case
            )
            increment_counter(
                "llm_fallback_invoked_total",
                labels={"use_case": use_case, "schema_version": plan.output_schema_version},
            )
            fallback_request = request.model_copy(deep=True)
            fallback_request.user_input.use_case = config.fallback_use_case
            fallback_request.flags.visited_use_cases = request.flags.visited_use_cases + [use_case]
            fallback_request.request_id = f"{request.request_id}-fallback"

            fallback_result = await self.execute_request(fallback_request, db=db)
            return RecoveryResult(
                result=fallback_result,
                repair_attempts=0,
                fallback_reason=(
                    str(validation_result.errors[0]) 
                    if validation_result.errors else "validation_failed"
                )
            )

        if not validation_result.valid:
            if is_repair_call and use_case.startswith("natal"):
                increment_counter(
                    "natal_repair_fail_total",
                    labels={"use_case": use_case, "schema_version": plan.output_schema_version},
                )
            raise OutputValidationError(
                f"Output validation failed for '{use_case}'", 
                details={"errors": validation_result.errors}
            )

        return RecoveryResult(result=provider_result)

    def _build_result(
        self,
        validation_result: ValidationResult,
        plan: ResolvedExecutionPlan,
        recovery: RecoveryResult,
        latency_ms: int,
        request: LLMExecutionRequest,
        qualified_ctx: Optional[QualifiedContext] = None
    ) -> GatewayResult:
        """Stage 6: Finalizes the GatewayResult with unified metadata."""
        result = recovery.result
        # The request is passed as an argument
        
        # Telemetry Axis 1: Execution Path
        if request.flags.test_fallback_active:
            execution_path = "test_fallback"
        elif recovery.fallback_reason:
            execution_path = "fallback_use_case"
        elif recovery.repair_attempts > 0:
            execution_path = "repaired"
        else:
            # Check if inner result already has an execution path (from recursion)
            execution_path = getattr(result.meta, "execution_path", "nominal")
            if execution_path == "unknown":
                execution_path = "nominal"

        # Telemetry Axis 2: Context Quality
        context_quality = plan.context_quality
        missing_context_fields = qualified_ctx.missing_fields if qualified_ctx else []

        # Telemetry Axis 3: Normalizations
        normalizations = validation_result.normalizations_applied

        # Update metadata
        result.meta.execution_path = execution_path
        result.meta.context_quality = context_quality
        result.meta.missing_context_fields = missing_context_fields
        result.meta.normalizations_applied = normalizations
        
        # Increment if recursion occurred, or take from recovery
        result.meta.repair_attempts = max(
            getattr(result.meta, "repair_attempts", 0), recovery.repair_attempts
        )
        if recovery.fallback_reason:
            result.meta.fallback_reason = recovery.fallback_reason
        
        # Synchronize legacy booleans (AC7)
        result.meta.repair_attempted = (result.meta.repair_attempts > 0)
        result.meta.fallback_triggered = (result.meta.fallback_reason is not None)

        if recovery.repair_attempts > 0:
             if result.meta.validation_status in ["valid", "repair_success"]:
                 result.meta.validation_status = "repair_success"
        elif recovery.fallback_reason:
             result.meta.validation_status = "fallback"
        elif not validation_result.valid:
             result.meta.validation_status = "error"
             result.meta.validation_errors = validation_result.errors
        else:
             result.meta.validation_status = "valid"

        # Preserve other technical metadata
        result.meta.latency_ms = latency_ms
        result.meta.model = plan.model_id
        result.meta.model_override_active = plan.model_override_active
        result.meta.prompt_version_id = plan.prompt_version_id or "hardcoded-v1"
        
        # Map Assembly metadata (AC10)
        result.meta.assembly_id = plan.assembly_id
        result.meta.feature = plan.feature
        result.meta.subfeature = plan.subfeature
        result.meta.plan = plan.plan
        result.meta.template_source = plan.template_source

        result.meta.persona_id = plan.persona_id
        result.meta.output_schema_id = plan.output_schema_id
        result.meta.schema_version = plan.output_schema_version
        
        # Map Execution Profile metadata (Story 66.11 AC10)
        result.meta.execution_profile_id = plan.execution_profile_id
        result.meta.execution_profile_source = plan.execution_profile_source
        result.meta.max_output_tokens_source = plan.max_output_tokens_source
        result.meta.reasoning_profile = plan.reasoning_profile
        result.meta.verbosity_profile = plan.verbosity_profile
        result.meta.output_mode = plan.output_mode
        result.meta.tool_mode = plan.tool_mode
        result.meta.provider = plan.provider
        result.meta.translated_provider_params = plan.translated_provider_params

        return result

    def _validate_input(self, config: UseCaseConfig, user_input: Dict[str, Any]) -> None:
        """Helper to validate user input against UseCaseConfig.input_schema."""
        logger.debug(
            "gateway_validate_input use_case=%s has_schema=%s", 
            getattr(config, "use_case", "unknown"), config.input_schema is not None
        )
        if config.input_schema:
            try:
                res = validate_input(user_input, config.input_schema)
                if not res.valid:
                    error_msg = "; ".join(res.errors)
                    logger.warning("gateway_input_validation_failed error=%s", error_msg)
                    raise InputValidationError(f"Input validation failed: {error_msg}")
            except InputValidationError:
                raise
            except Exception as e:
                logger.error("gateway_input_validation_unexpected_error error=%s", str(e))
                raise InputValidationError(f"Input validation failed (unexpected): {str(e)}") from e

    async def execute_request(
        self, request: LLMExecutionRequest, db: Optional[Session] = None
    ) -> GatewayResult:
        """Canonical entry point for LLM orchestration using typed contracts."""
        start_time = time.perf_counter()
        use_case = request.user_input.use_case
        user_input_dict = request.user_input.model_dump()
        visited = request.flags.visited_use_cases
        is_repair_call = request.flags.is_repair_call

        try:
            if use_case in visited and not is_repair_call:
                raise GatewayError(
                    f"Infinite fallback loop detected for use case '{use_case}'", 
                    details={"visited": visited}
                )

            if len(visited) > 3:
                raise GatewayError(
                    f"Fallback chain depth limit exceeded for '{use_case}'", 
                    details={"visited": visited}
                )

            # 0. Merge extra_context for preliminary resolution
            context_dict = request.context.model_dump()
            extra = context_dict.pop("extra_context", {})
            context_dict.update(extra)

            # Stage 0.5: Fast Validate Input (Story 66.4 AC8)
            # We need config before the full Stage 1 (which includes prompt rendering)
            # to fail fast if the user input is invalid.
            # We must use context_dict here to ensure correct resolution (e.g. overrides)
            config = await self._resolve_config(db, use_case, context_dict)
            self._validate_input(config, user_input_dict)

            # Stage 1: Resolve Plan (Now includes QualifiedContext)
            try:
                plan, qualified_ctx = await self._resolve_plan(
                    request, db, config_override=None, context_override=context_dict
                )
                # If assembly was used, config is within plan. We need to sync back to 'config' 
                # variable for Stage 1.5 validation if it depends on the exact model resolved.
                if plan.model_source == "assembly":
                    # Re-map config from plan for validation
                    config = UseCaseConfig(
                        model=plan.model_id,
                        temperature=plan.temperature,
                        max_output_tokens=plan.max_output_tokens,
                        developer_prompt=plan.rendered_developer_prompt,
                        output_schema_id=plan.output_schema_id,
                        input_schema=plan.input_schema,
                        interaction_mode=plan.interaction_mode,
                        user_question_policy=plan.user_question_policy,
                    )
            except Exception as e:
                logger.error("gateway_step_failed:resolve_plan use_case=%s error=%s", use_case, e)
                raise

            # Stage 1.5: Validate Input (Story 66.4 AC8)
            try:
                # We use the config just resolved
                self._validate_input(config, user_input_dict)
            except InputValidationError:
                raise
            except Exception as e:
                logger.error("gateway_step_failed:validate_input use_case=%s error=%s", use_case, e)
                raise

            if not is_repair_call:
                logger.info(
                    "llm_gateway_start use_case=%s request_id=%s", 
                    use_case, request.request_id
                )

            # Stage 2: Build Messages
            try:
                messages = self._build_messages(request, plan, qualified_ctx)
            except Exception as e:
                logger.error("gateway_step_failed:build_messages use_case=%s error=%s", use_case, e)
                raise

            # Stage 3: Call Provider
            try:
                provider_result = await self._call_provider(messages, plan, request)
            except Exception as e:
                logger.error("gateway_step_failed:call_provider use_case=%s error=%s", use_case, e)
                raise

            # Stage 4: Validate & Normalize
            try:
                validation = self._validate_and_normalize(provider_result.raw_output, plan, request)
                if validation.valid:
                    provider_result.structured_output = validation.parsed
            except Exception as e:
                logger.error(
                    "gateway_step_failed:validate_and_normalize use_case=%s error=%s", 
                    use_case, e
                )
                raise

            # Stage 5: Recovery (Repair/Fallback)
            try:
                if not validation.valid:
                    recovery = await self._handle_repair_or_fallback(
                        validation, request, plan, provider_result, db=db
                    )
                else:
                    recovery = RecoveryResult(result=provider_result)
            except Exception as e:
                logger.error("gateway_step_failed:recovery use_case=%s error=%s", use_case, e)
                raise

            latency_ms = int((time.perf_counter() - start_time) * 1000)
            # Stage 6: Build Final Result
            try:
                final_result = self._build_result(
                    validation, plan, recovery, latency_ms,
                    request, qualified_ctx
                )
            except Exception as e:
                logger.error("gateway_step_failed:build_result use_case=%s error=%s", use_case, e)
                raise

            if db and not is_repair_call:
                await log_call(
                    db=db, 
                    use_case=use_case, 
                    request_id=request.request_id, 
                    trace_id=request.trace_id, 
                    user_input=request.user_input.model_dump(), 
                    result=final_result
                )
                increment_counter(
                    "llm_gateway_requests_total", 
                    labels={"use_case": use_case, "status": "success"}
                )

            return final_result

        except Exception as e:
            if db and not is_repair_call:
                await log_call(
                    db=db, 
                    use_case=use_case, 
                    request_id=request.request_id, 
                    trace_id=request.trace_id, 
                    user_input=request.user_input.model_dump(), 
                    result=None, 
                    error=e
                )
            raise
