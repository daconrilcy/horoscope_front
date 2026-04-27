from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.errors import build_error_response
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.guidance import (
    ContextualGuidanceApiResponse,
    ContextualGuidanceRequest,
    GuidanceApiResponse,
    GuidanceRequest,
)
from app.services.llm_generation.guidance.guidance_service import (
    GuidanceService,
    GuidanceServiceError,
)

router = APIRouter(prefix="/v1/guidance", tags=["guidance"])


@router.post(
    "",
    response_model=GuidanceApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def request_guidance(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"user", "admin"}:
        return build_error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "user, admin"},
        )
    try:
        parsed_payload = GuidanceRequest.model_validate(payload)
        response = GuidanceService.request_guidance(
            db=db,
            user_id=current_user.id,
            period=parsed_payload.period,
            conversation_id=parsed_payload.conversation_id,
            request_id=request_id,
        )
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return build_error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_guidance_request",
            message="guidance request validation failed",
            details={"errors": error.errors()},
        )
    except GuidanceServiceError as error:
        db.rollback()
        if error.code in {"llm_timeout", "llm_unavailable"}:
            status_code = 503
        elif error.code == "conversation_not_found":
            status_code = 404
        elif error.code == "conversation_forbidden":
            status_code = 403
        elif error.code == "missing_birth_profile":
            status_code = 404
        else:
            status_code = 422
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.post(
    "/contextual",
    response_model=ContextualGuidanceApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def request_contextual_guidance(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"user", "admin"}:
        return build_error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "user, admin"},
        )
    try:
        parsed_payload = ContextualGuidanceRequest.model_validate(payload)
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=current_user.id,
            situation=parsed_payload.situation,
            objective=parsed_payload.objective,
            time_horizon=parsed_payload.time_horizon,
            conversation_id=parsed_payload.conversation_id,
            request_id=request_id,
        )
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return build_error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_contextual_guidance_request",
            message="contextual guidance request validation failed",
            details={"errors": error.errors()},
        )
    except GuidanceServiceError as error:
        db.rollback()
        if error.code in {"llm_timeout", "llm_unavailable"}:
            status_code = 503
        elif error.code in {"conversation_not_found", "missing_birth_profile"}:
            status_code = 404
        elif error.code == "conversation_forbidden":
            status_code = 403
        else:
            status_code = 422
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
