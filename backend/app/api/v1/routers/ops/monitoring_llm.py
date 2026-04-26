"""
Router pour le monitoring opérationnel LLM (Story 66.37).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_ops_user,
)
from app.api.v1.schemas.routers.ops.monitoring_llm import (
    LlmOpsMonitoringApiResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.llm_observability.monitoring_service import (
    LlmOpsMonitoringService,
)

router = APIRouter(prefix="/v1/ops/monitoring/llm", tags=["ops-monitoring-llm"])


@router.get(
    "/dashboard",
    response_model=LlmOpsMonitoringApiResponse,
)
def get_llm_ops_dashboard(
    request: Request,
    window: str = Query(default="24h"),
    current_user: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Récupère le tableau de bord d'exploitation LLM (AC1, AC2, AC15).
    """
    request_id = resolve_request_id(request)
    data = LlmOpsMonitoringService.get_llm_ops_data(db, window=window)
    return {"data": data, "meta": {"request_id": request_id}}
