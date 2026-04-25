"""Gère la génération applicative des guidances LLM quotidiennes, hebdomadaires et contextuelles."""

from __future__ import annotations

import asyncio
import logging
import random
import re
from datetime import datetime
from time import monotonic
from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.datetime_provider import datetime_provider
from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.adapter_errors import AIEngineAdapterError, map_adapter_error_to_codes
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.current_context import build_current_prompt_context
from app.services.entitlement.entitlement_types import QuotaDefinition
from app.services.llm_generation.anonymization_service import anonymize_text
from app.services.llm_generation.llm_token_usage_service import LlmTokenUsageService
from app.services.llm_generation.off_scope_policy import assess_off_scope
from app.services.llm_generation.shared.contextual_text import (
    compose_structured_guidance_full_text,
    normalize_structured_string_list,
)
from app.services.llm_generation.shared.natal_context import (
    build_user_natal_chart_summary_context,
    detect_degraded_natal_mode,
)
from app.services.persona_config_service import PersonaConfigService
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)


class GuidanceServiceError(Exception):
    """Exception raised by the guidance service."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialize a guidance error.

        Args:
            code: Unique error code.
            message: Descriptive error message.
            details: Optional dictionary of additional details.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class GuidanceData(BaseModel):
    """Data for a periodic guidance (daily or weekly)."""

    period: str
    summary: str
    key_points: list[str]
    actionable_advice: list[str]
    disclaimer: str
    attempts: int
    fallback_used: bool
    recovery: "GuidanceRecoveryMetadata"
    context_message_count: int
    generated_at: datetime


class ContextualGuidanceData(BaseModel):
    """Data for a contextual guidance based on a specific situation."""

    guidance_type: str
    situation: str
    objective: str
    time_horizon: str | None
    summary: str
    full_text: str
    key_points: list[str]
    actionable_advice: list[str]
    disclaimer: str
    attempts: int
    fallback_used: bool
    recovery: "GuidanceRecoveryMetadata"
    context_message_count: int
    generated_at: datetime


class GuidanceRecoveryMetadata(BaseModel):
    """Metadata about off-scope recovery attempts."""

    off_scope_detected: bool
    off_scope_score: float
    recovery_strategy: str
    recovery_applied: bool
    recovery_attempts: int
    recovery_reason: str | None


class GuidanceService:
    """
    Service de génération de guidances astrologiques.

    Génère des guidances périodiques et contextuelles en utilisant le profil
    natal de l'utilisateur, avec gestion des récupérations hors-scope.
    """

    logger = logging.getLogger(__name__)
    SAFE_FALLBACK_MESSAGE = (
        "Je prefere reformuler prudemment cette guidance. "
        "Pouvez-vous preciser l enjeu principal et l horizon temporel ?"
    )
    _markdown_heading_pattern = re.compile(r"^#{1,6}\s*")
    _markdown_bullet_pattern = re.compile(r"^\s*[-*•]\s+")
    _markdown_numbered_pattern = re.compile(r"^\s*\d+[\).\s]+")
    _markdown_bold_pattern = re.compile(r"\*\*(?P<text>[^*]+)\*\*")

    @staticmethod
    def _compose_structured_guidance_full_text(
        summary_raw: str,
        key_points: list[str],
        advice: list[str],
    ) -> str:
        """Delegue au formateur partage des guidances structurees."""
        return compose_structured_guidance_full_text(summary_raw, key_points, advice)

    @staticmethod
    def _normalize_structured_string_list(raw_value: Any) -> list[str]:
        """Delegue au normaliseur partage des listes structurees LLM."""
        return normalize_structured_string_list(raw_value)

    @staticmethod
    def _detect_degraded_natal_mode(
        *,
        birth_time: str | None,
        birth_place: str | None,
    ) -> str | None:
        """Delegue au helper partage de mode degrade natal."""
        return detect_degraded_natal_mode(
            birth_time=birth_time,
            birth_place=birth_place,
        )

    @staticmethod
    def build_natal_chart_summary_context(
        db: Session,
        *,
        user_id: int,
        birth_date: str,
        birth_time: str | None,
        birth_place: str | None,
    ) -> str | None:
        """Construit le resume natal partage en conservant le contrat du service."""
        return build_user_natal_chart_summary_context(
            db,
            user_id=user_id,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            warning_event="guidance_natal_chart_context_unavailable",
        )

    @staticmethod
    async def _sleep_before_retry_async(*, attempts: int, max_attempts: int) -> None:
        """Apply exponential backoff with jitter before retry (async)."""
        if attempts >= max_attempts:
            return
        base_seconds = max(0.0, settings.chat_llm_retry_backoff_seconds)
        max_seconds = max(base_seconds, settings.chat_llm_retry_backoff_max_seconds)
        jitter_seconds = max(0.0, settings.chat_llm_retry_jitter_seconds)
        if base_seconds <= 0 and jitter_seconds <= 0:
            return
        delay_seconds = min(max_seconds, base_seconds * (2 ** (attempts - 1)))
        if jitter_seconds > 0:
            delay_seconds += random.uniform(0.0, jitter_seconds)
        delay_seconds = max(0.0, min(delay_seconds, max_seconds))
        if delay_seconds <= 0:
            return
        observe_duration("guidance_retry_backoff_seconds", delay_seconds)
        increment_counter("guidance_retry_backoff_total", 1.0)
        await asyncio.sleep(delay_seconds)

    @staticmethod
    def _validate_period(period: str) -> str:
        """Validate and normalize the guidance period."""
        normalized = period.strip().lower()
        if normalized not in {"daily", "weekly"}:
            raise GuidanceServiceError(
                code="invalid_guidance_period",
                message="guidance period is invalid",
                details={"supported_periods": "daily,weekly"},
            )
        return normalized

    @staticmethod
    def _select_context_lines(
        repo: ChatRepository,
        conversation_id: int | None,
    ) -> tuple[list[str], int]:
        """Select context lines from conversation history."""
        if conversation_id is None:
            return ["no conversation context"], 0

        recent_messages = repo.get_recent_messages(conversation_id, 6)
        if not recent_messages:
            return ["no conversation context"], 0

        max_characters = max(1, settings.chat_context_max_characters // 2)
        selected: list[str] = []
        total_chars = 0
        selected_count = 0
        for message in reversed(recent_messages):
            content = anonymize_text(message.content.strip())
            line = f"{message.role}: {content}"
            line_chars = len(line)
            if selected and total_chars + line_chars > max_characters:
                break
            if not selected and line_chars > max_characters:
                line = line[:max_characters]
                line_chars = len(line)
            selected.append(line)
            total_chars += line_chars
            selected_count += 1

        selected.reverse()
        return selected or ["no conversation context"], selected_count

    @staticmethod
    def _resolve_conversation_id(
        repo: ChatRepository,
        user_id: int,
        conversation_id: int | None,
    ) -> int | None:
        """
        Resolve and validate conversation ID for guidance context.

        Args:
            repo: Chat repository instance.
            user_id: User identifier for ownership validation.
            conversation_id: Optional conversation ID to validate.

        Returns:
            Resolved conversation ID or None if no conversation context.

        Raises:
            GuidanceServiceError: If conversation not found or forbidden.
        """
        if conversation_id is not None:
            selected_conversation = repo.get_conversation_by_id(conversation_id)
            if selected_conversation is None:
                raise GuidanceServiceError(
                    code="conversation_not_found",
                    message="conversation was not found",
                    details={"conversation_id": str(conversation_id)},
                )
            if selected_conversation.user_id != user_id:
                raise GuidanceServiceError(
                    code="conversation_forbidden",
                    message="conversation does not belong to user",
                    details={"conversation_id": str(conversation_id)},
                )
            return selected_conversation.id
        latest_conversation = repo.get_latest_active_conversation_by_user_id(user_id)
        return latest_conversation.id if latest_conversation else None

    @staticmethod
    def _normalize_summary(generated_text: str, period: str) -> str:
        """Normalize generated summary by filtering prompt artifacts."""
        raw_summary = generated_text.strip()
        # Local stub echoes the full prompt; never expose internal prompt/context to end users.
        if "[guidance_prompt_version:" in raw_summary or "Recent context:" in raw_summary:
            if period == "daily":
                return (
                    "Votre guidance du jour met l accent sur la clarte des priorites "
                    "et des decisions progressives."
                )
            return (
                "Votre guidance de la semaine invite a structurer vos actions "
                "et a avancer par etapes."
            )
        return raw_summary[:500]

    @staticmethod
    def _normalize_contextual_summary(generated_text: str) -> str:
        """Normalize contextual summary by filtering prompt artifacts."""
        raw_summary = generated_text.strip()
        # Local stub echoes the full prompt; never expose internal prompt/context to end users.
        if "[guidance_prompt_version:" in raw_summary or "Recent context:" in raw_summary:
            return (
                "Votre guidance contextuelle met l accent sur des actions concretes, "
                "prudemment alignees avec votre situation."
            )
        lines = [line.strip() for line in raw_summary.splitlines()]
        paragraph_lines: list[str] = []
        for line in lines:
            if not line:
                if paragraph_lines:
                    break
                continue
            if GuidanceService._markdown_heading_pattern.match(line):
                if paragraph_lines:
                    break
                continue

            cleaned = GuidanceService._markdown_bold_pattern.sub(
                lambda match: match.group("text").strip(),
                line,
            )
            cleaned = GuidanceService._markdown_bullet_pattern.sub("", cleaned)
            cleaned = GuidanceService._markdown_numbered_pattern.sub("", cleaned)
            cleaned = re.sub(r"\s+", " ", cleaned).strip(" :-")
            if not cleaned:
                continue
            paragraph_lines.append(cleaned)
            if len(" ".join(paragraph_lines)) >= 600:
                break

        if not paragraph_lines:
            return raw_summary[:500]

        summary = " ".join(paragraph_lines).strip()
        sentence_endings = [summary.rfind(marker) for marker in (". ", "! ", "? ")]
        last_sentence_end = max(sentence_endings)
        if 80 <= last_sentence_end < len(summary) - 1:
            summary = summary[: last_sentence_end + 1].strip()
        return summary[:600].strip()

    @staticmethod
    def _validate_contextual_input(
        situation: str,
        objective: str,
        time_horizon: str | None,
    ) -> tuple[str, str, str | None]:
        """Validate and normalize contextual guidance inputs."""
        normalized_situation = situation.strip()
        normalized_objective = objective.strip()
        normalized_horizon = time_horizon.strip() if time_horizon else None
        if normalized_horizon == "":
            normalized_horizon = None
        if not normalized_situation or not normalized_objective:
            raise GuidanceServiceError(
                code="invalid_guidance_context",
                message="contextual guidance input is invalid",
                details={"required_fields": "situation,objective"},
            )
        return normalized_situation, normalized_objective, normalized_horizon

    @staticmethod
    def _assess_off_scope(content: str) -> tuple[bool, float, str | None]:
        """Assess if a response is off-scope with a confidence score."""
        return assess_off_scope(content)

    @staticmethod
    async def _apply_off_scope_recovery_async(
        *,
        db: Session,
        use_case: str,
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        assistant_content: str,
        persona_profile_code: str,
        entitlement_result: Any = None,
    ) -> tuple[str, bool, GuidanceRecoveryMetadata]:
        """Applique les stratégies de récupération si la guidance est hors-scope (async)."""
        off_scope_detected, off_scope_score, off_scope_reason = GuidanceService._assess_off_scope(
            assistant_content
        )
        if not off_scope_detected:
            return (
                assistant_content,
                False,
                GuidanceRecoveryMetadata(
                    off_scope_detected=False,
                    off_scope_score=0.0,
                    recovery_strategy="none",
                    recovery_applied=False,
                    recovery_attempts=0,
                    recovery_reason=None,
                ),
            )

        increment_counter("guidance_out_of_scope_total", 1.0)
        increment_counter(
            f"guidance_out_of_scope_total|persona_profile={persona_profile_code}",
            1.0,
        )
        GuidanceService.logger.warning(
            "guidance_off_scope_detected strategy=reformulate reason=%s score=%.2f",
            off_scope_reason or "unknown",
            off_scope_score,
        )

        recovery_attempts = 0
        try:
            recovery_attempts += 1
            result = await AIEngineAdapter.generate_guidance(
                use_case=use_case,
                context=context,
                user_id=user_id,
                request_id=f"{request_id}-recovery-1",
                trace_id=trace_id,
                db=db,
            )
            GuidanceService._record_tokens(
                db,
                user_id=user_id,
                feature_code="thematic_consultation",
                gateway_result=result,
                entitlement_result=entitlement_result,
            )
            reformulated = result.raw_output
            reformulate_off_scope, _, _ = GuidanceService._assess_off_scope(reformulated)
            if not reformulate_off_scope:
                increment_counter("guidance_recovery_success_total", 1.0)
                increment_counter(
                    f"guidance_recovery_success_total|persona_profile={persona_profile_code}",
                    1.0,
                )
                GuidanceService.logger.info(
                    "guidance_recovery_applied strategy=reformulate success=true"
                )
                return (
                    reformulated,
                    False,
                    GuidanceRecoveryMetadata(
                        off_scope_detected=True,
                        off_scope_score=off_scope_score,
                        recovery_strategy="reformulate",
                        recovery_applied=True,
                        recovery_attempts=recovery_attempts,
                        recovery_reason=off_scope_reason,
                    ),
                )
        except (TimeoutError, ConnectionError, AIEngineAdapterError):
            GuidanceService.logger.warning("guidance_recovery_error strategy=reformulate")

        try:
            recovery_attempts += 1
            result = await AIEngineAdapter.generate_guidance(
                use_case=use_case,
                context=context,
                user_id=user_id,
                request_id=f"{request_id}-recovery-2",
                trace_id=trace_id,
                db=db,
            )
            GuidanceService._record_tokens(
                db,
                user_id=user_id,
                feature_code="thematic_consultation",
                gateway_result=result,
                entitlement_result=entitlement_result,
            )
            retried = result.raw_output
            retry_off_scope, _, _ = GuidanceService._assess_off_scope(retried)
            if not retry_off_scope:
                increment_counter("guidance_recovery_success_total", 1.0)
                increment_counter(
                    f"guidance_recovery_success_total|persona_profile={persona_profile_code}",
                    1.0,
                )
                GuidanceService.logger.info(
                    "guidance_recovery_applied strategy=retry_once success=true"
                )
                return (
                    retried,
                    False,
                    GuidanceRecoveryMetadata(
                        off_scope_detected=True,
                        off_scope_score=off_scope_score,
                        recovery_strategy="retry_once",
                        recovery_applied=True,
                        recovery_attempts=recovery_attempts,
                        recovery_reason=off_scope_reason,
                    ),
                )
        except (TimeoutError, ConnectionError, AIEngineAdapterError):
            GuidanceService.logger.warning("guidance_recovery_error strategy=retry_once")

        GuidanceService.logger.info("guidance_recovery_applied strategy=safe_fallback success=true")
        return (
            GuidanceService.SAFE_FALLBACK_MESSAGE,
            True,
            GuidanceRecoveryMetadata(
                off_scope_detected=True,
                off_scope_score=off_scope_score,
                recovery_strategy="safe_fallback",
                recovery_applied=True,
                recovery_attempts=recovery_attempts,
                recovery_reason=off_scope_reason,
            ),
        )

    @staticmethod
    def _record_tokens(
        db: Session,
        *,
        user_id: int,
        feature_code: str,
        gateway_result: Any,
        entitlement_result: Any = None,
    ) -> None:
        """
        Enregistre l'usage des tokens de manière atomique.
        L'exception est propagée pour annuler la transaction en cas d'échec.
        """
        quota_defs: list[QuotaDefinition] = []
        if (
            entitlement_result
            and hasattr(entitlement_result, "usage_states")
            and entitlement_result.usage_states
        ):
            token_states = sorted(
                (state for state in entitlement_result.usage_states if state.quota_key == "tokens"),
                key=lambda state: (state.period_unit, state.period_value, state.quota_limit),
            )
            quota_defs = [
                QuotaDefinition(
                    quota_key=token_state.quota_key,
                    quota_limit=token_state.quota_limit,
                    period_unit=token_state.period_unit,
                    period_value=token_state.period_value,
                    reset_mode=token_state.reset_mode,
                )
                for token_state in token_states
            ]

        LlmTokenUsageService.record_usage(
            db,
            user_id=user_id,
            feature_code=feature_code,
            quotas=quota_defs,
            provider_model=gateway_result.meta.model,
            tokens_in=gateway_result.usage.input_tokens,
            tokens_out=gateway_result.usage.output_tokens,
            request_id=gateway_result.request_id,
        )

    @staticmethod
    def request_guidance(
        db: Session,
        *,
        user_id: int,
        period: str,
        conversation_id: int | None = None,
        request_id: str = "n/a",
    ) -> GuidanceData:
        """
        Génère une guidance périodique (quotidienne ou hebdomadaire).

        Cette méthode synchrone est un wrapper autour de request_guidance_async.
        Note: Utilise asyncio.run() pour les tests unitaires synchrones.
        Les endpoints FastAPI utilisent directement request_guidance_async.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            period: Période de guidance ("daily" ou "weekly").
            conversation_id: ID de conversation pour le contexte (optionnel).
            request_id: Identifiant de requête pour le logging.

        Returns:
            Guidance générée avec résumé et conseils.

        Raises:
            GuidanceServiceError: Si le profil natal manque ou en cas d'erreur LLM.
        """
        return asyncio.run(
            GuidanceService.request_guidance_async(
                db,
                user_id=user_id,
                period=period,
                conversation_id=conversation_id,
                request_id=request_id,
            )
        )

    @staticmethod
    async def request_guidance_async(
        db: Session,
        *,
        user_id: int,
        period: str,
        conversation_id: int | None = None,
        request_id: str = "n/a",
        trace_id: str | None = None,
    ) -> GuidanceData:
        """
        Génère une guidance périodique (quotidienne ou hebdomadaire) - version async.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            period: Période de guidance ("daily" ou "weekly").
            conversation_id: ID de conversation pour le contexte (optionnel).
            request_id: Identifiant de requête pour le logging.
            trace_id: Identifiant de trace pour le tracing distribué.

        Returns:
            Guidance générée avec résumé et conseils.

        Raises:
            GuidanceServiceError: Si le profil natal manque ou en cas d'erreur LLM.
        """
        start = monotonic()
        trace_id = trace_id or request_id
        normalized_period = GuidanceService._validate_period(period)
        use_case = f"guidance_{normalized_period}"
        increment_counter("conversation_messages_total", 1.0)
        try:
            profile = UserBirthProfileService.get_for_user(db, user_id=user_id)
        except UserBirthProfileServiceError as error:
            if error.code == "birth_profile_not_found":
                raise GuidanceServiceError(
                    code="missing_birth_profile",
                    message="birth profile is required for guidance",
                    details={"user_id": str(user_id)},
                ) from error
            raise GuidanceServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error

        repo = ChatRepository(db)
        selected_conversation_id = GuidanceService._resolve_conversation_id(
            repo, user_id, conversation_id
        )

        context_lines, context_message_count = GuidanceService._select_context_lines(
            repo,
            selected_conversation_id,
        )

        persona_config = PersonaConfigService.get_active(db)
        persona_profile_code = persona_config.profile_code
        increment_counter(
            f"conversation_messages_total|persona_profile={persona_profile_code}",
            1.0,
        )
        increment_counter(
            f"conversation_guidance_messages_total|persona_profile={persona_profile_code}",
            1.0,
        )

        current_context = build_current_prompt_context(profile)

        natal_chart_summary = GuidanceService.build_natal_chart_summary_context(
            db,
            user_id=user_id,
            birth_date=profile.birth_date,
            birth_time=profile.birth_time,
            birth_place=profile.birth_place,
        )

        # Story 59.4: Build astro context before LLM call

        from app.services.astro_context_builder import AstroContextBuilder

        astro_context = None
        try:
            today = datetime_provider.today()
            if normalized_period == "daily":
                astro_context = AstroContextBuilder.build_daily(
                    user_id, today, current_context.current_timezone, db
                )
            else:
                astro_context = AstroContextBuilder.build_weekly(
                    user_id, today, current_context.current_timezone, db
                )
        except Exception as e:
            GuidanceService.logger.warning("astro_context_build_failed user_id=%d: %s", user_id, e)

        context: dict[str, Any] = {
            "birth_date": profile.birth_date,
            "birth_time": profile.birth_time,
            "birth_timezone": profile.birth_timezone,
            "persona_line": persona_config.to_prompt_line(),
            "context_lines": "\n".join(context_lines),
            "natal_chart_summary": natal_chart_summary,
            "current_datetime": current_context.current_datetime,
            "current_timezone": current_context.current_timezone,
            "current_location": current_context.current_location,
            "astro_context": astro_context.model_dump() if astro_context else None,
        }

        attempts = 0
        max_attempts = 1  # Network retries now handled exclusively by Gateway V2
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"

        for _ in range(max_attempts):
            attempts += 1
            try:
                # Story 66.15: Resolve user plan for assembly
                from app.services.entitlement.effective_entitlement_resolver_service import (
                    EffectiveEntitlementResolverService,
                )

                snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
                    db, app_user_id=user_id
                )
                user_plan = snapshot.plan_code

                result = await AIEngineAdapter.generate_guidance(
                    use_case=use_case,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    db=db,
                    plan=user_plan,
                )
                (
                    recovered_text,
                    fallback_used,
                    recovery_metadata,
                ) = await GuidanceService._apply_off_scope_recovery_async(
                    db=db,
                    use_case=use_case,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    assistant_content=result.raw_output,
                    persona_profile_code=persona_profile_code,
                )

                # If recovery happened, we might have lost structured output or have new one
                # For now, let's assume we use structured output if no recovery,
                # or we try to parse if recovery happened (as recovery might return fallback)

                if not recovery_metadata.recovery_applied and result.structured_output:
                    s = result.structured_output
                    summary_raw = s.get("summary") or s.get("text") or result.raw_output
                    key_points = GuidanceService._normalize_structured_string_list(
                        s.get("key_points") or s.get("highlights")
                    )
                    advice = GuidanceService._normalize_structured_string_list(
                        s.get("actionable_advice") or s.get("advice")
                    )
                    disclaimers = s.get("disclaimers") or []
                    disclaimer_raw = s.get("disclaimer") or (disclaimers[0] if disclaimers else "")
                else:
                    # If recovery was applied, we might have a raw text from fallback
                    # In _apply_off_scope_recovery_async, it returns a string for now.
                    # TODO: If we want full structure on recovery, we'd need to change it.
                    # For now, let's do a simple extraction from the recovered_text.
                    # No, AC says structure is guaranteed by Gateway V2.
                    # If recovery returned a new result, we should have used it.

                    # Manual fallback/parsing for recovery text if it's not structured
                    summary_raw = recovered_text
                    key_points = []
                    advice = []
                    disclaimer_raw = ""

                summary = GuidanceService._normalize_summary(summary_raw, normalized_period)
                period_label = "jour" if normalized_period == "daily" else "semaine"

                # Fallback for key_points if parsing failed or returned empty
                if not key_points:
                    key_points = [
                        (
                            f"Tendance astrologique du {period_label} "
                            "calculee depuis votre profil natal."
                        ),
                        "Lecture prudente: utilisez cette guidance comme aide de reflexion.",
                    ]

                # Fallback for advice if parsing failed or returned empty
                if not advice:
                    advice = [
                        "Prenez un moment de recul avant une decision importante.",
                        "Notez les evenements marquants pour comparer avec la guidance.",
                    ]

                disclaimer = disclaimer_raw or (
                    "Cette guidance est informative et ne remplace pas un avis professionnel "
                    "medical, legal ou financier."
                )

                elapsed_seconds = monotonic() - start
                observe_duration("guidance_latency_seconds", elapsed_seconds)
                observe_duration(
                    f"guidance_latency_seconds|persona_profile={persona_profile_code}",
                    elapsed_seconds,
                )
                return GuidanceData(
                    period=normalized_period,
                    summary=summary,
                    key_points=key_points[:2],  # Cap at 2 as per audit
                    actionable_advice=advice[:2],  # Cap at 2 as per audit
                    disclaimer=disclaimer,
                    attempts=attempts,
                    fallback_used=fallback_used,
                    recovery=recovery_metadata,
                    context_message_count=context_message_count,
                    generated_at=datetime_provider.utcnow(),
                )
            except (AIEngineAdapterError, TimeoutError, ConnectionError) as err:
                last_error_code, last_error_message = map_adapter_error_to_codes(err)
                increment_counter("conversation_llm_errors_total", 1.0)
                increment_counter(
                    f"conversation_llm_errors_total|persona_profile={persona_profile_code}",
                    1.0,
                )
                GuidanceService.logger.warning(
                    "guidance_generation_error request_id=%s code=%s",
                    request_id,
                    last_error_code,
                )
                await GuidanceService._sleep_before_retry_async(
                    attempts=attempts, max_attempts=max_attempts
                )

        elapsed_seconds = monotonic() - start
        observe_duration("guidance_latency_seconds", elapsed_seconds)
        observe_duration(
            f"guidance_latency_seconds|persona_profile={persona_profile_code}",
            elapsed_seconds,
        )
        raise GuidanceServiceError(
            code=last_error_code,
            message=last_error_message,
            details={
                "retryable": "true",
                "attempts": str(attempts),
                "action": "retry_guidance",
                "fallback_message": (
                    "Le service est indisponible temporairement. Reessayez dans un instant."
                ),
            },
        )

    @staticmethod
    def request_contextual_guidance(
        db: Session,
        *,
        user_id: int,
        situation: str,
        objective: str,
        time_horizon: str | None = None,
        natal_chart_summary_override: str | None = None,
        conversation_id: int | None = None,
        request_id: str = "n/a",
        entitlement_result: Any = None,
    ) -> ContextualGuidanceData:
        """
        Génère une guidance contextuelle basée sur une situation spécifique.

        Cette méthode synchrone est un wrapper autour de request_contextual_guidance_async.
        Note: Utilise asyncio.run() pour les tests unitaires synchrones.
        Les endpoints FastAPI utilisent directement request_contextual_guidance_async.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            situation: Description de la situation actuelle.
            objective: Objectif visé par l'utilisateur.
            time_horizon: Horizon temporel (optionnel).
            natal_chart_summary_override: Résumé natal forcé (optionnel).
            conversation_id: ID de conversation pour le contexte (optionnel).
            request_id: Identifiant de requête pour le logging.
            entitlement_result: Résultat d'entitlement pour le débit de tokens (optionnel).

        Returns:
            Guidance contextuelle générée.

        Raises:
            GuidanceServiceError: Si le profil natal manque ou les entrées sont invalides.
        """
        return asyncio.run(
            GuidanceService.request_contextual_guidance_async(
                db,
                user_id=user_id,
                situation=situation,
                objective=objective,
                time_horizon=time_horizon,
                natal_chart_summary_override=natal_chart_summary_override,
                conversation_id=conversation_id,
                request_id=request_id,
                entitlement_result=entitlement_result,
            )
        )

    @staticmethod
    async def request_contextual_guidance_async(
        db: Session,
        *,
        user_id: int,
        situation: str,
        objective: str,
        time_horizon: str | None = None,
        natal_chart_summary_override: str | None = None,
        conversation_id: int | None = None,
        request_id: str = "n/a",
        trace_id: str | None = None,
        entitlement_result: Any = None,
    ) -> ContextualGuidanceData:
        """
        Génère une guidance contextuelle basée sur une situation spécifique (async).

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            situation: Description de la situation actuelle.
            objective: Objectif visé par l'utilisateur.
            time_horizon: Horizon temporel (optionnel).
            natal_chart_summary_override: Résumé natal forcé (optionnel).
            conversation_id: ID de conversation pour le contexte (optionnel).
            request_id: Identifiant de requête pour le logging.
            trace_id: Identifiant de trace pour le tracing distribué.
            entitlement_result: Résultat d'entitlement pour le débit de tokens (optionnel).

        Returns:
            Guidance contextuelle générée.

        Raises:
            GuidanceServiceError: Si le profil natal manque ou les entrées sont invalides.
        """
        start = monotonic()
        trace_id = trace_id or request_id
        use_case = "guidance_contextual"
        (
            normalized_situation,
            normalized_objective,
            normalized_horizon,
        ) = GuidanceService._validate_contextual_input(
            situation,
            objective,
            time_horizon,
        )
        increment_counter("conversation_messages_total", 1.0)
        try:
            profile = UserBirthProfileService.get_for_user(db, user_id=user_id)
        except UserBirthProfileServiceError as error:
            if error.code == "birth_profile_not_found":
                raise GuidanceServiceError(
                    code="missing_birth_profile",
                    message="birth profile is required for guidance",
                    details={"user_id": str(user_id)},
                ) from error
            raise GuidanceServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error

        repo = ChatRepository(db)
        selected_conversation_id = GuidanceService._resolve_conversation_id(
            repo, user_id, conversation_id
        )

        context_lines, context_message_count = GuidanceService._select_context_lines(
            repo,
            selected_conversation_id,
        )
        persona_config = PersonaConfigService.get_active(db)
        persona_profile_code = persona_config.profile_code
        increment_counter(
            f"conversation_messages_total|persona_profile={persona_profile_code}",
            1.0,
        )
        increment_counter(
            f"conversation_guidance_messages_total|persona_profile={persona_profile_code}",
            1.0,
        )

        current_context = build_current_prompt_context(profile)

        natal_chart_summary = natal_chart_summary_override
        if natal_chart_summary is None:
            natal_chart_summary = GuidanceService.build_natal_chart_summary_context(
                db,
                user_id=user_id,
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                birth_place=profile.birth_place,
            )

        context: dict[str, str | None] = {
            "birth_date": profile.birth_date,
            "birth_time": profile.birth_time,
            "birth_timezone": profile.birth_timezone,
            "persona_line": persona_config.to_prompt_line(),
            "context_lines": "\n".join(context_lines),
            "situation": normalized_situation,
            "objective": normalized_objective,
            "time_horizon": normalized_horizon,
            "natal_chart_summary": natal_chart_summary,
            "current_datetime": current_context.current_datetime,
            "current_timezone": current_context.current_timezone,
            "current_location": current_context.current_location,
        }

        attempts = 0
        max_attempts = 1  # Network retries now handled exclusively by Gateway V2
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"

        for _ in range(max_attempts):
            attempts += 1
            try:
                # Story 66.15: Resolve user plan for assembly
                from app.services.entitlement.effective_entitlement_resolver_service import (
                    EffectiveEntitlementResolverService,
                )

                snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
                    db, app_user_id=user_id
                )
                user_plan = snapshot.plan_code

                result = await AIEngineAdapter.generate_guidance(
                    use_case=use_case,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    db=db,
                    plan=user_plan,
                )

                # Record tokens for the call
                GuidanceService._record_tokens(
                    db,
                    user_id=user_id,
                    feature_code="thematic_consultation",
                    gateway_result=result,
                    entitlement_result=entitlement_result,
                )

                (
                    recovered_text,
                    fallback_used,
                    recovery_metadata,
                ) = await GuidanceService._apply_off_scope_recovery_async(
                    db=db,
                    use_case=use_case,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    assistant_content=result.raw_output,
                    persona_profile_code=persona_profile_code,
                )

                if not recovery_metadata.recovery_applied and result.structured_output:
                    s = result.structured_output
                    summary_raw = s.get("summary") or s.get("text") or result.raw_output
                    key_points = GuidanceService._normalize_structured_string_list(
                        s.get("key_points") or s.get("highlights")
                    )
                    advice = GuidanceService._normalize_structured_string_list(
                        s.get("actionable_advice") or s.get("advice")
                    )
                    disclaimers = s.get("disclaimers") or []
                    disclaimer_raw = s.get("disclaimer") or (disclaimers[0] if disclaimers else "")
                    full_text = GuidanceService._compose_structured_guidance_full_text(
                        str(summary_raw),
                        [str(item) for item in key_points if str(item).strip()],
                        [str(item) for item in advice if str(item).strip()],
                    )
                else:
                    summary_raw = recovered_text
                    key_points = []
                    advice = []
                    disclaimer_raw = ""
                    full_text = recovered_text

                summary = GuidanceService._normalize_contextual_summary(summary_raw)

                # Fallback for key_points if parsing failed or returned empty
                if not key_points:
                    key_points = [
                        "Votre contexte immediat est integre a la lecture astrologique.",
                        "La recommandation reste prudente et orientee decision progressive.",
                    ]

                # Fallback for advice if parsing failed or returned empty
                if not advice:
                    advice = [
                        "Priorisez une action simple dans les prochaines 24h.",
                        "Re-evaluez apres le premier signal concret observe.",
                    ]

                disclaimer = disclaimer_raw or (
                    "Cette guidance est informative et ne remplace pas un avis professionnel "
                    "medical, legal ou financier."
                )

                elapsed_seconds = monotonic() - start
                observe_duration("guidance_latency_seconds", elapsed_seconds)
                observe_duration(
                    f"guidance_latency_seconds|persona_profile={persona_profile_code}",
                    elapsed_seconds,
                )
                return ContextualGuidanceData(
                    guidance_type="contextual",
                    situation=normalized_situation,
                    objective=normalized_objective,
                    time_horizon=normalized_horizon,
                    summary=summary,
                    full_text=full_text,
                    key_points=key_points[:2],  # Cap at 2 as per audit
                    actionable_advice=advice[:2],  # Cap at 2 as per audit
                    disclaimer=disclaimer,
                    attempts=attempts,
                    fallback_used=fallback_used,
                    recovery=recovery_metadata,
                    context_message_count=context_message_count,
                    generated_at=datetime_provider.utcnow(),
                )
            except (AIEngineAdapterError, TimeoutError, ConnectionError) as err:
                last_error_code, last_error_message = map_adapter_error_to_codes(err)
                increment_counter("conversation_llm_errors_total", 1.0)
                increment_counter(
                    f"conversation_llm_errors_total|persona_profile={persona_profile_code}",
                    1.0,
                )
                GuidanceService.logger.warning(
                    "guidance_generation_error request_id=%s code=%s",
                    request_id,
                    last_error_code,
                )
                await GuidanceService._sleep_before_retry_async(
                    attempts=attempts, max_attempts=max_attempts
                )

        elapsed_seconds = monotonic() - start
        observe_duration("guidance_latency_seconds", elapsed_seconds)
        observe_duration(
            f"guidance_latency_seconds|persona_profile={persona_profile_code}",
            elapsed_seconds,
        )
        raise GuidanceServiceError(
            code=last_error_code,
            message=last_error_message,
            details={
                "retryable": "true",
                "attempts": str(attempts),
                "action": "retry_guidance",
                "fallback_message": (
                    "Le service est indisponible temporairement. Reessayez dans un instant."
                ),
            },
        )
