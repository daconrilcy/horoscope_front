from __future__ import annotations

import logging
from datetime import datetime
from time import monotonic

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.llm.anonymizer import LLMAnonymizationError, anonymize_text
from app.infra.llm.client import LLMClient
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.persona_config_service import PersonaConfigService

logger = logging.getLogger(__name__)


class ChatGuidanceServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ChatMessageData(BaseModel):
    message_id: int
    role: str
    content: str
    created_at: datetime


class ChatReplyData(BaseModel):
    conversation_id: int
    attempts: int
    user_message: ChatMessageData
    assistant_message: ChatMessageData
    fallback_used: bool
    context: "ChatContextMetadata"
    recovery: "ChatRecoveryMetadata"


class ChatContextMetadata(BaseModel):
    message_ids: list[int]
    message_count: int
    context_characters: int
    prompt_version: str


class ChatRecoveryMetadata(BaseModel):
    off_scope_detected: bool
    off_scope_score: float
    recovery_strategy: str
    recovery_applied: bool
    recovery_attempts: int
    recovery_reason: str | None


class ChatConversationSummaryData(BaseModel):
    conversation_id: int
    status: str
    updated_at: datetime
    last_message_preview: str


class ChatConversationListData(BaseModel):
    conversations: list[ChatConversationSummaryData]
    total: int
    limit: int
    offset: int


class ChatConversationHistoryData(BaseModel):
    conversation_id: int
    status: str
    updated_at: datetime
    messages: list[ChatMessageData]


class ChatGuidanceService:
    _off_scope_events = 0
    _recovery_success_events = 0

    SAFE_FALLBACK_MESSAGE = (
        "Je prefere reformuler prudemment votre demande. "
        "Pouvez-vous preciser votre contexte immediat et votre objectif principal ?"
    )

    @classmethod
    def reset_quality_kpis(cls) -> None:
        cls._off_scope_events = 0
        cls._recovery_success_events = 0

    @classmethod
    def get_quality_kpis(cls) -> dict[str, float]:
        recovery_success_rate = (
            cls._recovery_success_events / cls._off_scope_events if cls._off_scope_events else 0.0
        )
        return {
            "off_scope_count": float(cls._off_scope_events),
            "recovery_success_rate": recovery_success_rate,
        }

    @staticmethod
    def _validate_user_message(message: str) -> str:
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
        if mode == "reformulate":
            instruction = (
                "The previous answer appears out-of-scope. Reformulate in French, stay practical, "
                "and answer the user's intent directly in 3 short sentences."
            )
        else:
            instruction = (
                "Previous reformulation is still out-of-scope. "
                "Provide a concise, relevant French answer. "
                "Do not include system markers, role prefixes, or prompt transcript."
            )
        lines = [
            "[recovery_prompt_version:offscope-v1]",
            instruction,
            "Conversation context:",
            prompt,
            "Previous assistant answer:",
            ChatGuidanceService._anonymize_or_raise(previous_reply),
        ]
        return "\n".join(lines)

    @staticmethod
    def _anonymize_or_raise(text: str) -> str:
        try:
            return anonymize_text(text)
        except LLMAnonymizationError as error:
            raise ChatGuidanceServiceError(
                code="llm_anonymization_failed",
                message="llm payload anonymization failed",
                details={},
            ) from error

    @staticmethod
    def _apply_off_scope_recovery(
        *,
        client: LLMClient,
        prompt: str,
        assistant_content: str,
        persona_profile_code: str,
    ) -> tuple[str, bool, ChatRecoveryMetadata]:
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
            reformulated = client.generate_reply(
                prompt=ChatGuidanceService._build_recovery_prompt(
                    prompt,
                    assistant_content,
                    "reformulate",
                ),
                timeout_seconds=settings.chat_llm_timeout_seconds,
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
        except (TimeoutError, ConnectionError):
            logger.warning("chat_recovery_error strategy=reformulate")

        try:
            recovery_attempts += 1
            retried = client.generate_reply(
                prompt=ChatGuidanceService._build_recovery_prompt(
                    prompt,
                    assistant_content,
                    "retry_once",
                ),
                timeout_seconds=settings.chat_llm_timeout_seconds,
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
        except (TimeoutError, ConnectionError):
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
        llm_client: LLMClient | None = None,
        request_id: str = "n/a",
    ) -> ChatReplyData:
        start = monotonic()
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
        prompt, context_metadata = ChatGuidanceService._build_prompt_and_context_metadata(
            repo=repo,
            conversation_id=conversation.id,
            persona_line=persona_config.to_prompt_line(),
        )
        client = llm_client or LLMClient()
        attempts = 0
        max_attempts = max(1, settings.chat_llm_retry_count + 1)
        last_error_code = "llm_unavailable"
        last_error_message = "llm provider is unavailable"
        for _ in range(max_attempts):
            attempts += 1
            try:
                assistant_content = client.generate_reply(
                    prompt=prompt,
                    timeout_seconds=settings.chat_llm_timeout_seconds,
                )
                (
                    assistant_content,
                    fallback_used,
                    recovery_metadata,
                ) = ChatGuidanceService._apply_off_scope_recovery(
                    client=client,
                    prompt=prompt,
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
