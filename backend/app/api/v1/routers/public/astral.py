# Commentaire global: routes publiques de facade vers les jobs Astral externalises.
"""Routes publiques de facade vers les jobs Astral externalises."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.errors import build_error_response
from app.api.errors.catalog import resolve_application_error_status
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.astral import (
    AstralJobApiResponse,
    AstralJobCreateRequest,
)
from app.services.astral.integration_service import (
    AstralIntegrationService,
    AstralIntegrationServiceError,
    AstralJobCommand,
)

router = APIRouter(prefix="/v1/astral", tags=["astral"])


@router.post(
    "/jobs",
    response_model=AstralJobApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        504: {"model": ErrorEnvelope},
    },
)
async def submit_astral_job(
    request: Request,
    payload: AstralJobCreateRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Soumet un job Astral sans exposer le service externe au navigateur."""
    request_id = resolve_request_id(request)
    try:
        data = await AstralIntegrationService().submit_job(
            db=db,
            user=current_user,
            command=AstralJobCommand(
                product=payload.product,
                plan=payload.plan,
                period=payload.period,
                birth_profile_id=payload.birth_profile_id,
                client_request_id=payload.client_request_id,
                target_language_code=payload.target_language_code,
                audience_level=payload.audience_level,
            ),
        )
        return {"data": data, "meta": {"request_id": request_id}}
    except ValidationError as error:
        return build_error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_astral_job_request",
            message="Astral job request validation failed",
            details={"errors": error.errors()},
        )
    except AstralIntegrationServiceError as error:
        return build_error_response(
            status_code=resolve_application_error_status(error.code),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/jobs/{run_id}",
    response_model=AstralJobApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        504: {"model": ErrorEnvelope},
    },
)
async def get_astral_job(
    request: Request,
    run_id: str,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    """Lit le statut d'un job Astral par polling backend."""
    request_id = resolve_request_id(request)
    _ = current_user
    try:
        data = await AstralIntegrationService().get_job_status(run_id)
        return {"data": data, "meta": {"request_id": request_id}}
    except AstralIntegrationServiceError as error:
        return build_error_response(
            status_code=resolve_application_error_status(error.code),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/jobs/{run_id}/events",
    response_class=StreamingResponse,
    responses={401: {"model": ErrorEnvelope}, 503: {"model": ErrorEnvelope}},
)
async def get_astral_job_events(
    request: Request,
    run_id: str,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    """Proxy le flux SSE Mercure sans exposer le hub Astral au navigateur."""
    service = AstralIntegrationService()
    tenant_id = str(current_user.id)

    return StreamingResponse(
        service.stream_job_events(
            tenant_id=tenant_id,
            run_id=run_id,
            is_disconnected=request.is_disconnected,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
