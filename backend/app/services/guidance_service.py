"""
Astrological guidance service.

This module generates daily/weekly and contextual guidances based on
the user's natal profile and conversation history.
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timezone
from time import monotonic

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.llm.anonymizer import anonymize_text
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.ai_engine_adapter import (
    AIEngineAdapter,
    AIEngineAdapterError,
    assess_off_scope,
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
        return raw_summary[:500]

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
        use_case: str,
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        assistant_content: str,
        persona_profile_code: str,
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
            reformulated = await AIEngineAdapter.generate_guidance(
                use_case=use_case,
                context=context,
                user_id=user_id,
                request_id=f"{request_id}-recovery-1",
                trace_id=trace_id,
            )
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
            retried = await AIEngineAdapter.generate_guidance(
                use_case=use_case,
                context=context,
                user_id=user_id,
                request_id=f"{request_id}-recovery-2",
                trace_id=trace_id,
            )
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

        # natal_chart_summary: Not yet implemented. Templates support it via
        # {% if context.natal_chart_summary %} but computed chart data isn't
        # available here yet. Future enhancement: integrate with NatalChartService.
        context: dict[str, str | None] = {
            "birth_date": profile.birth_date,
            "birth_time": profile.birth_time,
            "birth_timezone": profile.birth_timezone,
            "persona_line": persona_config.to_prompt_line(),
            "context_lines": "\n".join(context_lines),
            "natal_chart_summary": None,
        }

        attempts = 0
        max_attempts = max(1, settings.chat_llm_retry_count + 1)
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"

        for _ in range(max_attempts):
            attempts += 1
            try:
                generated_text = await AIEngineAdapter.generate_guidance(
                    use_case=use_case,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                )
                (
                    recovered_text,
                    fallback_used,
                    recovery_metadata,
                ) = await GuidanceService._apply_off_scope_recovery_async(
                    use_case=use_case,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    assistant_content=generated_text,
                    persona_profile_code=persona_profile_code,
                )
                summary = GuidanceService._normalize_summary(recovered_text, normalized_period)
                period_label = "jour" if normalized_period == "daily" else "semaine"
                elapsed_seconds = monotonic() - start
                observe_duration("guidance_latency_seconds", elapsed_seconds)
                observe_duration(
                    f"guidance_latency_seconds|persona_profile={persona_profile_code}",
                    elapsed_seconds,
                )
                return GuidanceData(
                    period=normalized_period,
                    summary=summary,
                    key_points=[
                        (
                            f"Tendance astrologique du {period_label} "
                            "calculee depuis votre profil natal."
                        ),
                        "Lecture prudente: utilisez cette guidance comme aide de reflexion.",
                    ],
                    actionable_advice=[
                        "Prenez un moment de recul avant une decision importante.",
                        "Notez les evenements marquants pour comparer avec la guidance.",
                    ],
                    disclaimer=(
                        "Cette guidance est informative et ne remplace pas un avis professionnel "
                        "medical, legal ou financier."
                    ),
                    attempts=attempts,
                    fallback_used=fallback_used,
                    recovery=recovery_metadata,
                    context_message_count=context_message_count,
                    generated_at=datetime.now(timezone.utc),
                )
            except AIEngineAdapterError as err:
                if err.code == "rate_limit_exceeded":
                    last_error_code = "rate_limit_exceeded"
                    last_error_message = "rate limit exceeded"
                elif err.code == "context_too_large":
                    last_error_code = "context_too_large"
                    last_error_message = "context too large"
                else:
                    last_error_code = err.code
                    last_error_message = err.message
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
            except TimeoutError:
                last_error_code = "llm_timeout"
                last_error_message = "llm provider timeout"
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
            except ConnectionError:
                last_error_code = "llm_unavailable"
                last_error_message = "llm provider is unavailable"
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
        conversation_id: int | None = None,
        request_id: str = "n/a",
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
            conversation_id: ID de conversation pour le contexte (optionnel).
            request_id: Identifiant de requête pour le logging.

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
                conversation_id=conversation_id,
                request_id=request_id,
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
        conversation_id: int | None = None,
        request_id: str = "n/a",
        trace_id: str | None = None,
    ) -> ContextualGuidanceData:
        """
        Génère une guidance contextuelle basée sur une situation spécifique (async).

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            situation: Description de la situation actuelle.
            objective: Objectif visé par l'utilisateur.
            time_horizon: Horizon temporel (optionnel).
            conversation_id: ID de conversation pour le contexte (optionnel).
            request_id: Identifiant de requête pour le logging.
            trace_id: Identifiant de trace pour le tracing distribué.

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

        # natal_chart_summary: Not yet implemented. Templates support it via
        # {% if context.natal_chart_summary %} but computed chart data isn't
        # available here yet. Future enhancement: integrate with NatalChartService.
        context: dict[str, str | None] = {
            "birth_date": profile.birth_date,
            "birth_time": profile.birth_time,
            "birth_timezone": profile.birth_timezone,
            "persona_line": persona_config.to_prompt_line(),
            "context_lines": "\n".join(context_lines),
            "situation": normalized_situation,
            "objective": normalized_objective,
            "time_horizon": normalized_horizon,
            "natal_chart_summary": None,
        }

        attempts = 0
        max_attempts = max(1, settings.chat_llm_retry_count + 1)
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"

        for _ in range(max_attempts):
            attempts += 1
            try:
                generated_text = await AIEngineAdapter.generate_guidance(
                    use_case=use_case,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                )
                (
                    recovered_text,
                    fallback_used,
                    recovery_metadata,
                ) = await GuidanceService._apply_off_scope_recovery_async(
                    use_case=use_case,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    assistant_content=generated_text,
                    persona_profile_code=persona_profile_code,
                )
                summary = GuidanceService._normalize_contextual_summary(recovered_text)
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
                    key_points=[
                        "Votre contexte immediat est integre a la lecture astrologique.",
                        "La recommandation reste prudente et orientee decision progressive.",
                    ],
                    actionable_advice=[
                        "Priorisez une action simple dans les prochaines 24h.",
                        "Re-evaluez apres le premier signal concret observe.",
                    ],
                    disclaimer=(
                        "Cette guidance est informative et ne remplace pas un avis professionnel "
                        "medical, legal ou financier."
                    ),
                    attempts=attempts,
                    fallback_used=fallback_used,
                    recovery=recovery_metadata,
                    context_message_count=context_message_count,
                    generated_at=datetime.now(timezone.utc),
                )
            except AIEngineAdapterError as err:
                if err.code == "rate_limit_exceeded":
                    last_error_code = "rate_limit_exceeded"
                    last_error_message = "rate limit exceeded"
                elif err.code == "context_too_large":
                    last_error_code = "context_too_large"
                    last_error_message = "context too large"
                else:
                    last_error_code = err.code
                    last_error_message = err.message
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
            except TimeoutError:
                last_error_code = "llm_timeout"
                last_error_message = "llm provider timeout"
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
            except ConnectionError:
                last_error_code = "llm_unavailable"
                last_error_message = "llm provider is unavailable"
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
