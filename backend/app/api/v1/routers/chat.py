from __future__ import annotations

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
from app.services.chat_entitlement_gate import (
    ChatAccessDeniedError,
    ChatEntitlementGate,
    ChatEntitlementResult,
    ChatQuotaExceededError,
)
from app.services.chat_guidance_service import (
    ChatConversationHistoryData,
    ChatConversationListData,
    ChatGuidanceService,
    ChatGuidanceServiceError,
    ChatReplyData,
)


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


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


router = APIRouter(prefix="/v1/chat", tags=["chat"])


def _build_quota_info(result: ChatEntitlementResult) -> QuotaInfo:
    if result.path in ("canonical_quota", "canonical_unlimited") and result.usage_states:
        state = result.usage_states[0]
        return QuotaInfo(
            remaining=state.remaining,
            limit=state.quota_limit,
            window_end=state.window_end,
        )
    return QuotaInfo()


@router.post(
    "/messages",
    response_model=ChatMessageApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def send_chat_message(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"user", "admin"}:
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role is not allowed",
                    "details": {"required_roles": "user, admin"},
                    "request_id": request_id,
                }
            },
        )

    try:
        parsed_payload = ChatMessageRequest.model_validate(payload)

        entitlement_result = ChatEntitlementGate.check_and_consume(db, user_id=current_user.id)

        quota_info = _build_quota_info(entitlement_result)

        response = ChatGuidanceService.send_message(
            db=db,
            user_id=current_user.id,
            message=parsed_payload.message,
            conversation_id=parsed_payload.conversation_id,
            request_id=request_id,
            persona_id=parsed_payload.persona_id,
            client_message_id=parsed_payload.client_message_id,
        )
        db.commit()
        return {
            "data": response.model_dump(mode="json"),
            "meta": {"request_id": request_id},
            "quota_info": quota_info.model_dump(mode="json"),
        }
    except ValidationError as error:
        db.rollback()
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "invalid_chat_request",
                    "message": "chat request validation failed",
                    "details": {"errors": error.errors()},
                    "request_id": request_id,
                }
            },
        )
    except ChatQuotaExceededError as error:
        db.rollback()
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "chat_quota_exceeded",
                    "message": "quota de messages chat épuisé",
                    "details": {
                        "quota_key": error.quota_key,
                        "used": error.used,
                        "limit": error.limit,
                        "reason_code": "quota_exhausted",
                        "window_end": error.window_end.isoformat() if error.window_end else None,
                    },
                    "request_id": request_id,
                }
            },
        )
    except ChatAccessDeniedError as error:
        db.rollback()
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "chat_access_denied",
                    "message": "accès au chat refusé",
                    "details": {
                        "reason": error.reason,
                        "reason_code": error.reason_code,
                        "billing_status": error.billing_status,
                    },
                    "request_id": request_id,
                }
            },
        )
    except ChatGuidanceServiceError as error:
        db.rollback()
        if error.code in {"llm_timeout", "llm_unavailable"}:
            status_code = 503
        elif error.code == "conversation_not_found":
            status_code = 404
        elif error.code == "conversation_forbidden":
            status_code = 403
        else:
            status_code = 422
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )


@router.get(
    "/conversations",
    response_model=ChatConversationListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def list_chat_conversations(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"user", "admin"}:
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role is not allowed",
                    "details": {"required_roles": "user, admin"},
                    "request_id": request_id,
                }
            },
        )

    try:
        response = ChatGuidanceService.list_conversations(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ChatGuidanceServiceError as error:
        db.rollback()
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ChatConversationHistoryApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
    },
)
def get_chat_conversation_history(
    request: Request,
    conversation_id: int,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"user", "admin"}:
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role is not allowed",
                    "details": {"required_roles": "user, admin"},
                    "request_id": request_id,
                }
            },
        )

    try:
        response = ChatGuidanceService.get_conversation_history(
            db=db,
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ChatGuidanceServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "conversation_not_found" else 403
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )


@router.post(
    "/conversations/by-persona/{persona_id}",
    response_model=GetOrCreateConversationApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def get_or_create_conversation_by_persona(
    request: Request,
    persona_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"user", "admin"}:
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role is not allowed",
                    "details": {"required_roles": "user, admin"},
                    "request_id": request_id,
                }
            },
        )

    try:
        conversation_id = ChatGuidanceService.get_or_create_conversation_by_persona(
            db=db,
            user_id=current_user.id,
            persona_id=persona_id,
        )
        db.commit()
        return {
            "data": {"conversation_id": conversation_id},
            "meta": {"request_id": request_id},
        }
    except ChatGuidanceServiceError as error:
        db.rollback()
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )
