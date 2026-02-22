"""AI Engine FastAPI routes."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.ai_engine.exceptions import AIEngineError
from app.ai_engine.schemas import (
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
)
from app.ai_engine.services import chat_service, generate_service
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/ai", tags=["ai"])


def _resolve_trace_id(request: Request, body_trace_id: str | None) -> str:
    """Resolve trace_id from request or generate new one."""
    if body_trace_id:
        return body_trace_id
    trace_header = request.headers.get("X-Trace-Id")
    if trace_header:
        return trace_header
    return f"trace_{uuid.uuid4().hex[:16]}"


def _build_error_response(
    error: AIEngineError,
    request_id: str,
    trace_id: str,
) -> JSONResponse:
    """Build error response from AIEngineError."""
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                **error.to_dict(),
                "request_id": request_id,
                "trace_id": trace_id,
            }
        },
    )


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: Request,
    body: GenerateRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> GenerateResponse | JSONResponse:
    """
    Generate text using the AI engine.

    Selects appropriate prompt from registry based on use_case,
    renders template with provided context, and calls the LLM provider.
    """
    request_id = body.request_id or resolve_request_id(request)
    trace_id = _resolve_trace_id(request, body.trace_id)

    try:
        response = await generate_service.generate_text(
            body,
            request_id=request_id,
            trace_id=trace_id,
            user_id=current_user.id,
        )
        return response
    except AIEngineError as err:
        increment_counter(
            f"ai_engine_requests_total|use_case={body.use_case}|status=error",
            1.0,
        )
        logger.warning(
            "ai_generate_error request_id=%s trace_id=%s user_id=%d error_type=%s message=%s",
            request_id,
            trace_id,
            current_user.id,
            err.error_type,
            err.message,
        )
        return _build_error_response(err, request_id, trace_id)


@router.post("/chat", response_model=None)
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> ChatResponse | StreamingResponse | JSONResponse:
    """
    Generate a chat completion.

    Supports both streaming (SSE) and non-streaming responses
    based on output.stream flag.
    """
    request_id = body.request_id or resolve_request_id(request)
    trace_id = _resolve_trace_id(request, body.trace_id)

    try:
        if body.output.stream:
            return StreamingResponse(
                chat_service.chat_stream(
                    body,
                    request_id=request_id,
                    trace_id=trace_id,
                    user_id=current_user.id,
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Request-Id": request_id,
                    "X-Trace-Id": trace_id,
                },
            )
        response = await chat_service.chat(
            body,
            request_id=request_id,
            trace_id=trace_id,
            user_id=current_user.id,
        )
        return response
    except AIEngineError as err:
        increment_counter("ai_engine_requests_total|use_case=chat|status=error", 1.0)
        logger.warning(
            "ai_chat_error request_id=%s trace_id=%s user_id=%d error_type=%s message=%s",
            request_id,
            trace_id,
            current_user.id,
            err.error_type,
            err.message,
        )
        return _build_error_response(err, request_id, trace_id)
