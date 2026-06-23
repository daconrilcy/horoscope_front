# Commentaire global: routes publiques de facade vers les jobs Astral externalises.
"""Routes publiques de facade vers les jobs Astral externalises."""

from __future__ import annotations

import json
import logging
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
logger = logging.getLogger(__name__)
PUBLIC_ASTRAL_ERROR_CODE = "astral_external_service_error"
PUBLIC_ASTRAL_ERROR_MESSAGE = (
    "Le service Astral n'a pas pu produire la lecture pour le moment. Veuillez réessayer plus tard."
)
EXTERNAL_ASTRAL_CLIENT_ERROR_CODES = frozenset(
    {
        "astral_invalid_json",
        "astral_invalid_response",
        "astral_mercure_unavailable",
        "astral_upstream_error",
        "astral_upstream_timeout",
        "astral_upstream_unreachable",
    }
)


def _resolve_astral_error_status(error: AstralIntegrationServiceError) -> int:
    """Mappe les erreurs Astral externes sans contaminer l'auth utilisateur."""
    upstream_status = error.details.get("upstream_http_status")
    if isinstance(upstream_status, int) and 400 <= upstream_status <= 599:
        if _is_external_astral_error(error):
            if upstream_status in {408, 504}:
                return 504
            if upstream_status >= 500 or upstream_status in {401, 403, 429}:
                return 503
            return 502
        return upstream_status
    return resolve_application_error_status(error.code)


def _is_external_astral_error(error: AstralIntegrationServiceError) -> bool:
    """Détermine si l'erreur vient du module Astral externe."""
    return (
        isinstance(error.details.get("upstream_http_status"), int)
        or error.code in EXTERNAL_ASTRAL_CLIENT_ERROR_CODES
    )


def _public_astral_error_payload(
    error: AstralIntegrationServiceError,
) -> tuple[str, str, dict[str, Any]]:
    """Construit une erreur publique sobre sans détail technique Astral."""
    if not _is_external_astral_error(error):
        return error.code, error.message, error.details
    return PUBLIC_ASTRAL_ERROR_CODE, PUBLIC_ASTRAL_ERROR_MESSAGE, {}


TERMINAL_ASTRAL_FAILURE_STATUSES = frozenset({"failed", "safety_rejected", "cancelled", "expired"})


def _nested_reading_status(data: dict[str, Any]) -> str | None:
    """Retourne le statut de lecture imbriqué quand le job externe est completed."""
    result = data.get("result")
    if not isinstance(result, dict):
        return None
    reading = result.get("reading")
    if not isinstance(reading, dict):
        return None
    status = reading.get("status")
    return status if isinstance(status, str) else None


def _has_astral_job_failure(data: dict[str, Any]) -> bool:
    """Détecte les erreurs Astral top-level ou imbriquées dans la lecture."""
    return data.get("status") in TERMINAL_ASTRAL_FAILURE_STATUSES or (
        _nested_reading_status(data) in TERMINAL_ASTRAL_FAILURE_STATUSES
    )


def _public_astral_job_data(data: dict[str, Any]) -> dict[str, Any]:
    """Masque les détails techniques d'un job Astral en erreur avant retour navigateur."""
    if not _has_astral_job_failure(data):
        return data
    public_data = dict(data)
    if public_data.get("status") in TERMINAL_ASTRAL_FAILURE_STATUSES:
        public_data["error"] = {
            "code": PUBLIC_ASTRAL_ERROR_CODE,
            "message": PUBLIC_ASTRAL_ERROR_MESSAGE,
        }
    result = public_data.get("result")
    if isinstance(result, dict):
        public_result = dict(result)
        reading = public_result.get("reading")
        if isinstance(reading, dict) and reading.get("status") in TERMINAL_ASTRAL_FAILURE_STATUSES:
            public_reading = dict(reading)
            public_reading["error"] = {
                "code": PUBLIC_ASTRAL_ERROR_CODE,
                "message": PUBLIC_ASTRAL_ERROR_MESSAGE,
            }
            public_result["reading"] = public_reading
            public_data["result"] = public_result
    return public_data


def _json_for_log(payload: Any) -> str:
    """Sérialise un payload de diagnostic sans casser le logging."""
    try:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    except TypeError:
        return str(payload)


def _log_astral_service_error(
    *,
    event_name: str,
    request_id: str,
    error: AstralIntegrationServiceError,
    context: dict[str, Any],
) -> None:
    """Loggue le détail complet d'une erreur Astral côté backend uniquement."""
    logger.exception(
        "%s request_id=%s error_code=%s error_message=%s details=%s context=%s",
        event_name,
        request_id,
        error.code,
        error.message,
        _json_for_log(error.details),
        _json_for_log(context),
    )


def _log_failed_astral_job(
    *,
    request_id: str,
    data: dict[str, Any],
    context: dict[str, Any],
) -> None:
    """Loggue les jobs Astral terminés en erreur avec leur payload complet."""
    if not _has_astral_job_failure(data):
        return
    logger.error(
        "astral_job_terminal_failure request_id=%s run_id=%s status=%s service_code=%s "
        "error=%s context=%s payload=%s",
        request_id,
        data.get("run_id"),
        data.get("status"),
        data.get("service_code"),
        _json_for_log(data.get("error")),
        _json_for_log(context),
        _json_for_log(data),
    )


@router.post(
    "/jobs",
    response_model=AstralJobApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
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
                chart_calculation_id=payload.chart_calculation_id,
                client_request_id=payload.client_request_id,
                target_language_code=payload.target_language_code,
                audience_level=payload.audience_level,
            ),
        )
        _log_failed_astral_job(
            request_id=request_id,
            data=data,
            context={"product": payload.product, "requested_plan": payload.plan},
        )
        return {"data": _public_astral_job_data(data), "meta": {"request_id": request_id}}
    except ValidationError as error:
        logger.warning(
            "astral_job_request_validation_failed request_id=%s product=%s plan=%s errors_count=%s",
            request_id,
            payload.product,
            payload.plan,
            len(error.errors()),
        )
        return build_error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_astral_job_request",
            message="Astral job request validation failed",
            details={"errors": error.errors()},
        )
    except AstralIntegrationServiceError as error:
        status_code = _resolve_astral_error_status(error)
        _log_astral_service_error(
            event_name="astral_job_submit_failed",
            request_id=request_id,
            error=error,
            context={
                "product": payload.product,
                "requested_plan": payload.plan,
                "status_code": status_code,
            },
        )
        public_code, public_message, public_details = _public_astral_error_payload(error)
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=public_code,
            message=public_message,
            details=public_details,
        )


@router.get(
    "/jobs/{run_id}",
    response_model=AstralJobApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        504: {"model": ErrorEnvelope},
    },
)
async def get_astral_job(
    request: Request,
    run_id: str,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Lit le statut d'un job Astral par polling backend."""
    request_id = resolve_request_id(request)
    try:
        data = await AstralIntegrationService().get_job_status(run_id, db=db, user=current_user)
        _log_failed_astral_job(
            request_id=request_id,
            data=data,
            context={"run_id": run_id},
        )
        return {"data": _public_astral_job_data(data), "meta": {"request_id": request_id}}
    except AstralIntegrationServiceError as error:
        status_code = _resolve_astral_error_status(error)
        _log_astral_service_error(
            event_name="astral_job_status_failed",
            request_id=request_id,
            error=error,
            context={"run_id": run_id, "status_code": status_code},
        )
        public_code, public_message, public_details = _public_astral_error_payload(error)
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=public_code,
            message=public_message,
            details=public_details,
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
