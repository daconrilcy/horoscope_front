"""
Chat and astrological guidance service.

This module handles conversations with the astrological assistant, including
context building, AI Engine calls, and off-scope recovery.
"""

from __future__ import annotations

import asyncio
import logging
import urllib.parse
import uuid
from datetime import datetime
from time import monotonic

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.llm.anonymizer import LLMAnonymizationError, anonymize_text
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.ai_engine_adapter import (
    AIEngineAdapter,
    AIEngineAdapterError,
    assess_off_scope,
    map_adapter_error_to_codes,
)
from app.services.current_context import build_current_prompt_context
from app.services.natal_interpretation_service import _detect_degraded_mode, build_chat_natal_hint
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)
from app.services.user_natal_chart_service import UserNatalChartService, UserNatalChartServiceError

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
    client_message_id: str | None = None
    reply_to_client_message_id: str | None = None


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
    persona_id: uuid.UUID
    persona_name: str | None
    avatar_url: str | None
    status: str
    updated_at: datetime
    last_message_at: datetime | None
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
    persona_id: uuid.UUID
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
        db: Session,
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
                db=db,
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
                db=db,
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
        persona_id: str | None = None,
        client_message_id: str | None = None,
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
            persona_id: ID de persona spécifique (optionnel).
            client_message_id: UUID d'idempotence généré côté client (optionnel).

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
                persona_id=persona_id,
                client_message_id=client_message_id,
            )
        )

    @staticmethod
    async def _get_default_persona_id(db: Session) -> uuid.UUID:
        """Récupère l'ID du persona par défaut (Astrologue Standard)."""
        from app.infra.db.models.llm_persona import LlmPersonaModel

        # Tenter de trouver "Astrologue Standard"
        stmt = (
            select(LlmPersonaModel.id).where(LlmPersonaModel.name == "Astrologue Standard").limit(1)
        )
        persona_id = db.scalar(stmt)
        if persona_id:
            return persona_id

        # Fallback: premier persona activé
        stmt = (
            select(LlmPersonaModel.id)
            .where(LlmPersonaModel.enabled)
            .order_by(LlmPersonaModel.created_at)
            .limit(1)
        )
        persona_id = db.scalar(stmt)
        if persona_id:
            return persona_id

        # Hard fallback: n'importe quel persona
        stmt = select(LlmPersonaModel.id).limit(1)
        persona_id = db.scalar(stmt)
        if persona_id:
            return persona_id

        default_persona = LlmPersonaModel(
            name="Astrologue Standard",
            description="Persona par defaut pour les conversations astrologiques.",
            tone="direct",
            verbosity="medium",
            style_markers=["precis", "empathique"],
            boundaries=["Aucun conseil medical, legal ou financier ferme."],
            allowed_topics=["astrologie", "guidance", "reflexion personnelle"],
            disallowed_topics=["diagnostic medical", "prediction mortelle", "conseil juridique"],
            formatting={"sections": True, "bullets": False, "emojis": False},
            enabled=True,
        )
        db.add(default_persona)
        try:
            db.flush()
        except IntegrityError as error:
            db.rollback()
            raise ChatGuidanceServiceError(
                code="no_persona_available",
                message="failed to create default LLM persona",
            ) from error
        return default_persona.id

    @staticmethod
    def _load_persona_sync(db: Session, persona_id: uuid.UUID | None) -> object:
        """
        Charge le LlmPersonaModel correspondant au persona_id de la conversation.

        Si persona_id est None (conversation legacy), log un warning et retourne le persona
        par défaut pour permettre un backfill ultérieur (AC4).
        """
        from app.infra.db.models.llm_persona import LlmPersonaModel

        if persona_id is not None:
            stmt = select(LlmPersonaModel).where(LlmPersonaModel.id == persona_id).limit(1)
            persona = db.scalar(stmt)
            if persona is not None:
                return persona
            logger.warning("chat_persona_not_found persona_id=%s fallback=default", persona_id)
        else:
            logger.warning(
                "chat_persona_missing persona_id=None fallback=default (backfill required)"
            )

        # Fallback: Astrologue Standard ou premier persona activé
        stmt = select(LlmPersonaModel).where(LlmPersonaModel.name == "Astrologue Standard").limit(1)
        persona = db.scalar(stmt)
        if persona:
            return persona

        stmt = (
            select(LlmPersonaModel)
            .where(LlmPersonaModel.enabled)
            .order_by(LlmPersonaModel.created_at)
            .limit(1)
        )
        persona = db.scalar(stmt)
        if persona:
            return persona

        stmt = select(LlmPersonaModel).limit(1)
        persona = db.scalar(stmt)
        if persona:
            return persona

        raise ChatGuidanceServiceError(
            code="no_persona_available",
            message="no LLM persona available in database",
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
        persona_id: str | uuid.UUID | None = None,
        client_message_id: str | None = None,
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
            persona_id: ID de persona spécifique (optionnel).

        Returns:
            Réponse complète avec métadonnées de contexte et récupération.

        Raises:
            ChatGuidanceServiceError: Si la conversation n'existe pas ou en cas d'erreur LLM.
        """
        import uuid as uuid_module

        start = monotonic()
        trace_id = trace_id or request_id
        normalized_message = ChatGuidanceService._validate_user_message(message)
        increment_counter("conversation_messages_total", 1.0)
        increment_counter("conversation_chat_messages_total", 1.0)
        repo = ChatRepository(db)

        # Resolve persona_id if not provided
        try:
            if persona_id is None and conversation_id is None:
                resolved_persona_id = await ChatGuidanceService._get_default_persona_id(db)
            elif persona_id is not None:
                if isinstance(persona_id, str):
                    resolved_persona_id = uuid_module.UUID(persona_id)
                else:
                    resolved_persona_id = persona_id
            else:
                # Will be taken from conversation if conversation_id is set
                resolved_persona_id = None
        except ValueError:
            raise ChatGuidanceServiceError(
                code="invalid_persona_id",
                message="persona_id is not a valid UUID",
                details={"persona_id": str(persona_id)},
            )

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
            # Ensure persona_id matches if provided
            if resolved_persona_id and conversation.persona_id != resolved_persona_id:
                raise ChatGuidanceServiceError(
                    code="conversation_persona_mismatch",
                    message="conversation does not match requested persona",
                    details={
                        "conversation_id": str(conversation_id),
                        "requested_persona_id": str(resolved_persona_id),
                    },
                )
        else:
            # Multi-persona routing: find or create active conversation for this user + persona
            conversation = repo.get_or_create_active_conversation(
                user_id=user_id, persona_id=resolved_persona_id
            )

        # Idempotency check: if client_message_id provided and this exact message was already
        # processed (e.g. network timeout on previous attempt), return the cached response.
        if client_message_id:
            existing_user_msg = repo.get_message_by_client_id(conversation.id, client_message_id)
            if existing_user_msg:
                existing_assistant_msg = repo.get_next_assistant_message(
                    conversation.id, existing_user_msg.id
                )
                if existing_assistant_msg:
                    logger.info(
                        "chat_idempotent_hit request_id=%s client_message_id=%s",
                        request_id,
                        client_message_id,
                    )
                    stored_meta = existing_assistant_msg.metadata_payload
                    stored_context = stored_meta.get("context") or {}
                    stored_recovery = stored_meta.get("recovery") or {}
                    return ChatReplyData(
                        conversation_id=conversation.id,
                        attempts=int(stored_meta.get("attempts", 1)),
                        user_message=ChatMessageData(
                            message_id=existing_user_msg.id,
                            role=existing_user_msg.role,
                            content=existing_user_msg.content,
                            created_at=existing_user_msg.created_at,
                            client_message_id=existing_user_msg.client_message_id,
                        ),
                        assistant_message=ChatMessageData(
                            message_id=existing_assistant_msg.id,
                            role=existing_assistant_msg.role,
                            content=existing_assistant_msg.content,
                            created_at=existing_assistant_msg.created_at,
                            reply_to_client_message_id=existing_assistant_msg.reply_to_client_message_id,
                        ),
                        fallback_used=bool(stored_meta.get("fallback_used", False)),
                        context=ChatContextMetadata(**stored_context)
                        if stored_context
                        else ChatContextMetadata(
                            message_ids=[],
                            message_count=0,
                            context_characters=0,
                            prompt_version=settings.chat_prompt_version,
                        ),
                        recovery=ChatRecoveryMetadata(**stored_recovery)
                        if stored_recovery
                        else ChatRecoveryMetadata(
                            off_scope_detected=False,
                            off_scope_score=0.0,
                            recovery_strategy="none",
                            recovery_applied=False,
                            recovery_attempts=0,
                            recovery_reason=None,
                        ),
                    )
                # User message exists but no assistant yet (race condition):
                # skip creating a duplicate user message, proceed to run LLM.
                user_message = existing_user_msg
            else:
                # Use a savepoint to handle the race where two concurrent requests
                # carry the same client_message_id and both see no existing message.
                try:
                    with db.begin_nested():
                        user_message = repo.create_message(
                            conversation_id=conversation.id,
                            role="user",
                            content=normalized_message,
                            client_message_id=client_message_id,
                        )
                except IntegrityError:
                    # Another request just won the race and created this user message.
                    # Re-fetch and reuse it; the winner will create the assistant message.
                    existing_user_msg = repo.get_message_by_client_id(
                        conversation.id, client_message_id
                    )
                    if existing_user_msg:
                        existing_assistant_msg = repo.get_next_assistant_message(
                            conversation.id, existing_user_msg.id
                        )
                        if existing_assistant_msg:
                            logger.info(
                                "chat_idempotent_hit_race request_id=%s client_message_id=%s",
                                request_id,
                                client_message_id,
                            )
                            stored_meta = existing_assistant_msg.metadata_payload
                            stored_context = stored_meta.get("context") or {}
                            stored_recovery = stored_meta.get("recovery") or {}
                            return ChatReplyData(
                                conversation_id=conversation.id,
                                attempts=int(stored_meta.get("attempts", 1)),
                                user_message=ChatMessageData(
                                    message_id=existing_user_msg.id,
                                    role=existing_user_msg.role,
                                    content=existing_user_msg.content,
                                    created_at=existing_user_msg.created_at,
                                    client_message_id=existing_user_msg.client_message_id,
                                ),
                                assistant_message=ChatMessageData(
                                    message_id=existing_assistant_msg.id,
                                    role=existing_assistant_msg.role,
                                    content=existing_assistant_msg.content,
                                    created_at=existing_assistant_msg.created_at,
                                    reply_to_client_message_id=existing_assistant_msg.reply_to_client_message_id,
                                ),
                                fallback_used=bool(stored_meta.get("fallback_used", False)),
                                context=ChatContextMetadata(**stored_context)
                                if stored_context
                                else ChatContextMetadata(
                                    message_ids=[],
                                    message_count=0,
                                    context_characters=0,
                                    prompt_version=settings.chat_prompt_version,
                                ),
                                recovery=ChatRecoveryMetadata(**stored_recovery)
                                if stored_recovery
                                else ChatRecoveryMetadata(
                                    off_scope_detected=False,
                                    off_scope_score=0.0,
                                    recovery_strategy="none",
                                    recovery_applied=False,
                                    recovery_attempts=0,
                                    recovery_reason=None,
                                ),
                            )
                        # User message exists but no assistant yet; reuse it.
                        user_message = existing_user_msg
                    else:
                        raise
        else:
            user_message = repo.create_message(
                conversation_id=conversation.id,
                role="user",
                content=normalized_message,
            )

        persona = ChatGuidanceService._load_persona_sync(db, conversation.persona_id)
        persona_profile_code = (
            "legacy-default"
            if persona.name == "Astrologue Standard"
            else persona.name.lower().replace(" ", "-")
        )
        increment_counter(
            f"conversation_messages_total|persona_profile={persona_profile_code}",
            1.0,
        )
        increment_counter(
            f"conversation_chat_messages_total|persona_profile={persona_profile_code}",
            1.0,
        )

        window_messages, max_characters = ChatGuidanceService._validate_context_config()
        recent_messages = repo.get_recent_messages(
            conversation_id=conversation.id,
            limit=window_messages,
        )

        selected: list[tuple[int, str, str]] = []  # (id, role, content)
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
            if selected and total_chars + message_chars > max_characters:
                break
            if not selected and message_chars > max_characters:
                normalized_content = normalized_content[:max_characters]
                message_chars = len(normalized_content)
            selected.append((msg.id, msg.role, normalized_content))
            total_chars += message_chars

        if not selected:
            raise ChatGuidanceServiceError(
                code="chat_context_unavailable",
                message="chat context could not be built",
                details={"conversation_id": str(conversation.id)},
            )

        selected.reverse()
        chat_messages: list[dict[str, str]] = [
            {"role": role, "content": content} for _, role, content in selected
        ]
        context_metadata = ChatContextMetadata(
            message_ids=[item[0] for item in selected],
            message_count=len(selected),
            context_characters=total_chars,
            prompt_version=settings.chat_prompt_version,
        )

        # Construit le contexte avec les champs dynamiques du persona (AC1, AC2, AC3)
        style_markers_str = "; ".join(persona.style_markers) if persona.style_markers else ""
        boundaries_str = "; ".join(persona.boundaries) if persona.boundaries else ""

        # Récupération du résumé du thème natal de l'utilisateur (si disponible)
        natal_summary = None
        current_datetime_str = None
        current_timezone_str = None
        current_location_str = None
        try:
            birth_profile = UserBirthProfileService.get_for_user(db, user_id=user_id)
            natal_chart = UserNatalChartService.get_latest_for_user(db, user_id=user_id)
            degraded_mode = _detect_degraded_mode(birth_profile)
            natal_summary = build_chat_natal_hint(
                natal_result=natal_chart.result,
                degraded_mode=degraded_mode,
            )
            current_context = build_current_prompt_context(birth_profile)
            current_datetime_str = current_context.current_datetime
            current_timezone_str = current_context.current_timezone
            current_location_str = current_context.current_location
        except (UserBirthProfileServiceError, UserNatalChartServiceError):
            # Optionnel : le chat fonctionne même sans thème natal
            logger.debug("chat_natal_summary_not_available user_id=%d", user_id)

        context: dict[str, str | None] = {
            "persona_name": persona.name,
            "persona_tone": str(persona.tone),
            "persona_verbosity": str(persona.verbosity),
            "persona_style_markers": style_markers_str or None,
            "persona_boundaries": boundaries_str or None,
            "natal_chart_summary": natal_summary,
            "conversation_id": str(conversation.id),
            "current_datetime": current_datetime_str,
            "current_timezone": current_timezone_str,
            "current_location": current_location_str,
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
                    db=db,
                )
                (
                    assistant_content,
                    fallback_used,
                    recovery_metadata,
                ) = await ChatGuidanceService._apply_off_scope_recovery_async(
                    db=db,
                    messages=chat_messages,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    assistant_content=assistant_content,
                    persona_profile_code=persona_profile_code,
                )
                # Use a savepoint so concurrent workers carrying the same
                # client_message_id cannot each insert a separate assistant message.
                try:
                    with db.begin_nested():
                        assistant_message = repo.create_message(
                            conversation_id=conversation.id,
                            role="assistant",
                            content=assistant_content,
                            metadata_payload={
                                "attempts": attempts,
                                "fallback_used": fallback_used,
                                "persona_profile_code": persona_profile_code,
                                "context": context_metadata.model_dump(mode="json"),
                                "recovery": recovery_metadata.model_dump(mode="json"),
                            },
                            reply_to_client_message_id=client_message_id,
                        )
                except IntegrityError:
                    # Another concurrent worker already created the assistant message.
                    cached = (
                        repo.get_assistant_by_reply_client_id(conversation.id, client_message_id)
                        if client_message_id
                        else None
                    )
                    if cached:
                        logger.info(
                            "chat_assistant_idempotent_hit request_id=%s client_message_id=%s",
                            request_id,
                            client_message_id,
                        )
                        assistant_message = cached
                    else:
                        raise
                elapsed_seconds = monotonic() - start
                observe_duration("conversation_latency_seconds", elapsed_seconds)
                observe_duration(
                    f"conversation_latency_seconds|persona_profile={persona_profile_code}",
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
                        client_message_id=user_message.client_message_id,
                    ),
                    assistant_message=ChatMessageData(
                        message_id=assistant_message.id,
                        role=assistant_message.role,
                        content=assistant_message.content,
                        created_at=assistant_message.created_at,
                        reply_to_client_message_id=assistant_message.reply_to_client_message_id,
                    ),
                    fallback_used=fallback_used,
                    context=context_metadata,
                    recovery=recovery_metadata,
                )
            except (AIEngineAdapterError, TimeoutError, ConnectionError) as err:
                last_error_code, last_error_message = map_adapter_error_to_codes(err)
                increment_counter("conversation_llm_errors_total", 1.0)
                increment_counter(
                    f"conversation_llm_errors_total|persona_profile={persona_profile_code}",
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
        for conversation, preview, persona_name, last_message_at in conversations:
            # URL encode persona_name for safety in Dicebear URL
            encoded_name = urllib.parse.quote(persona_name) if persona_name else "default"
            avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={encoded_name}"

            items.append(
                ChatConversationSummaryData(
                    conversation_id=conversation.id,
                    persona_id=conversation.persona_id,
                    persona_name=persona_name,
                    avatar_url=avatar_url,
                    status=conversation.status,
                    updated_at=conversation.updated_at,
                    last_message_at=last_message_at,
                    # preview is already truncated to 120 in SQL, but we ensure string type
                    last_message_preview=preview or "",
                )
            )
        return ChatConversationListData(
            conversations=items,
            total=total,
            limit=validated_limit,
            offset=validated_offset,
        )

    @staticmethod
    def get_or_create_conversation_by_persona(
        db: Session,
        *,
        user_id: int,
        persona_id: uuid.UUID,
    ) -> int:
        """
        Retourne l'ID de la conversation active pour (user, persona), ou en crée une nouvelle.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            persona_id: Identifiant du persona.

        Returns:
            L'ID de la conversation (existante ou nouvellement créée).
        """
        repo = ChatRepository(db)
        conversation = repo.get_or_create_conversation_by_persona(
            user_id=user_id, persona_id=persona_id
        )
        return conversation.id

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
            persona_id=conversation.persona_id,
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
