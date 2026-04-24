"""Gère les conversations LLM avec l’assistant astrologique et leur contexte applicatif."""

from __future__ import annotations

import asyncio
import json
import logging
import urllib.parse
import uuid
from datetime import date, datetime
from time import monotonic
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.llm.ai_engine_adapter import (
    AIEngineAdapter,
    AIEngineAdapterError,
    assess_off_scope,
    map_adapter_error_to_codes,
)
from app.core.config import settings
from app.core.datetime_provider import datetime_provider
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.db.repositories.user_repository import UserRepository
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.chat_entitlement_gate import ChatEntitlementResult, ChatQuotaExceededError
from app.services.current_context import build_current_prompt_context
from app.services.entitlement_types import QuotaDefinition
from app.services.llm_generation.anonymization_service import (
    LLMAnonymizationError,
    anonymize_text,
)
from app.services.llm_generation.llm_token_usage_service import LlmTokenUsageService
from app.services.llm_generation.natal_interpretation_service import (
    _detect_degraded_mode,
    build_chat_natal_hint,
)
from app.services.quota_usage_service import QuotaExhaustedError, QuotaUsageService
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
)
from app.services.user_natal_chart_service import UserNatalChartService

logger = logging.getLogger(__name__)


class ChatGuidanceServiceError(Exception):
    """Exception levée par le service de chat."""

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
    """Représentation d'un message dans une conversation."""

    message_id: int
    role: str
    content: str
    created_at: datetime
    client_message_id: str | None = None
    reply_to_client_message_id: str | None = None


class ChatReplyData(BaseModel):
    """Données de réponse du service de chat."""

    conversation_id: int
    attempts: int
    user_message: ChatMessageData
    assistant_message: ChatMessageData
    fallback_used: bool
    context: ChatContextMetadata
    recovery: ChatRecoveryMetadata


class ChatContextMetadata(BaseModel):
    """Métadonnées sur le contexte utilisé pour générer la réponse."""

    message_ids: list[int]
    message_count: int
    context_characters: int
    prompt_version: str


class ChatRecoveryMetadata(BaseModel):
    """Métadonnées sur la récupération hors-scope."""

    off_scope_detected: bool
    off_scope_score: float
    recovery_strategy: str
    recovery_applied: bool
    recovery_attempts: int
    recovery_reason: str | None


class ChatConversationSummaryData(BaseModel):
    """Résumé d'une conversation pour la liste."""

    conversation_id: int
    persona_id: uuid.UUID
    persona_name: str | None
    avatar_url: str | None
    status: str
    updated_at: datetime
    last_message_at: datetime | None
    last_message_preview: str


class ChatConversationListData(BaseModel):
    """Liste paginée des conversations."""

    conversations: list[ChatConversationSummaryData]
    total: int
    limit: int
    offset: int


class ChatConversationHistoryData(BaseModel):
    """Historique complet d'une conversation."""

    conversation_id: int
    persona_id: uuid.UUID
    status: str
    updated_at: datetime
    messages: list[ChatMessageData]


