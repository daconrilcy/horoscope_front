"""
Chat and astrological guidance service.

This module handles conversations with the astrological assistant, including
context building, AI Engine calls, and off-scope recovery.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from time import monotonic

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.llm.anonymizer import LLMAnonymizationError, anonymize_text
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.ai_engine_adapter import (
    AIEngineAdapter,
    AIEngineAdapterError,
    assess_off_scope,
)
from app.services.persona_config_service import PersonaConfigService

logger = logging.getLogger(__name__)


class ChatGuidanceServiceError(Exception):
    """Exception raised by the chat guidance service."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialize a chat error.

        Args:
            code: Unique error code.
            message: Descriptive error message.
            details: Optional dictionary of additional details.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ChatMessageData(BaseModel):
    """Data for a conversation message."""

    message_id: int
    role: str
    content: str
    created_at: datetime


class ChatReplyData(BaseModel):
    """Complete response to a user message with metadata."""

    conversation_id: int
    attempts: int
    user_message: ChatMessageData
    assistant_message: ChatMessageData
    fallback_used: bool
    context: "ChatContextMetadata"
    recovery: "ChatRecoveryMetadata"


class ChatContextMetadata(BaseModel):
    """Metadata about the context used to generate the response."""

    message_ids: list[int]
    message_count: int
    context_characters: int
    prompt_version: str


class ChatRecoveryMetadata(BaseModel):
    """Metadata about off-scope recovery attempts."""

    off_scope_detected: bool
    off_scope_score: float
    recovery_strategy: str
    recovery_applied: bool
    recovery_attempts: int
    recovery_reason: str | None


class ChatConversationSummaryData(BaseModel):
    """Summary of a conversation for list display."""

    conversation_id: int
    status: str
    updated_at: datetime
    last_message_preview: str


class ChatConversationListData(BaseModel):
    """Paginated list of conversations."""

    conversations: list[ChatConversationSummaryData]
    total: int
    limit: int
    offset: int


class ChatConversationHistoryData(BaseModel):
    """Complete history of a conversation."""

    conversation_id: int
    status: str
    updated_at: datetime
    messages: list[ChatMessageData]


