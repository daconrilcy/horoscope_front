from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.constants import CHAT_TEMPORARY_UNAVAILABLE_MESSAGE
from app.api.v1.schemas.common import ErrorEnvelope
from app.api.v1.schemas.routers.public.chat import (
    ChatConversationHistoryApiResponse,
    ChatConversationListApiResponse,
    ChatMessageRequest,
    GetOrCreateConversationApiResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.entitlement.chat_entitlement_gate import (
    ChatAccessDeniedError,
    ChatEntitlementGate,
    ChatQuotaExceededError,
)
from app.services.llm_generation.chat.chat_guidance_service import (
    ChatGuidanceService,
    ChatGuidanceServiceError,
)
from app.services.llm_generation.chat.public_chat import (
    _build_post_turn_quota_info,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/chat", tags=["chat"])


@router.post(
    "/messages",
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
    logger.info("TOP OF send_chat_message request_id=%s user_id=%s", request_id, current_user.id)
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
        logger.info("Validating payload...")
        parsed_payload = ChatMessageRequest.model_validate(payload)

        logger.info("Checking access...")
        entitlement_result = ChatEntitlementGate.check_access(db, user_id=current_user.id)

        logger.info("Sending message...")
        response = ChatGuidanceService.send_message(
            db=db,
            user_id=current_user.id,
            message=parsed_payload.message,
            conversation_id=parsed_payload.conversation_id,
            request_id=request_id,
            persona_id=parsed_payload.persona_id,
            client_message_id=parsed_payload.client_message_id,
            entitlement_result=entitlement_result,
        )
        quota_info = _build_post_turn_quota_info(
            db,
            user_id=current_user.id,
            result=entitlement_result,
        )
        logger.info("Message sent, preparing final dict...")

        # Plain dict to bypass any return validation
        res = {
            "data": {
                "conversation_id": response.conversation_id,
                "attempts": response.attempts,
                "user_message": response.user_message.model_dump(mode="json"),
                "assistant_message": response.assistant_message.model_dump(mode="json"),
                "fallback_used": response.fallback_used,
                "context": response.context.model_dump(mode="json"),
                "recovery": response.recovery.model_dump(mode="json"),
            },
            "meta": {"request_id": request_id},
            "quota_info": quota_info.model_dump(mode="json"),
        }
        db.commit()
        return res
    except ValidationError as error:
        logger.error("Chat API validation error: %s", error.json())
        logger.error("Failed payload: %s", str(payload))
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
            message = CHAT_TEMPORARY_UNAVAILABLE_MESSAGE
        elif error.code == "conversation_not_found":
            status_code = 404
            message = error.message
        elif error.code == "conversation_forbidden":
            status_code = 403
            message = error.message
        else:
            status_code = 422
            message = error.message
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )
    except Exception as error:
        logger.exception("Unexpected error in send_chat_message: %s", str(error))
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": str(error),
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
