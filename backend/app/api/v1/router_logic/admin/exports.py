"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import csv
import io
import logging
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.request_id import resolve_request_id
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/admin/exports", tags=["admin-exports"])
GEN_EXPORT_COMPAT_DEPRECATION_WARNING = (
    '299 - "Deprecated field: use_case_compat is compatibility-only and will be removed after '
    '2026-09-30. Use feature/subfeature/subscription_plan instead."'
)
GEN_EXPORT_COMPAT_DEPRECATION_SUNSET = "Tue, 30 Sep 2026 23:59:59 GMT"


def _generate_csv_response(
    rows: list[dict[str, Any]],
    fieldnames: list[str],
    filename: str,
    *,
    extra_headers: dict[str, str] | None = None,
):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    if extra_headers:
        headers.update(extra_headers)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers,
    )


def _record_export_audit(
    db: Session,
    request: Request,
    user: AuthenticatedUser,
    export_type: str,
    count: int,
    filters: dict,
):
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=user.id,
            actor_role=user.role,
            action="sensitive_data_exported",
            target_type="system",
            target_id=None,
            status="success",
            details={
                "export_type": export_type,
                "filters": filters,
                "record_count": count,
            },
        ),
    )
    db.commit()
