from __future__ import annotations

from typing import Any

from fastapi import Depends, Header, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter
from app.services.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.enterprise_credentials_service import (
    EnterpriseCredentialsService,
    EnterpriseCredentialsServiceError,
)


class AuthenticatedEnterpriseClient(BaseModel):
    account_id: int
    credential_id: int
    key_prefix: str


class EnterpriseApiKeyAuthenticationError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


def _record_auth_failure_audit(
    db: Session,
    *,
    request_id: str,
    action: str,
    target_id: str | None,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=None,
            actor_role="enterprise_client",
            action=action,
            target_type="enterprise_api_credential",
            target_id=target_id,
            status="failed",
            details=details,
        ),
    )


def require_authenticated_b2b_client(
    request: Request,
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db_session),
) -> AuthenticatedEnterpriseClient:
    request_id = resolve_request_id(request)
    key = (x_api_key or "").strip()
    if not key:
        increment_counter("b2b_api_auth_failures_total", 1.0)
        raise EnterpriseApiKeyAuthenticationError(
            code="missing_api_key",
            message="missing api key",
            status_code=401,
            details={},
        )

    try:
        authenticated = EnterpriseCredentialsService.authenticate_api_key(db, api_key=key)
        return AuthenticatedEnterpriseClient(
            account_id=authenticated.account_id,
            credential_id=authenticated.credential_id,
            key_prefix=authenticated.key_prefix,
        )
    except EnterpriseCredentialsServiceError as error:
        increment_counter("b2b_api_auth_failures_total", 1.0)
        audit_action = (
            "b2b_api_auth_revoked" if error.code == "revoked_api_key" else "b2b_api_auth_failed"
        )
        target_id = None
        try:
            _record_auth_failure_audit(
                db,
                request_id=request_id,
                action=audit_action,
                target_id=target_id,
                details={"error_code": error.code},
            )
            db.commit()
        except AuditServiceError:
            db.rollback()
            increment_counter("b2b_api_auth_audit_failures_total", 1.0)

        status_code = (
            403 if error.code in {"revoked_api_key", "enterprise_account_inactive"} else 401
        )
        raise EnterpriseApiKeyAuthenticationError(
            code=error.code,
            message=error.message,
            status_code=status_code,
            details=error.details,
        ) from error
