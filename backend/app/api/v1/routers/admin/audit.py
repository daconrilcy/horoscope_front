# Commentaire global: ce routeur expose les surfaces admin d'audit sans payload sensible.
from __future__ import annotations

import csv
import io
import json
import logging
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.errors import raise_api_error
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.admin.audit import (
    AdminAuditExportRequest,
    AdminAuditLogResponse,
    AdminReplaySnapshotV1MetadataResponse,
    AdminReplaySnapshotV1ReplayAttemptResponse,
)
from app.services.ops.admin_audit import (
    _build_export_filename,
    _get_audit_query,
    _mask_email,
    _mask_target_id,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.replay_snapshot_v1_service import (
    ReplaySnapshotMetadata,
    ReplaySnapshotResult,
    ReplaySnapshotV1Service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/audit", tags=["admin-audit"])
AuditPeriod = Literal["7d", "30d", "all"]


def get_replay_snapshot_v1_service() -> type[ReplaySnapshotV1Service]:
    """Retourne le service canonique du cycle de vie replay snapshot."""
    return ReplaySnapshotV1Service


def raise_unavailable_replay_snapshot(result: ReplaySnapshotResult) -> None:
    """Mappe les etats service non disponibles vers les erreurs HTTP stables."""
    if result.status == "not_found":
        raise_api_error(status_code=404, message="Replay snapshot not found")
    if result.status in {"expired", "already_purged"}:
        raise_api_error(
            status_code=410,
            code="replay_snapshot_unavailable",
            message="Replay snapshot is no longer available",
            details={"status": result.status},
        )
    raise_api_error(
        status_code=400,
        message="Replay snapshot operation failed",
        details={"status": result.status},
    )


def to_replay_snapshot_response(
    metadata: ReplaySnapshotMetadata,
    *,
    audit_event_id: int | None = None,
    replay_attempt_id: str | None = None,
) -> AdminReplaySnapshotV1MetadataResponse:
    """Projette les metadonnees internes vers le contrat admin redige."""
    return AdminReplaySnapshotV1MetadataResponse(
        snapshot_id=metadata.snapshot_id,
        status=metadata.status,
        created_at=metadata.created_at,
        expires_at=metadata.expires_at,
        redaction_state=metadata.redaction_state,
        version_identity=metadata.version_identity or None,
        provenance_refs=metadata.provenance or None,
        audit_event_id=audit_event_id,
        replay_attempt_id=replay_attempt_id,
    )


@router.get("", response_model=AdminAuditLogResponse)
def get_audit_log(
    request: Request,
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    period: AuditPeriod | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, le=100),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get global audit logs with filters and pagination.
    """
    stmt = _get_audit_query(actor, action, target_type, period)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    results = db.execute(stmt.offset((page - 1) * per_page).limit(per_page)).all()

    data = []
    for r in results:
        data.append(
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "actor_email_masked": _mask_email(r.actor_email),
                "actor_role": r.actor_role,
                "action": r.action,
                "target_type": r.target_type,
                "target_id_masked": _mask_target_id(r.target_id, r.target_type),
                "status": r.status,
                "details": r.details or {},
            }
        )

    return {
        "data": data,
        "total": total or 0,
        "page": page,
        "per_page": per_page,
    }


@router.get(
    "/replay_snapshot_v1/{snapshot_id}",
    response_model=AdminReplaySnapshotV1MetadataResponse,
)
def get_replay_snapshot_v1_metadata(
    snapshot_id: UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
    service: type[ReplaySnapshotV1Service] = Depends(get_replay_snapshot_v1_service),
) -> AdminReplaySnapshotV1MetadataResponse:
    """Retourne les metadonnees admin redigees d'un snapshot replay."""
    result = service.get_snapshot_metadata(
        db,
        snapshot_id=snapshot_id,
        request_id=resolve_request_id(request),
        actor_user_id=current_user.id,
        actor_role=current_user.role,
        audit=True,
    )
    if result.status != "success" or result.metadata is None:
        if result.audit_event_id is not None:
            db.commit()
        raise_unavailable_replay_snapshot(result)
    db.commit()
    return to_replay_snapshot_response(result.metadata, audit_event_id=result.audit_event_id)


@router.post(
    "/replay_snapshot_v1/{snapshot_id}/replay-attempt",
    response_model=AdminReplaySnapshotV1ReplayAttemptResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_replay_snapshot_v1_attempt(
    snapshot_id: UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
    service: type[ReplaySnapshotV1Service] = Depends(get_replay_snapshot_v1_service),
) -> JSONResponse:
    """Accepte une tentative de replay admin sans retourner le payload source."""
    result = service.start_replay_attempt(
        db,
        snapshot_id=snapshot_id,
        request_id=resolve_request_id(request),
        actor_user_id=current_user.id,
        actor_role=current_user.role,
    )
    if result.status != "success" or result.metadata is None or result.replay_attempt_id is None:
        if result.audit_event_id is not None:
            db.commit()
        raise_unavailable_replay_snapshot(result)
    db.commit()
    response = to_replay_snapshot_response(
        result.metadata,
        audit_event_id=result.audit_event_id,
        replay_attempt_id=result.replay_attempt_id,
    )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=response.model_dump(mode="json", exclude_none=True),
    )


@router.delete(
    "/replay_snapshot_v1/{snapshot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def purge_replay_snapshot_v1(
    snapshot_id: UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
    service: type[ReplaySnapshotV1Service] = Depends(get_replay_snapshot_v1_service),
) -> Response:
    """Purge manuellement un snapshot replay via le service canonique audite."""
    result = service.purge_snapshot(
        db,
        snapshot_id=snapshot_id,
        request_id=resolve_request_id(request),
        actor_user_id=current_user.id,
        actor_role=current_user.role,
    )
    if result.status != "success":
        if result.audit_event_id is not None:
            db.commit()
        raise_unavailable_replay_snapshot(result)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/export")
def export_audit_log(
    request: Request,
    payload: AdminAuditExportRequest,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Export filtered audit logs to CSV.
    """
    stmt = _get_audit_query(payload.actor, payload.action, payload.target_type, payload.period)

    # Limit to 5000 for MVP
    results = db.execute(stmt.limit(5000)).all()

    # 1. Audit the export action itself
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="audit_log_exported",
            target_type="system",
            target_id=None,
            status="success",
            details={
                "filters": payload.model_dump(),
                "record_count": len(results),
            },
        ),
    )
    db.commit()

    # 2. Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)

    header = [
        "ID",
        "Timestamp",
        "Actor Email (Masked)",
        "Actor Role",
        "Action",
        "Target Type",
        "Target ID (Masked)",
        "Status",
        "Details (JSON)",
    ]
    writer.writerow(header)

    for r in results:
        writer.writerow(
            [
                r.id,
                r.timestamp.isoformat(),
                _mask_email(r.actor_email),
                r.actor_role,
                r.action,
                r.target_type,
                _mask_target_id(r.target_id, r.target_type),
                r.status,
                json.dumps(r.details or {}, ensure_ascii=False, sort_keys=True),
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={_build_export_filename(payload.period)}"
        },
    )
