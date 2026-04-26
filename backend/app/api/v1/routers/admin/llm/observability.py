"""Routeur admin LLM dédié aux endpoints d'observabilité."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.routers.admin.llm.prompts import (
    LlmCallLogListResponse,
    LlmDashboardResponse,
    ReplayPayload,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.llm_observability.admin_observability import (
    get_dashboard as get_dashboard_data,
)
from app.services.llm_observability.admin_observability import (
    list_call_logs as list_call_logs_data,
)
from app.services.llm_observability.admin_observability import (
    purge_logs as purge_logs_data,
)
from app.services.llm_observability.admin_observability import (
    replay_request as replay_request_data,
)

router = APIRouter(prefix="/v1/admin/llm", tags=["admin-llm"])


@router.get("/call-logs", response_model=LlmCallLogListResponse)
def list_call_logs(
    request: Request,
    use_case: Optional[str] = None,
    status: Optional[str] = None,
    prompt_version_id: Optional[uuid.UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Expose les journaux d'appels LLM filtrés pour l'administration."""
    return list_call_logs_data(
        request_id=resolve_request_id(request),
        use_case=use_case,
        status=status,
        prompt_version_id=prompt_version_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size,
        current_user=current_user,
        db=db,
    )


@router.get("/dashboard", response_model=LlmDashboardResponse)
def get_dashboard(
    request: Request,
    period_hours: int = 24,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Expose les métriques d'observabilité LLM pour le tableau de bord admin."""
    return get_dashboard_data(
        request_id=resolve_request_id(request),
        period_hours=period_hours,
        current_user=current_user,
        db=db,
    )


@router.post("/replay", response_model=dict)
async def replay_request(
    request: Request,
    payload: ReplayPayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Expose la relance d'une requête LLM observée."""
    return await replay_request_data(
        request_id=resolve_request_id(request),
        payload=payload,
        current_user=current_user,
        db=db,
    )


@router.post("/call-logs/purge", response_model=dict)
async def purge_logs(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Expose la purge des journaux LLM expirés."""
    return await purge_logs_data(
        request_id=resolve_request_id(request),
        current_user=current_user,
        db=db,
    )


__all__ = ["router"]
