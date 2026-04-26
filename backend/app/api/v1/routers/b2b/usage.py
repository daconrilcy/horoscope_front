from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
    require_authenticated_b2b_client,
)
from app.api.v1.schemas.common import ErrorEnvelope
from app.api.v1.schemas.routers.b2b.usage import (
    B2BUsageSummaryApiResponse,
)
from app.core.rate_limit import RateLimitError
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.api_entitlement_gate import B2BApiAccessDeniedError
from app.services.b2b.api_usage import (
    _enforce_limits,
    _error_response,
    _record_usage_audit,
)
from app.services.b2b.canonical_usage_service import (
    B2BCanonicalUsageSummaryService,
)
from app.services.ops.audit_service import AuditServiceError

router = APIRouter(prefix="/v1/b2b/usage", tags=["b2b-usage"])

# Source de vérité: feature_usage_counters via QuotaUsageService (depuis story 61.22)


@router.get(
    "/summary",
    response_model=B2BUsageSummaryApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def get_b2b_usage_summary(
    request: Request,
    client: AuthenticatedEnterpriseClient = Depends(require_authenticated_b2b_client),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        _enforce_limits(client=client, operation="summary")
        summary = B2BCanonicalUsageSummaryService.get_summary(
            db,
            account_id=client.account_id,
        )
        _record_usage_audit(
            db,
            request_id=request_id,
            action="b2b_usage_summary_read",
            status="success",
            account_id=client.account_id,
            credential_id=client.credential_id,
            details={},
        )
        db.commit()
        return {"data": summary.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except RateLimitError as error:
        db.rollback()
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BApiAccessDeniedError as error:
        db.rollback()
        try:
            _record_usage_audit(
                db,
                request_id=request_id,
                action="b2b_usage_summary_read",
                status="failed",
                account_id=client.account_id,
                credential_id=client.credential_id,
                details={"error_code": error.code},
            )
            db.commit()
        except AuditServiceError:
            db.rollback()
            return _error_response(
                status_code=503,
                request_id=request_id,
                code="audit_unavailable",
                message="audit service is unavailable",
                details={},
            )
        return _error_response(
            status_code=403,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditServiceError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )
