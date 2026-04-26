"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.constants import CHAT_TEMPORARY_UNAVAILABLE_MESSAGE

from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

import logging
import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.entitlement.chat_entitlement_gate import (
    ChatAccessDeniedError,
    ChatEntitlementGate,
    ChatEntitlementResult,
    ChatQuotaExceededError,
)
from app.services.entitlement.entitlement_types import QuotaDefinition
from app.services.llm_generation.chat.chat_guidance_service import (
    ChatConversationHistoryData,
    ChatConversationListData,
    ChatGuidanceService,
    ChatGuidanceServiceError,
    ChatReplyData,
)
from app.services.quota.usage_service import QuotaUsageService

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
