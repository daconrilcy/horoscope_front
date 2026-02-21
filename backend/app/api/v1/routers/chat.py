from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.chat_guidance_service import (
    ChatConversationHistoryData,
    ChatConversationListData,
    ChatGuidanceService,
    ChatGuidanceServiceError,
    ChatReplyData,
)
from app.services.quota_service import QuotaService, QuotaServiceError


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


class ChatMessageApiResponse(BaseModel):
    data: ChatReplyData
    meta: ResponseMeta


class ChatConversationListApiResponse(BaseModel):
    data: ChatConversationListData
    meta: ResponseMeta


class ChatConversationHistoryApiResponse(BaseModel):
    data: ChatConversationHistoryData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/chat", tags=["chat"])


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
    if current_user.role != "user":
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role is not allowed",
                    "details": {"required_roles": "user"},
                    "request_id": request_id,
                }
            },
        )

    try:
        parsed_payload = ChatMessageRequest.model_validate(payload)
        QuotaService.consume_quota_or_raise(
            db,
            user_id=current_user.id,
            request_id=request_id,
        )
        response = ChatGuidanceService.send_message(
            db=db,
            user_id=current_user.id,
            message=parsed_payload.message,
            conversation_id=parsed_payload.conversation_id,
            request_id=request_id,
        )
        db.commit()
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
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
    except QuotaServiceError as error:
        db.rollback()
        if error.code == "quota_exceeded":
            status_code = 429
        elif error.code == "no_active_subscription":
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
    if current_user.role != "user":
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role is not allowed",
                    "details": {"required_roles": "user"},
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
    if current_user.role != "user":
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role is not allowed",
                    "details": {"required_roles": "user"},
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
