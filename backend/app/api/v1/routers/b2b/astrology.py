from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
    require_authenticated_b2b_client,
)
from app.api.v1.schemas.common import ErrorEnvelope
from app.api.v1.schemas.routers.b2b.astrology import WeeklyBySignApiResponse
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter
from app.services.b2b.api_astrology import (
    _enforce_limits,
    _raise_error,
)
from app.services.b2b.api_entitlement_gate import (
    B2BApiAccessDeniedError,
    B2BApiEntitlementGate,
    B2BApiQuotaExceededError,
)
from app.services.b2b.astrology_service import (
    B2BAstrologyService,
    B2BAstrologyServiceError,
)
from app.services.b2b.editorial_service import B2BEditorialService, B2BEditorialServiceError

router = APIRouter(prefix="/v1/b2b/astrology", tags=["b2b-astrology"])
logger = logging.getLogger(__name__)


@router.get(
    "/weekly-by-sign",
    response_model=WeeklyBySignApiResponse,
    response_model_exclude_none=True,
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

    # Reset the read transaction opened during auth so the quota consumption
    # and downstream generation share an explicit atomic transaction.
    db.rollback()

    try:
        with db.begin():
            increment_counter("b2b_api_calls_total", 1.0)

            gate_result = B2BApiEntitlementGate.check_and_consume(db, account_id=client.account_id)

            if gate_result.path == "canonical_quota":
                # Le canonique a déjà consommé.
                state = gate_result.usage_states[0] if gate_result.usage_states else None
                quota_info = {
                    "source": "canonical",
                    "limit": state.quota_limit if state else None,
                    "remaining": state.remaining if state else None,
                    "window_end": state.window_end if state else None,
                }
            else:
                # path == "canonical_unlimited"
                quota_info = {"source": "canonical"}

            editorial_config = B2BEditorialService.get_active_config(
                db,
                account_id=client.account_id,
            )
            if editorial_config.version_number > 0:
                increment_counter("b2b_editorial_config_used_total", 1.0)
            logger.info(
                (
                    "b2b_editorial_config_applied request_id=%s "
                    "account_id=%s credential_id=%s version=%s"
                ),
                request_id,
                client.account_id,
                client.credential_id,
                editorial_config.version_number,
            )
            data = B2BAstrologyService.get_weekly_by_sign(db, editorial_config=editorial_config)
        return {
            "data": data.model_dump(mode="json"),
            "meta": {"request_id": request_id},
            "quota_info": quota_info,
        }
    except B2BEditorialServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "enterprise_account_not_found" else 422
        return _raise_error(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except (B2BApiAccessDeniedError, B2BApiQuotaExceededError) as error:
        db.rollback()
        if isinstance(error, B2BApiAccessDeniedError):
            status_code = 403
            details = getattr(error, "details", {})
            if "reason_code" not in details:
                details["reason_code"] = error.code
        else:
            # B2BApiQuotaExceededError
            status_code = 429
            details = getattr(error, "details", {})
            if "reason_code" not in details:
                details["reason_code"] = "quota_exhausted"

        return _raise_error(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=details,
        )
    except B2BAstrologyServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "reference_data_unavailable" else 422
        return _raise_error(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