class ChatGuidanceService:
    """
    Service de gestion des conversations avec l'assistant astrologique.
    """

    SAFE_FALLBACK_MESSAGE = (
        "Je prefere reformuler prudemment votre demande. "
        "Pouvez-vous preciser votre contexte immediat et votre objectif principal ?"
    )

    _MONTHS_FR = (
        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre",
    )

    _off_scope_events = 0
    _recovery_success_events = 0

    @staticmethod
    def _extract_assistant_text(gateway_result: Any) -> str:
        """Normalize chat output so the UI never receives raw structured JSON."""
        structured_output = getattr(gateway_result, "structured_output", None)
        if isinstance(structured_output, dict):
            message = structured_output.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()

        raw_output = getattr(gateway_result, "raw_output", "")
        if not isinstance(raw_output, str):
            return str(raw_output)

        raw_output = raw_output.strip()
        if not raw_output:
            return raw_output

        try:
            parsed = json.loads(raw_output)
        except (json.JSONDecodeError, TypeError, ValueError):
            return raw_output

        if isinstance(parsed, dict):
            message = parsed.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()

        return raw_output

    @classmethod
    def reset_quality_kpis(cls) -> None:
        """Réinitialise les compteurs de KPI qualité."""
        cls._off_scope_events = 0
        cls._recovery_success_events = 0

    @classmethod
    def get_quality_kpis(cls) -> dict[str, float]:
        """Retourne les indicateurs de qualité du chat."""
        recovery_success_rate = (
            cls._recovery_success_events / cls._off_scope_events if cls._off_scope_events else 0.0
        )
        return {
            "off_scope_count": float(cls._off_scope_events),
            "recovery_success_rate": recovery_success_rate,
        }

    @staticmethod
    def _validate_user_message(message: str) -> str:
        """Valide et nettoie le message utilisateur."""
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
        """Retourne et valide la configuration de contexte."""
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
        """Analyse si une réponse LLM est hors-scope."""
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
    def _derive_user_display_name(email: str) -> str:
        local_part = email.split("@", 1)[0].strip()
        if not local_part:
            return "Utilisateur"
        normalized = local_part.replace(".", " ").replace("_", " ").replace("-", " ")
        words = [part for part in normalized.split() if part]
        if not words:
            return local_part
        return " ".join(word.capitalize() for word in words)

    @classmethod
    def _format_today_label(cls, current_datetime: str | None) -> str:
        if current_datetime:
            return current_datetime.split(" à ", 1)[0]
        today = datetime_provider.today()
        month_name = cls._MONTHS_FR[today.month - 1]
        return f"{today.day:02d} {month_name} {today.year}"

    @staticmethod
    def _compute_user_age(birth_date_iso: str | None, today: date | None = None) -> int | None:
        if not birth_date_iso:
            return None
        try:
            birth_date = date.fromisoformat(birth_date_iso)
        except ValueError:
            return None
        reference = today or datetime_provider.today()
        age = (
            reference.year
            - birth_date.year
            - ((reference.month, reference.day) < (birth_date.month, birth_date.day))
        )
        return age if age >= 0 else None

    @classmethod
    def _build_opening_user_profile(
        cls,
        *,
        email: str,
        birth_date_iso: str | None,
    ) -> str:
        display_name = cls._derive_user_display_name(email)
        age = cls._compute_user_age(birth_date_iso)
        parts = [f"Nom: {display_name}", f"Email: {email}"]
        if age is not None:
            parts.append(f"Âge: {age} ans")
        return " | ".join(parts)

    @staticmethod
    async def _apply_off_scope_recovery_async(
        *,
        db: Session,
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        gateway_result: Any,
        persona_profile_code: str,
        entitlement_result: ChatEntitlementResult | None = None,
    ) -> tuple[str, bool, ChatRecoveryMetadata]:
        """
        Applique les stratégies de récupération si la réponse est hors-scope (async).

        Tente successivement reformulation, retry, puis fallback sécurisé.
        """
        assistant_content = ChatGuidanceService._extract_assistant_text(gateway_result)
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
            recovery_result = await AIEngineAdapter.generate_chat_reply(
                messages=recovery_messages,
                context=context,
                user_id=user_id,
                request_id=f"{request_id}-recovery-1",
                trace_id=trace_id,
                db=db,
            )

            # Record tokens for recovery attempt 1
            ChatGuidanceService._record_tokens(
                db,
                user_id=user_id,
                gateway_result=recovery_result,
                entitlement_result=entitlement_result,
            )

            reformulated = ChatGuidanceService._extract_assistant_text(recovery_result)
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
            recovery_result = await AIEngineAdapter.generate_chat_reply(
                messages=retry_messages,
                context=context,
                user_id=user_id,
                request_id=f"{request_id}-recovery-2",
                trace_id=trace_id,
                db=db,
            )

            # Record tokens for recovery attempt 2
            ChatGuidanceService._record_tokens(
                db,
                user_id=user_id,
                gateway_result=recovery_result,
                entitlement_result=entitlement_result,
            )

            retried = ChatGuidanceService._extract_assistant_text(recovery_result)
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
    def _record_tokens(
        db: Session,
        *,
        user_id: int,
        gateway_result: Any,
        entitlement_result: ChatEntitlementResult | None = None,
    ) -> None:
        """
        Enregistre l'usage des tokens de manière atomique (AC9).
        Si l'enregistrement échoue, l'exception est propagée pour annuler la transaction.
        """
        quota_defs: list[QuotaDefinition] = []
        if entitlement_result and entitlement_result.usage_states:
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
            feature_code="astrologer_chat",
            quotas=quota_defs,
            provider_model=gateway_result.meta.model,
            tokens_in=gateway_result.usage.input_tokens,
            tokens_out=gateway_result.usage.output_tokens,
            request_id=gateway_result.request_id,
            quota_mode="cap",
        )

    @staticmethod
    def _consume_non_token_quotas(
        db: Session,
        *,
        user_id: int,
        entitlement_result: ChatEntitlementResult | None = None,
    ) -> None:
        if entitlement_result is None or not entitlement_result.usage_states:
            return

        non_token_states = sorted(
            (state for state in entitlement_result.usage_states if state.quota_key != "tokens"),
            key=lambda state: (state.period_unit, state.period_value, state.quota_limit),
        )
        for state in non_token_states:
            quota = QuotaDefinition(
                quota_key=state.quota_key,
                quota_limit=state.quota_limit,
                period_unit=state.period_unit,
                period_value=state.period_value,
                reset_mode=state.reset_mode,
            )
            try:
                QuotaUsageService.consume(
                    db,
                    user_id=user_id,
                    feature_code="astrologer_chat",
                    quota=quota,
                    amount=1,
                )
            except QuotaExhaustedError as exc:
                raise ChatQuotaExceededError(
                    quota_key=exc.quota_key,
                    used=exc.used,
                    limit=exc.limit,
                    window_end=state.window_end,
                ) from exc

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
        entitlement_result: ChatEntitlementResult | None = None,
    ) -> ChatReplyData:
        """wrapper synchrone"""
        try:
            return asyncio.run(
                ChatGuidanceService.send_message_async(
                    db,
                    user_id=user_id,
                    message=message,
                    conversation_id=conversation_id,
                    request_id=request_id,
                    persona_id=persona_id,
                    client_message_id=client_message_id,
                    entitlement_result=entitlement_result,
                )
            )
        except Exception as e:
            logger.exception("Exception in send_message (asyncio.run wrapper): %s", str(e))
            raise e

    @staticmethod
    async def _get_default_persona_id(db: Session) -> uuid.UUID:
        """Récupère l'ID du persona par défaut (Astrologue Standard)."""
        from app.infra.db.models.llm.llm_persona import LlmPersonaModel

        stmt = (
            select(LlmPersonaModel.id).where(LlmPersonaModel.name == "Astrologue Standard").limit(1)
        )
        persona_id = db.scalar(stmt)
        if persona_id:
            return persona_id

        stmt = (
            select(LlmPersonaModel.id)
            .where(LlmPersonaModel.enabled)
            .order_by(LlmPersonaModel.created_at)
            .limit(1)
        )
        persona_id = db.scalar(stmt)
        if persona_id:
            return persona_id

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
        """Charge le LlmPersonaModel correspondant au persona_id."""
        from app.infra.db.models.llm.llm_persona import LlmPersonaModel

        if persona_id is not None:
            stmt = select(LlmPersonaModel).where(LlmPersonaModel.id == persona_id).limit(1)
            persona = db.scalar(stmt)
            if persona is not None:
                return persona
            logger.warning("chat_persona_not_found persona_id=%s fallback=default", persona_id)
        else:
            logger.warning("chat_persona_missing persona_id=None fallback=default")

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
        entitlement_result: ChatEntitlementResult | None = None,
    ) -> ChatReplyData:
        """
        Envoie un message et obtient une réponse de l'assistant (async).
        """
        import uuid as uuid_module

        start = monotonic()
        trace_id = trace_id or request_id
        raw_user_message = ChatGuidanceService._validate_user_message(message)
        normalized_message = ChatGuidanceService._anonymize_or_raise(raw_user_message)

        increment_counter("conversation_messages_total", 1.0)
        increment_counter("conversation_chat_messages_total", 1.0)
        repo = ChatRepository(db)

        try:
            if persona_id is None and conversation_id is None:
                resolved_persona_id = await ChatGuidanceService._get_default_persona_id(db)
            elif persona_id is not None:
                resolved_persona_id = (
                    uuid_module.UUID(persona_id) if isinstance(persona_id, str) else persona_id
                )
            else:
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
                # User message exists but no assistant yet: pick up its ID and proceed
                user_message_id = existing_user_msg.id
                user_message_created_at = existing_user_msg.created_at
            else:
                user_message_id = None
                user_message_created_at = None
        else:
            user_message_id = None
            user_message_created_at = None

        persona = ChatGuidanceService._load_persona_sync(db, conversation.persona_id)
        persona_profile_code = persona.name.lower().replace(" ", "-")
        from app.services.persona_config_service import PersonaConfigService

        monitoring_persona_code = PersonaConfigService.get_active(db).profile_code
        increment_counter(
            f"conversation_messages_total|persona_profile={monitoring_persona_code}",
            1.0,
        )
        window_messages, max_characters = ChatGuidanceService._validate_context_config()
        recent_messages = repo.get_recent_messages(
            conversation_id=conversation.id,
            limit=window_messages,
        )

        selected: list[tuple[int, str, str]] = []
        total_chars = 0
        # If user_message_id is NOT None, the message is already in DB and might
        # be in recent_messages.
        # If user_message_id IS None, it's not in DB yet.
        in_db = any(m.id == user_message_id for m in recent_messages) if user_message_id else False

        # If not in DB, we will add 1 message (the current one), so we only take
        # window_messages - 1 from history.
        history_limit = window_messages if in_db else window_messages - 1

        # Take the LATEST messages from the history
        history_to_process = recent_messages[-history_limit:] if history_limit > 0 else []

        for msg in reversed(history_to_process):
            normalized_content = ChatGuidanceService._anonymize_or_raise(msg.content.strip())
            message_chars = len(normalized_content)
            if selected and total_chars + message_chars > max_characters:
                break
            selected.append((msg.id, msg.role, normalized_content))
            total_chars += message_chars

        chat_messages = [{"role": role, "content": content} for _, role, content in selected]
        chat_messages.reverse()

        if not in_db:
            chat_messages.append({"role": "user", "content": normalized_message})
            msg_count = len(selected) + 1
            char_count = total_chars + len(normalized_message)
        else:
            msg_count = len(selected)
            char_count = total_chars

        message_ids = [item[0] for item in selected]
        if not in_db:
            message_ids = [*message_ids, 0]

        context_metadata = ChatContextMetadata(
            message_ids=message_ids,  # dummy current-turn ID until the user message exists
            message_count=msg_count,
            context_characters=char_count,
            prompt_version=settings.chat_prompt_version,
        )

        natal_summary = None
        current_datetime_str = None
        opening_user_profile = None
        user_model = UserRepository(db).get_by_id(user_id)
        is_first_user_turn = msg_count <= 1

        try:
            birth_profile = UserBirthProfileService.get_for_user(db, user_id=user_id)
            current_context = build_current_prompt_context(birth_profile)
            current_datetime_str = current_context.current_datetime
            opening_user_profile = ChatGuidanceService._build_opening_user_profile(
                email=user_model.email, birth_date_iso=birth_profile.birth_date
            )
            if not is_first_user_turn:
                natal_chart = UserNatalChartService.get_latest_for_user(db, user_id=user_id)
                natal_summary = build_chat_natal_hint(
                    natal_chart.result,
                    _detect_degraded_mode(birth_profile),
                )
        except Exception:
            pass

        # Construit le contexte avec les champs dynamiques du persona
        style_markers_str = "; ".join(persona.style_markers) if persona.style_markers else ""
        boundaries_str = "; ".join(persona.boundaries) if persona.boundaries else ""

        context: dict[str, str | None] = {
            "persona_name": persona.name,
            "persona_tone": (
                str(persona.tone.value) if hasattr(persona.tone, "value") else str(persona.tone)
            ),
            "persona_verbosity": (
                str(persona.verbosity.value)
                if hasattr(persona.verbosity, "value")
                else str(persona.verbosity)
            ),
            "persona_style_markers": style_markers_str or None,
            "persona_boundaries": boundaries_str or None,
            "conversation_id": str(conversation.id),
            "chat_turn_stage": "opening" if is_first_user_turn else "follow_up",
            "today_date": ChatGuidanceService._format_today_label(current_datetime_str),
            "current_datetime": current_datetime_str,
            "user_profile_brief": opening_user_profile if is_first_user_turn else None,
            "natal_chart_summary": natal_summary,
        }

        attempts = 0
        max_attempts = max(1, settings.chat_llm_retry_count + 1)
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"

        # Story 66.20 High Issue 1: Resolve user plan for assembly resolution
        from types import SimpleNamespace

        from app.services.effective_entitlement_resolver_service import (
            EffectiveEntitlementResolverService,
        )

        try:
            snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
                db, app_user_id=user_id
            )
            user_plan = snapshot.plan_code
        except Exception:
            user_plan = "free"

        for _ in range(max_attempts):
            attempts += 1
            try:
                gateway_result = await AIEngineAdapter.generate_chat_reply(
                    messages=chat_messages,
                    context=context,
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    db=db,
                    entitlement_result=SimpleNamespace(plan_code=user_plan) if user_plan else None,
                )
                logger.info("Chat reply generated, recording tokens...")
                # Atomic transaction for the whole turn recording (AC9)
                # If anything here fails, BOTH user_message and assistant_message are rolled back
                with db.begin_nested():
                    # 1. Create User Message inside nested transaction if not exists
                    if not user_message_id:
                        user_message = repo.create_message(
                            conversation_id=conversation.id,
                            role="user",
                            content=normalized_message,
                            client_message_id=client_message_id,
                        )
                    else:
                        # Re-fetch or use existing metadata (dummy object for compatibility)
                        from types import SimpleNamespace

                        user_message = SimpleNamespace()
                        user_message.id = user_message_id
                        user_message.role = "user"
                        user_message.content = normalized_message
                        user_message.created_at = user_message_created_at
                        user_message.client_message_id = client_message_id

                    # 2. Consume non-token quotas such as free-tier message caps.
                    ChatGuidanceService._consume_non_token_quotas(
                        db,
                        user_id=user_id,
                        entitlement_result=entitlement_result,
                    )

                    # 3. Record Tokens
                    ChatGuidanceService._record_tokens(
                        db,
                        user_id=user_id,
                        gateway_result=gateway_result,
                        entitlement_result=entitlement_result,
                    )

                    # 4. Off-scope recovery
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
                        gateway_result=gateway_result,
                        persona_profile_code=monitoring_persona_code,
                        entitlement_result=entitlement_result,
                    )

                    # 5. Create Assistant Message
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

                elapsed_seconds = monotonic() - start
                observe_duration("conversation_latency_seconds", elapsed_seconds)
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
                        content=assistant_content,
                        created_at=assistant_message.created_at,
                        reply_to_client_message_id=assistant_message.reply_to_client_message_id,
                    ),
                    fallback_used=fallback_used,
                    context=context_metadata,
                    recovery=recovery_metadata,
                )
            except (AIEngineAdapterError, TimeoutError, ConnectionError) as err:
                last_error_code, last_error_message = map_adapter_error_to_codes(err)
                logger.warning(
                    "chat_generation_error request_id=%s code=%s",
                    request_id,
                    last_error_code,
                )

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
        validated_limit, validated_offset = ChatGuidanceService._validate_pagination(limit, offset)
        repo = ChatRepository(db)
        conversations = repo.list_conversations_with_last_preview_by_user_id(
            user_id,
            limit=validated_limit,
            offset=validated_offset,
        )
        total = repo.count_conversations_by_user_id(user_id)
        items = [
            ChatConversationSummaryData(
                conversation_id=c.id,
                persona_id=c.persona_id,
                persona_name=p_name,
                avatar_url=(
                    "https://api.dicebear.com/7.x/bottts/svg"
                    f"?seed={urllib.parse.quote(p_name or 'default')}"
                ),
                status=c.status,
                updated_at=c.updated_at,
                last_message_at=last_message_at,
                last_message_preview=preview or "",
            )
            for c, preview, p_name, last_message_at in conversations
        ]
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
        repo = ChatRepository(db)
        conversation = repo.get_or_create_active_conversation(
            user_id=user_id,
            persona_id=persona_id,
        )
        return conversation.id

    @staticmethod
    def get_conversation_history(
        db: Session,
        *,
        user_id: int,
        conversation_id: int,
    ) -> ChatConversationHistoryData:
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
