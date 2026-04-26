"""Expose les endpoints HTTP historiques du moteur LLM sur leur emplacement API canonique."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.router_logic.public.ai import (
    _build_error_response,
    _check_rate_limit,
    _resolve_trace_id,
)
from app.api.v1.schemas.ai import (
    ChatRequest,
    ChatResponse,
    GenerateMeta,
    GenerateRequest,
    GenerateResponse,
    UsageInfo,
)
from app.core.request_id import resolve_request_id
from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.errors import AIEngineError
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/ai", tags=["ai"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: Request,
    body: GenerateRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> GenerateResponse | JSONResponse:
    """
    Generate text using the AI engine.

    Routes to LLMGateway via AIEngineAdapter.
    """
    request_id = body.request_id or resolve_request_id(request)
    trace_id = _resolve_trace_id(request, body.trace_id)

    try:
        _check_rate_limit(current_user.id)

        # Convert GenerateContext to dict for adapter
        context_dict = body.context.model_dump()

        result = await AIEngineAdapter.generate_guidance(
            use_case=body.use_case,
            context=context_dict,
            user_id=current_user.id,
            request_id=request_id,
            trace_id=trace_id,
            locale=body.locale,
            db=db,
        )

        # Return GenerateResponse compatible payload
        usage = UsageInfo(
            input_tokens=getattr(result.usage, "input_tokens", 0)
            if hasattr(result, "usage")
            else 0,
            output_tokens=getattr(result.usage, "output_tokens", 0)
            if hasattr(result, "usage")
            else 0,
            total_tokens=getattr(result.usage, "total_tokens", 0)
            if hasattr(result, "usage")
            else 0,
        )
        return GenerateResponse(
            request_id=request_id,
            trace_id=trace_id,
            provider=getattr(result, "provider", "unknown"),
            model=getattr(result, "model", "unknown"),
            text=result.raw_output,
            usage=usage,
            meta=GenerateMeta(
                cached=getattr(result.meta, "cached", False),
                latency_ms=getattr(result.meta, "latency_ms", 0),
            ),
        )
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
    except Exception as err:
        logger.exception("unexpected_ai_generate_error")
        return JSONResponse(status_code=500, content={"error": {"message": str(err)}})


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> ChatResponse | JSONResponse:
    """
    Generate a chat completion.

    Routes to LLMGateway via AIEngineAdapter.
    SSE streaming is currently not supported via AIEngineAdapter simplified interface.
    """
    request_id = body.request_id or resolve_request_id(request)
    trace_id = _resolve_trace_id(request, body.trace_id)

    if body.output.stream:
        return JSONResponse(
            status_code=501,
            content={"error": {"message": "Streaming not supported in V2 migration path."}},
        )

    try:
        _check_rate_limit(current_user.id)

        # Convert ChatContext to dict for adapter
        context_dict = body.context.model_dump()
        messages_list = [m.model_dump() for m in body.messages]

        response_text = await AIEngineAdapter.generate_chat_reply(
            messages=messages_list,
            context=context_dict,
            user_id=current_user.id,
            request_id=request_id,
            trace_id=trace_id,
            locale=body.locale,
            db=db,
        )

        return ChatResponse(
            request_id=request_id,
            trace_id=trace_id,
            provider="openai",  # Default
            model="AUTO",
            text=response_text,
            usage=UsageInfo(),  # Not easily available from current generate_chat_reply
            meta=GenerateMeta(),
        )
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
    except Exception as err:
        logger.exception("unexpected_ai_chat_error")
        return JSONResponse(status_code=500, content={"error": {"message": str(err)}})
