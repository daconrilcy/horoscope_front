"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.services.llm_generation.chat.chat_guidance_service import (
    ChatConversationHistoryData,
    ChatConversationListData,
    ChatReplyData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class ChatMessageRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    message: str
    conversation_id: int | None = None
    persona_id: str | None = None
    client_message_id: str | None = None


class QuotaInfo(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    remaining: int | None = None
    limit: int | None = None
    window_end: datetime | None = None


class ChatMessageApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ChatReplyData
    meta: ResponseMeta
    quota_info: QuotaInfo = Field(default_factory=QuotaInfo)


class ChatConversationListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ChatConversationListData
    meta: ResponseMeta


class ChatConversationHistoryApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ChatConversationHistoryData
    meta: ResponseMeta


class GetOrCreateConversationData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    conversation_id: int


class GetOrCreateConversationApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: GetOrCreateConversationData
    meta: ResponseMeta
