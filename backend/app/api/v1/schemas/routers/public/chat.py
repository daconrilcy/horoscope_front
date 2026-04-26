"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035


import logging
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.llm_generation.chat.chat_guidance_service import (
    ChatConversationHistoryData,
    ChatConversationListData,
    ChatReplyData,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/chat", tags=["chat"])


class ResponseMeta(BaseModel):
    request_id: str


class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: int | None = None
    persona_id: str | None = None
    client_message_id: str | None = None


class QuotaInfo(BaseModel):
    remaining: int | None = None
    limit: int | None = None
    window_end: datetime | None = None


class ChatMessageApiResponse(BaseModel):
    data: ChatReplyData
    meta: ResponseMeta
    quota_info: QuotaInfo = Field(default_factory=QuotaInfo)


class ChatConversationListApiResponse(BaseModel):
    data: ChatConversationListData
    meta: ResponseMeta


class ChatConversationHistoryApiResponse(BaseModel):
    data: ChatConversationHistoryData
    meta: ResponseMeta


class GetOrCreateConversationData(BaseModel):
    conversation_id: int


class GetOrCreateConversationApiResponse(BaseModel):
    data: GetOrCreateConversationData
    meta: ResponseMeta
