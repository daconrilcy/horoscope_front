"""
Service de guidance astrologique.

Ce module génère des guidances quotidiennes/hebdomadaires et contextuelles
basées sur le profil natal de l'utilisateur et l'historique de conversation.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from time import monotonic, sleep

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.llm.anonymizer import anonymize_text
from app.infra.llm.client import LLMClient
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.persona_config_service import PersonaConfigService
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)


class GuidanceServiceError(Exception):
    """Exception levée lors d'erreurs de génération de guidance."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de guidance.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class GuidanceData(BaseModel):
    """Données d'une guidance périodique (quotidienne ou hebdomadaire)."""

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
    """Données d'une guidance contextuelle basée sur une situation."""

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
    """Métadonnées sur les tentatives de récupération hors-scope."""

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
    def _sleep_before_retry(*, attempts: int, max_attempts: int) -> None:
        """Effectue une pause exponentielle avec jitter avant une nouvelle tentative."""
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
        sleep(delay_seconds)

    @staticmethod
    def _validate_period(period: str) -> str:
        """Valide et normalise la période de guidance."""
        normalized = period.strip().lower()
        if normalized not in {"daily", "weekly"}:
            raise GuidanceServiceError(
                code="invalid_guidance_period",
                message="guidance period is invalid",
                details={"supported_periods": "daily,weekly"},
            )
        return normalized

    @staticmethod
    def _build_prompt(
        *,
        period: str,
        birth_date: str,
        birth_time: str,
        birth_timezone: str,
        persona_line: str,
        context_lines: list[str],
    ) -> str:
        """Construit le prompt pour une guidance périodique."""
        lines = [
            "[guidance_prompt_version:guidance-v1]",
            persona_line,
            "You are a prudent astrology assistant.",
            "Never provide medical, legal, or financial certainty.",
            f"Period: {period}",
            f"Birth date: {birth_date}",
            f"Birth time: {birth_time}",
            f"Birth timezone: {birth_timezone}",
            "Recent context:",
            *context_lines,
            "Return practical and calm guidance in French.",
        ]
        return anonymize_text("\n".join(lines))

    @staticmethod
    def _select_context_lines(
        repo: ChatRepository,
        conversation_id: int | None,
    ) -> tuple[list[str], int]:
        """Sélectionne les lignes de contexte depuis l'historique de conversation."""
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
    def _normalize_summary(generated_text: str, period: str) -> str:
        """Normalise le résumé généré en filtrant les artefacts de prompt."""
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
        """Normalise le résumé contextuel en filtrant les artefacts."""
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
        """Valide et normalise les entrées de guidance contextuelle."""
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
    def _build_contextual_prompt(
        *,
        birth_date: str,
        birth_time: str,
        birth_timezone: str,
        persona_line: str,
        situation: str,
        objective: str,
        time_horizon: str | None,
        context_lines: list[str],
    ) -> str:
        """Construit le prompt pour une guidance contextuelle."""
        lines = [
            "[guidance_prompt_version:guidance-contextual-v1]",
            persona_line,
            "You are a prudent astrology assistant.",
            "Never provide medical, legal, or financial certainty.",
            f"Birth date: {birth_date}",
            f"Birth time: {birth_time}",
            f"Birth timezone: {birth_timezone}",
            f"Situation: {situation}",
            f"Objective: {objective}",
            f"Time horizon: {time_horizon or 'not provided'}",
            "Recent context:",
            *context_lines,
            "Return practical and calm guidance in French.",
        ]
        return anonymize_text("\n".join(lines))

    @staticmethod
    def _assess_off_scope(content: str) -> tuple[bool, float, str | None]:
        """Évalue si une réponse est hors-scope avec un score de confiance."""
        normalized = content.strip().lower()
        if not normalized:
            return True, 1.0, "empty_response"
        if "[off_scope]" in normalized:
            return True, 0.95, "explicit_marker"
        if normalized.startswith("hors_scope:"):
            return True, 0.9, "explicit_prefix"
        return False, 0.0, None

    @staticmethod
    def _build_recovery_prompt(prompt: str, previous_reply: str, mode: str) -> str:
        """Construit un prompt de récupération pour reformuler une guidance hors-scope."""
        if mode == "reformulate":
            instruction = (
                "The previous guidance appears out-of-scope. "
                "Reformulate in French, stay practical, "
                "and keep a prudent tone."
            )
        else:
            instruction = (
                "Previous reformulation is still out-of-scope. "
                "Provide a concise, relevant French guidance. "
                "Do not include system markers, role prefixes, or prompt transcript."
            )
        lines = [
            "[recovery_prompt_version:guidance-offscope-v1]",
            instruction,
            "Guidance request context:",
            prompt,
            "Previous guidance answer:",
            anonymize_text(previous_reply),
        ]
        return "\n".join(lines)

    @staticmethod
    def _apply_off_scope_recovery(
        *,
        client: LLMClient,
        prompt: str,
        assistant_content: str,
        persona_profile_code: str,
    ) -> tuple[str, bool, GuidanceRecoveryMetadata]:
        """Applique les stratégies de récupération si la guidance est hors-scope."""
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
            reformulated = client.generate_reply(
                prompt=GuidanceService._build_recovery_prompt(
                    prompt,
                    assistant_content,
                    "reformulate",
                ),
                timeout_seconds=settings.chat_llm_timeout_seconds,
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
        except (TimeoutError, ConnectionError):
            GuidanceService.logger.warning("guidance_recovery_error strategy=reformulate")

        try:
            recovery_attempts += 1
            retried = client.generate_reply(
                prompt=GuidanceService._build_recovery_prompt(
                    prompt,
                    assistant_content,
                    "retry_once",
                ),
                timeout_seconds=settings.chat_llm_timeout_seconds,
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
        except (TimeoutError, ConnectionError):
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
        llm_client: LLMClient | None = None,
        request_id: str = "n/a",
    ) -> GuidanceData:
        """
        Génère une guidance périodique (quotidienne ou hebdomadaire).

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            period: Période de guidance ("daily" ou "weekly").
            conversation_id: ID de conversation pour le contexte (optionnel).
            llm_client: Client LLM personnalisé (optionnel).
            request_id: Identifiant de requête pour le logging.

        Returns:
            Guidance générée avec résumé et conseils.

        Raises:
            GuidanceServiceError: Si le profil natal manque ou en cas d'erreur LLM.
        """
        start = monotonic()
        normalized_period = GuidanceService._validate_period(period)
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
            selected_conversation_id = selected_conversation.id
        else:
            latest_conversation = repo.get_latest_active_conversation_by_user_id(user_id)
            selected_conversation_id = latest_conversation.id if latest_conversation else None

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
        prompt = GuidanceService._build_prompt(
            period=normalized_period,
            birth_date=profile.birth_date,
            birth_time=profile.birth_time,
            birth_timezone=profile.birth_timezone,
            persona_line=persona_config.to_prompt_line(),
            context_lines=context_lines,
        )
        client = llm_client or LLMClient()
        attempts = 0
        max_attempts = max(1, settings.chat_llm_retry_count + 1)
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"
        for _ in range(max_attempts):
            attempts += 1
            try:
                generated_text = client.generate_reply(
                    prompt=prompt,
                    timeout_seconds=settings.chat_llm_timeout_seconds,
                )
                (
                    recovered_text,
                    fallback_used,
                    recovery_metadata,
                ) = GuidanceService._apply_off_scope_recovery(
                    client=client,
                    prompt=prompt,
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
                GuidanceService._sleep_before_retry(attempts=attempts, max_attempts=max_attempts)
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
                GuidanceService._sleep_before_retry(attempts=attempts, max_attempts=max_attempts)

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
        llm_client: LLMClient | None = None,
        request_id: str = "n/a",
    ) -> ContextualGuidanceData:
        """
        Génère une guidance contextuelle basée sur une situation spécifique.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            situation: Description de la situation actuelle.
            objective: Objectif visé par l'utilisateur.
            time_horizon: Horizon temporel (optionnel).
            conversation_id: ID de conversation pour le contexte (optionnel).
            llm_client: Client LLM personnalisé (optionnel).
            request_id: Identifiant de requête pour le logging.

        Returns:
            Guidance contextuelle générée.

        Raises:
            GuidanceServiceError: Si le profil natal manque ou les entrées sont invalides.
        """
        start = monotonic()
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
            selected_conversation_id = selected_conversation.id
        else:
            latest_conversation = repo.get_latest_active_conversation_by_user_id(user_id)
            selected_conversation_id = latest_conversation.id if latest_conversation else None

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
        prompt = GuidanceService._build_contextual_prompt(
            birth_date=profile.birth_date,
            birth_time=profile.birth_time,
            birth_timezone=profile.birth_timezone,
            persona_line=persona_config.to_prompt_line(),
            situation=normalized_situation,
            objective=normalized_objective,
            time_horizon=normalized_horizon,
            context_lines=context_lines,
        )
        client = llm_client or LLMClient()
        attempts = 0
        max_attempts = max(1, settings.chat_llm_retry_count + 1)
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"
        for _ in range(max_attempts):
            attempts += 1
            try:
                generated_text = client.generate_reply(
                    prompt=prompt,
                    timeout_seconds=settings.chat_llm_timeout_seconds,
                )
                (
                    recovered_text,
                    fallback_used,
                    recovery_metadata,
                ) = GuidanceService._apply_off_scope_recovery(
                    client=client,
                    prompt=prompt,
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
                GuidanceService._sleep_before_retry(attempts=attempts, max_attempts=max_attempts)
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
                GuidanceService._sleep_before_retry(attempts=attempts, max_attempts=max_attempts)

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
