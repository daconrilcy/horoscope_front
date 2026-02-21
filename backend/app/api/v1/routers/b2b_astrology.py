from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
    require_authenticated_b2b_client,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter
from app.services.b2b_astrology_service import (
    B2BAstrologyService,
    B2BAstrologyServiceError,
    WeeklyBySignData,
)
from app.services.b2b_editorial_service import B2BEditorialService, B2BEditorialServiceError
from app.services.b2b_usage_service import B2BUsageService, B2BUsageServiceError


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class WeeklyBySignApiResponse(BaseModel):
    data: WeeklyBySignData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/b2b/astrology", tags=["b2b-astrology"])
logger = logging.getLogger(__name__)


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


def _enforce_limits(
    *,
    client: AuthenticatedEnterpriseClient,
    request_id: str,
    operation: str,
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"b2b_astrology:global:{operation}", limit=240, window_seconds=60)
        check_rate_limit(
            key=f"b2b_astrology:account:{client.account_id}:{operation}",
            limit=120,
            window_seconds=60,
        )
        check_rate_limit(
            key=f"b2b_astrology:credential:{client.credential_id}:{operation}",
            limit=60,
            window_seconds=60,
        )
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None


@router.get(
    "/weekly-by-sign",
    response_model=WeeklyBySignApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def get_weekly_by_sign(
    request: Request,
    client: AuthenticatedEnterpriseClient = Depends(require_authenticated_b2b_client),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    limit_error = _enforce_limits(client=client, request_id=request_id, operation="weekly_by_sign")
    if limit_error is not None:
        return limit_error

    try:
        increment_counter("b2b_api_calls_total", 1.0)
        B2BUsageService.consume_or_raise(
            db,
            account_id=client.account_id,
            credential_id=client.credential_id,
            request_id=request_id,
            units=1,
        )
        editorial_config = B2BEditorialService.get_active_config(db, account_id=client.account_id)
        if editorial_config.version_number > 0:
            increment_counter("b2b_editorial_config_used_total", 1.0)
        logger.info(
            "b2b_editorial_config_applied request_id=%s account_id=%s credential_id=%s version=%s",
            request_id,
            client.account_id,
            client.credential_id,
            editorial_config.version_number,
        )
        data = B2BAstrologyService.get_weekly_by_sign(db, editorial_config=editorial_config)
        db.commit()
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except B2BEditorialServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "enterprise_account_not_found" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BUsageServiceError as error:
        db.rollback()
        status_code = 429 if error.code == "b2b_quota_exceeded" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BAstrologyServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "reference_data_unavailable" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
