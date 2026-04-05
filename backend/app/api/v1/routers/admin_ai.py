from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.admin_ai import (
    AdminAiMetricsResponse,
    AdminAiUseCaseDetailResponse,
    AdminAiUseCaseMetrics,
)
from app.core.request_id import resolve_request_id
from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.session import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/ai", tags=["admin-ai"])


@router.get("/metrics", response_model=AdminAiMetricsResponse)
def get_ai_metrics(
    request: Request,
    period: str = Query(default="30d"),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get aggregated LLM metrics per use case.
    """
    if period == "7d":
        start_date = datetime.now(UTC) - timedelta(days=7)
    else:
        start_date = datetime.now(UTC) - timedelta(days=30)

    # Base aggregation query
    # Using case() for error count calculation to be database-neutral
    error_case = case((LlmCallLogModel.validation_status == LlmValidationStatus.ERROR, 1), else_=0)

    stmt = (
        select(
            LlmCallLogModel.use_case,
            func.count(LlmCallLogModel.id).label("call_count"),
            func.sum(LlmCallLogModel.tokens_in + LlmCallLogModel.tokens_out).label("total_tokens"),
            func.sum(LlmCallLogModel.cost_usd_estimated).label("total_cost"),
            func.avg(LlmCallLogModel.latency_ms).label("avg_latency"),
            func.sum(error_case).label("error_count"),
        )
        .where(LlmCallLogModel.timestamp >= start_date)
        .group_by(LlmCallLogModel.use_case)
    )

    results = db.execute(stmt).all()
    
    metrics = []
    for r in results:
        error_rate = (r.error_count / r.call_count) if r.call_count > 0 else 0
        metrics.append({
            "use_case": r.use_case,
            "call_count": r.call_count,
            "total_tokens": int(r.total_tokens or 0),
            "estimated_cost_usd": float(r.total_cost or 0),
            "avg_latency_ms": int(r.avg_latency or 0),
            "error_rate": float(error_rate),
            "retry_rate": 0,
        })

    return {"data": metrics, "period": period}


@router.get("/metrics/{use_case}", response_model=AdminAiUseCaseDetailResponse)
def get_use_case_detail(
    use_case: str,
    request: Request,
    period: str = Query(default="30d"),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get detailed metrics and trend for a specific use case.
    """
    if period == "7d":
        start_date = datetime.now(UTC) - timedelta(days=7)
    else:
        start_date = datetime.now(UTC) - timedelta(days=30)

    error_case = case((LlmCallLogModel.validation_status == LlmValidationStatus.ERROR, 1), else_=0)

    # 1. Summary
    summary_stmt = (
        select(
            func.count(LlmCallLogModel.id).label("call_count"),
            func.sum(LlmCallLogModel.tokens_in + LlmCallLogModel.tokens_out).label("total_tokens"),
            func.sum(LlmCallLogModel.cost_usd_estimated).label("total_cost"),
            func.avg(LlmCallLogModel.latency_ms).label("avg_latency"),
            func.sum(error_case).label("error_count"),
        )
        .where(LlmCallLogModel.use_case == use_case, LlmCallLogModel.timestamp >= start_date)
    )
    s = db.execute(summary_stmt).first()
    if not s or s.call_count == 0:
        raise HTTPException(status_code=404, detail="No data for this use case")

    error_rate = (s.error_count / s.call_count) if s.call_count > 0 else 0
    metrics = {
        "use_case": use_case,
        "call_count": s.call_count,
        "total_tokens": int(s.total_tokens or 0),
        "estimated_cost_usd": float(s.total_cost or 0),
        "avg_latency_ms": int(s.avg_latency or 0),
        "error_rate": float(error_rate),
    }

    # 2. Trend Data
    date_func = func.date(LlmCallLogModel.timestamp)
    trend_stmt = (
        select(
            date_func,
            func.count(LlmCallLogModel.id),
            func.sum(error_case)
        )
        .where(LlmCallLogModel.use_case == use_case, LlmCallLogModel.timestamp >= start_date)
        .group_by(date_func)
        .order_by(date_func)
    )
    trend_rows = db.execute(trend_stmt).all()
    trend_data = [
        {"date": str(r[0]), "call_count": r[1], "error_count": int(r[2] or 0)} 
        for r in trend_rows
    ]

    # 3. Failed calls
    failed_stmt = (
        select(LlmCallLogModel)
        .where(LlmCallLogModel.use_case == use_case, 
               LlmCallLogModel.validation_status == LlmValidationStatus.ERROR)
        .order_by(LlmCallLogModel.timestamp.desc())
        .limit(10)
    )
    failed_rows = db.scalars(failed_stmt).all()
    recent_failed_calls = [
        {
            "id": str(f.id),
            "timestamp": f.timestamp,
            "error_code": "GENERIC_ERROR",
            "user_id_masked": f.request_id[:8] + "..."
        }
        for f in failed_rows
    ]

    return {
        "use_case": use_case,
        "metrics": metrics,
        "trend_data": trend_data,
        "recent_failed_calls": recent_failed_calls
    }