class ChatGuidanceService:
    """
    Service de conversation avec l'assistant astrologique.

    Gère l'envoi de messages, la construction du contexte, l'appel au LLM,
    et les stratégies de récupération en cas de réponse hors-scope.
    """

    _off_scope_events = 0
    _recovery_success_events = 0

    SAFE_FALLBACK_MESSAGE = (
        "Je prefere reformuler prudemment votre demande. "
        "Pouvez-vous preciser votre contexte immediat et votre objectif principal ?"
    )

    @classmethod
    def reset_quality_kpis(cls) -> None:
        """Réinitialise les compteurs de KPI qualité."""
        cls._off_scope_events = 0
        cls._recovery_success_events = 0

    @classmethod
    def get_quality_kpis(cls) -> dict[str, float]:
        """Retourne les KPI de qualité des conversations."""
        recovery_success_rate = (
            cls._recovery_success_events / cls._off_scope_events if cls._off_scope_events else 0.0
        )
        return {
            "off_scope_count": float(cls._off_scope_events),
            "recovery_success_rate": recovery_success_rate,
        }

    @staticmethod
    def _validate_user_message(message: str) -> str:
        """Valide et normalise le message utilisateur."""
        normalized = message.strip()
        if not normalized:
            raise ChatGuidanceServiceError(
                code="invalid_chat_input",
                message="chat message is required",
                details={"field": "message"},
            )
        return normalized

    @staticmethod
    def _validate_context_config() -> tuple[int, int]:
        """Valide la configuration de contexte de chat."""
        window_messages = settings.chat_context_window_messages
        max_characters = settings.chat_context_max_characters
        if window_messages <= 0 or max_characters <= 0:
            raise ChatGuidanceServiceError(
                code="invalid_chat_context_config",
                message="chat context configuration is invalid",
                details={},
            )
        return window_messages, max_characters

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> tuple[int, int]:
        """Valide les paramètres de pagination."""
        if limit <= 0 or limit > 100:
            raise ChatGuidanceServiceError(
                code="invalid_chat_pagination",
                message="chat pagination is invalid",
                details={"field": "limit"},
            )
        if offset < 0:
            raise ChatGuidanceServiceError(
                code="invalid_chat_pagination",
                message="chat pagination is invalid",
                details={"field": "offset"},
            )
        return limit, offset

    @staticmethod
    def _build_prompt_and_context_metadata(
        *,
        repo: ChatRepository,
        conversation_id: int,
        persona_line: str,
    ) -> tuple[str, ChatContextMetadata]:
        """Construit le prompt LLM avec le contexte de conversation."""
        window_messages, max_characters = ChatGuidanceService._validate_context_config()
        recent_messages = repo.get_recent_messages(
            conversation_id=conversation_id,
            limit=window_messages,
        )

        selected: list[tuple[int, str, str]] = []
        total_chars = 0
        for message in reversed(recent_messages):
            try:
                normalized_content = anonymize_text(message.content.strip())
            except LLMAnonymizationError as error:
                raise ChatGuidanceServiceError(
                    code="llm_anonymization_failed",
                    message="llm payload anonymization failed",
                    details={},
                ) from error
            message_chars = len(normalized_content)
            if selected and total_chars + message_chars > max_characters:
                break
            if not selected and message_chars > max_characters:
                normalized_content = normalized_content[:max_characters]
                message_chars = len(normalized_content)
            selected.append((message.id, message.role, normalized_content))
            total_chars += message_chars

        if not selected:
            raise ChatGuidanceServiceError(
                code="chat_context_unavailable",
                message="chat context could not be built",
                details={"conversation_id": str(conversation_id)},
            )

        selected.reverse()
        prompt_lines = [f"{role}: {content}" for _, role, content in selected]
        prompt = f"[prompt_version:{settings.chat_prompt_version}]\n{persona_line}\n" + "\n".join(
            prompt_lines
        )
        context_metadata = ChatContextMetadata(
            message_ids=[item[0] for item in selected],
            message_count=len(selected),
            context_characters=total_chars,
            prompt_version=settings.chat_prompt_version,
        )
        return prompt, context_metadata

    @staticmethod
    def _assess_off_scope(content: str) -> tuple[bool, float, str | None]:
        """Assess if a response is off-scope with a confidence score."""
        return assess_off_scope(content)

    @staticmethod
    def _anonymize_or_raise(text: str) -> str:
        """Anonymise le texte ou lève une exception en cas d'erreur."""
        try:
            return anonymize_text(text)
        except LLMAnonymizationError as error:
            raise ChatGuidanceServiceError(
                code="llm_anonymization_failed",
                message="llm payload anonymization failed",
                details={},
            ) from error

    @staticmethod
    async def _apply_off_scope_recovery_async(
        *,
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        assistant_content: str,
        persona_profile_code: str,
    ) -> tuple[str, bool, ChatRecoveryMetadata]:
        """
        Applique les stratégies de récupération si la réponse est hors-scope (async).

        Tente successivement reformulation, retry, puis fallback sécurisé.
        """
        off_scope_detected, off_scope_score, off_scope_reason = (
            ChatGuidanceService._assess_off_scope(assistant_content)
        )
        if not off_scope_detected:
            return (
                assistant_content,
                False,
                ChatRecoveryMetadata(
                    off_scope_detected=False,
                    off_scope_score=0.0,
                    recovery_strategy="none",
                    recovery_applied=False,
                    recovery_attempts=0,
                    recovery_reason=None,
                ),
            )

        ChatGuidanceService._off_scope_events += 1
        increment_counter("conversation_out_of_scope_total", 1.0)
        increment_counter(
            f"conversation_out_of_scope_total|persona_profile={persona_profile_code}",
            1.0,
        )
        kpis = ChatGuidanceService.get_quality_kpis()
        logger.warning(
            "chat_off_scope_detected strategy=reformulate reason=%s "
            "score=%.2f off_scope_count=%.0f recovery_success_rate=%.3f",
            off_scope_reason or "unknown",
            off_scope_score,
            kpis["off_scope_count"],
            kpis["recovery_success_rate"],
        )

        recovery_attempts = 0
        try:
            recovery_attempts += 1
            recovery_messages = messages + [
                {"role": "assistant", "content": assistant_content},
                {
                    "role": "user",
                    "content": (
                        "La réponse précédente semble hors-sujet. Reformule en "
                        "français de manière pratique et pertinente en 3 phrases."
                    ),
                },
            ]
            reformulated = await AIEngineAdapter.generate_chat_reply(
                messages=recovery_messages,
                context=context,
                user_id=user_id,
                request_id=f"{request_id}-recovery-1",
                trace_id=trace_id,
            )
            reformulate_off_scope, _, _ = ChatGuidanceService._assess_off_scope(reformulated)
            if not reformulate_off_scope:
                ChatGuidanceService._recovery_success_events += 1
                increment_counter("conversation_recovery_success_total", 1.0)
                increment_counter(
                    f"conversation_recovery_success_total|persona_profile={persona_profile_code}",
                    1.0,
                )
                kpis = ChatGuidanceService.get_quality_kpis()
                logger.info("chat_recovery_applied strategy=reformulate success=true")
                logger.info(
                    "chat_quality_kpis off_scope_count=%.0f recovery_success_rate=%.3f",
                    kpis["off_scope_count"],
                    kpis["recovery_success_rate"],
                )
                return (
                    reformulated,
                    False,
                    ChatRecoveryMetadata(
                        off_scope_detected=True,
                        off_scope_score=off_scope_score,
                        recovery_strategy="reformulate",
                        recovery_applied=True,
                        recovery_attempts=recovery_attempts,
                        recovery_reason=off_scope_reason,
                    ),
                )
        except (TimeoutError, ConnectionError, AIEngineAdapterError):
            logger.warning("chat_recovery_error strategy=reformulate")

        try:
            recovery_attempts += 1
            retry_messages = messages + [
                {
                    "role": "user",
                    "content": (
                        "Reprends la conversation et réponds de manière concise et pertinente. "
                        "Pas de marqueurs système ni de préfixes."
                    ),
                },
            ]
            retried = await AIEngineAdapter.generate_chat_reply(
                messages=retry_messages,
                context=context,
                user_id=user_id,
                request_id=f"{request_id}-recovery-2",
                trace_id=trace_id,
            )
            retry_off_scope, _, _ = ChatGuidanceService._assess_off_scope(retried)
            if not retry_off_scope:
                ChatGuidanceService._recovery_success_events += 1
                increment_counter("conversation_recovery_success_total", 1.0)
                increment_counter(
                    f"conversation_recovery_success_total|persona_profile={persona_profile_code}",
                    1.0,
                )
                kpis = ChatGuidanceService.get_quality_kpis()
                logger.info("chat_recovery_applied strategy=retry_once success=true")
                logger.info(
                    "chat_quality_kpis off_scope_count=%.0f recovery_success_rate=%.3f",
                    kpis["off_scope_count"],
                    kpis["recovery_success_rate"],
                )
                return (
                    retried,
                    False,
                    ChatRecoveryMetadata(
                        off_scope_detected=True,
                        off_scope_score=off_scope_score,
                        recovery_strategy="retry_once",
                        recovery_applied=True,
                        recovery_attempts=recovery_attempts,
                        recovery_reason=off_scope_reason,
                    ),
                )
        except (TimeoutError, ConnectionError, AIEngineAdapterError):
            logger.warning("chat_recovery_error strategy=retry_once")

        logger.info("chat_recovery_applied strategy=safe_fallback success=true")
        return (
            ChatGuidanceService.SAFE_FALLBACK_MESSAGE,
            True,
            ChatRecoveryMetadata(
                off_scope_detected=True,
                off_scope_score=off_scope_score,
                recovery_strategy="safe_fallback",
                recovery_applied=True,
                recovery_attempts=recovery_attempts,
                recovery_reason=off_scope_reason,
            ),
        )

    @staticmethod
    def send_message(
        db: Session,
        *,
        user_id: int,
        message: str,
        conversation_id: int | None = None,
        request_id: str = "n/a",
    ) -> ChatReplyData:
        """
        Envoie un message et obtient une réponse de l'assistant.

        Cette méthode synchrone est un wrapper autour de send_message_async.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            message: Contenu du message.
            conversation_id: ID de conversation existante (optionnel).
            request_id: Identifiant de requête pour le logging.

        Returns:
            Réponse complète avec métadonnées de contexte et récupération.

        Raises:
            ChatGuidanceServiceError: Si la conversation n'existe pas ou en cas d'erreur LLM.
        """
        return asyncio.run(
            ChatGuidanceService.send_message_async(
                db,
                user_id=user_id,
                message=message,
                conversation_id=conversation_id,
                request_id=request_id,
            )
        )

    @staticmethod
    async def send_message_async(
        db: Session,
        *,
        user_id: int,
        message: str,
        conversation_id: int | None = None,
        request_id: str = "n/a",
        trace_id: str | None = None,
    ) -> ChatReplyData:
        """
        Envoie un message et obtient une réponse de l'assistant (async).

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            message: Contenu du message.
            conversation_id: ID de conversation existante (optionnel).
            request_id: Identifiant de requête pour le logging.
            trace_id: Identifiant de trace pour le tracing distribué.

        Returns:
            Réponse complète avec métadonnées de contexte et récupération.

        Raises:
            ChatGuidanceServiceError: Si la conversation n'existe pas ou en cas d'erreur LLM.
        """
        start = monotonic()
        trace_id = trace_id or request_id
        normalized_message = ChatGuidanceService._validate_user_message(message)
        increment_counter("conversation_messages_total", 1.0)
        increment_counter("conversation_chat_messages_total", 1.0)
        repo = ChatRepository(db)
        if conversation_id is not None:
            conversation = repo.get_conversation_by_id(conversation_id)
            if conversation is None:
                raise ChatGuidanceServiceError(
                    code="conversation_not_found",
                    message="conversation was not found",
                    details={"conversation_id": str(conversation_id)},
                )
            if conversation.user_id != user_id:
                raise ChatGuidanceServiceError(
                    code="conversation_forbidden",
                    message="conversation does not belong to user",
                    details={"conversation_id": str(conversation_id)},
                )
        else:
            conversation = repo.get_latest_active_conversation_by_user_id(user_id)
            if conversation is None:
                conversation = repo.create_conversation(user_id=user_id)

        user_message = repo.create_message(
            conversation_id=conversation.id,
            role="user",
            content=normalized_message,
        )

        persona_config = PersonaConfigService.get_active(db)
        increment_counter(
            f"conversation_messages_total|persona_profile={persona_config.profile_code}",
            1.0,
        )
        increment_counter(
            f"conversation_chat_messages_total|persona_profile={persona_config.profile_code}",
            1.0,
        )

        _, context_metadata = ChatGuidanceService._build_prompt_and_context_metadata(
            repo=repo,
            conversation_id=conversation.id,
            persona_line=persona_config.to_prompt_line(),
        )

        window_messages, max_characters = ChatGuidanceService._validate_context_config()
        recent_messages = repo.get_recent_messages(
            conversation_id=conversation.id,
            limit=window_messages,
        )

        selected_messages: list[tuple[str, str]] = []
        total_chars = 0
        for msg in reversed(recent_messages):
            try:
                normalized_content = anonymize_text(msg.content.strip())
            except LLMAnonymizationError as error:
                raise ChatGuidanceServiceError(
                    code="llm_anonymization_failed",
                    message="llm payload anonymization failed",
                    details={},
                ) from error
            message_chars = len(normalized_content)
            if selected_messages and total_chars + message_chars > max_characters:
                break
            if not selected_messages and message_chars > max_characters:
                normalized_content = normalized_content[:max_characters]
                message_chars = len(normalized_content)
            selected_messages.append((msg.role, normalized_content))
            total_chars += message_chars

        selected_messages.reverse()
        chat_messages: list[dict[str, str]] = [
            {"role": role, "content": content} for role, content in selected_messages
        ]

        # natal_chart_summary: Not yet implemented. The templates support it via
        # {% if context.natal_chart_summary %} but we don't have access to computed
        # natal chart data here. Future enhancement: integrate with NatalChartService.
        context: dict[str, str | None] = {
            "persona_line": persona_config.to_prompt_line(),
            "natal_chart_summary": None,
        }

        attempts = 0
        max_attempts = max(1, settings.chat_llm_retry_count + 1)
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"

        # No backoff between retries: chat UX prioritizes responsiveness over throttling.
        # For guidance endpoints (less interactive), see GuidanceService._sleep_before_retry().
        for _ in range(max_attempts):
            attempts += 1
            try:
                assistant_content = await AIEngineAdapter.generate_chat_reply(
                    messages=chat_messages,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                )
                (
                    assistant_content,
                    fallback_used,
                    recovery_metadata,
                ) = await ChatGuidanceService._apply_off_scope_recovery_async(
                    messages=chat_messages,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    assistant_content=assistant_content,
                    persona_profile_code=persona_config.profile_code,
                )
                assistant_message = repo.create_message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=assistant_content,
                    metadata_payload={
                        "attempts": attempts,
                        "fallback_used": fallback_used,
                        "persona_profile_code": persona_config.profile_code,
                        "context": context_metadata.model_dump(mode="json"),
                        "recovery": recovery_metadata.model_dump(mode="json"),
                    },
                )
                elapsed_seconds = monotonic() - start
                observe_duration("conversation_latency_seconds", elapsed_seconds)
                observe_duration(
                    f"conversation_latency_seconds|persona_profile={persona_config.profile_code}",
                    elapsed_seconds,
                )
                return ChatReplyData(
                    conversation_id=conversation.id,
                    attempts=attempts,
                    user_message=ChatMessageData(
                        message_id=user_message.id,
                        role=user_message.role,
                        content=user_message.content,
                        created_at=user_message.created_at,
                    ),
                    assistant_message=ChatMessageData(
                        message_id=assistant_message.id,
                        role=assistant_message.role,
                        content=assistant_message.content,
                        created_at=assistant_message.created_at,
                    ),
                    fallback_used=fallback_used,
                    context=context_metadata,
                    recovery=recovery_metadata,
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
                    f"conversation_llm_errors_total|persona_profile={persona_config.profile_code}",
                    1.0,
                )
                logger.warning(
                    "chat_generation_error request_id=%s code=%s",
                    request_id,
                    last_error_code,
                )
            except TimeoutError:
                last_error_code = "llm_timeout"
                last_error_message = "llm provider timeout"
                increment_counter("conversation_llm_errors_total", 1.0)
                increment_counter(
                    f"conversation_llm_errors_total|persona_profile={persona_config.profile_code}",
                    1.0,
                )
                logger.warning(
                    "chat_generation_error request_id=%s code=%s",
                    request_id,
                    last_error_code,
                )
            except ConnectionError:
                last_error_code = "llm_unavailable"
                last_error_message = "llm provider is unavailable"
                increment_counter("conversation_llm_errors_total", 1.0)
                increment_counter(
                    f"conversation_llm_errors_total|persona_profile={persona_config.profile_code}",
                    1.0,
                )
                logger.warning(
                    "chat_generation_error request_id=%s code=%s",
                    request_id,
                    last_error_code,
                )

        observe_duration("conversation_latency_seconds", monotonic() - start)
        raise ChatGuidanceServiceError(
            code=last_error_code,
            message=last_error_message,
            details={
                "retryable": "true",
                "attempts": str(attempts),
                "action": "retry_message",
                "fallback_message": (
                    "Le service est indisponible temporairement. Reessayez dans un instant."
                ),
                "conversation_id": str(conversation.id),
                "context_message_count": str(context_metadata.message_count),
                "context_characters": str(context_metadata.context_characters),
                "prompt_version": context_metadata.prompt_version,
            },
        )

    @staticmethod
    def list_conversations(
        db: Session,
        *,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> ChatConversationListData:
        """
        Liste les conversations d'un utilisateur avec pagination.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            limit: Nombre maximum de résultats.
            offset: Décalage pour la pagination.

        Returns:
            Liste paginée des conversations avec aperçu.
        """
        validated_limit, validated_offset = ChatGuidanceService._validate_pagination(limit, offset)
        repo = ChatRepository(db)
        conversations = repo.list_conversations_with_last_preview_by_user_id(
            user_id,
            limit=validated_limit,
            offset=validated_offset,
        )
        total = repo.count_conversations_by_user_id(user_id)
        items: list[ChatConversationSummaryData] = []
        for conversation, preview in conversations:
            items.append(
                ChatConversationSummaryData(
                    conversation_id=conversation.id,
                    status=conversation.status,
                    updated_at=conversation.updated_at,
                    last_message_preview=(preview or "")[:120],
                )
            )
        return ChatConversationListData(
            conversations=items,
            total=total,
            limit=validated_limit,
            offset=validated_offset,
        )

    @staticmethod
    def get_conversation_history(
        db: Session,
        *,
        user_id: int,
        conversation_id: int,
    ) -> ChatConversationHistoryData:
        """
        Récupère l'historique complet d'une conversation.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur (pour vérification d'accès).
            conversation_id: Identifiant de la conversation.

        Returns:
            Historique avec tous les messages.

        Raises:
            ChatGuidanceServiceError: Si la conversation n'existe pas ou
                n'appartient pas à l'utilisateur.
        """
        repo = ChatRepository(db)
        conversation = repo.get_conversation_by_id(conversation_id)
        if conversation is None:
            raise ChatGuidanceServiceError(
                code="conversation_not_found",
                message="conversation was not found",
                details={"conversation_id": str(conversation_id)},
            )
        if conversation.user_id != user_id:
            raise ChatGuidanceServiceError(
                code="conversation_forbidden",
                message="conversation does not belong to user",
                details={"conversation_id": str(conversation_id)},
            )
        messages = repo.get_messages_by_conversation_id(conversation_id)
        return ChatConversationHistoryData(
            conversation_id=conversation.id,
            status=conversation.status,
            updated_at=conversation.updated_at,
            messages=[
                ChatMessageData(
                    message_id=message.id,
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in messages
            ],
        )
