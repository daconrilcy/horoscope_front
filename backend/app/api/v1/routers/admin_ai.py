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
)
from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.session import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/ai", tags=["admin-ai"])


_AI_METRIC_CATEGORY_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "key": "natal_theme_short_free",
        "display_name": "Theme natal short free",
        "raw_use_cases": ("natal_long_free",),
    },
    {
        "key": "natal_theme_short_paid",
        "display_name": "Theme natal short basic/premium",
        "raw_use_cases": ("natal_interpretation_short",),
    },
    {
        "key": "natal_theme_complete_paid",
        "display_name": "Theme natal complete basic/premium",
        "raw_use_cases": ("natal_interpretation",),
    },
    {
        "key": "thematic_consultations",
        "display_name": "Consultations thematiques",
        "raw_use_cases": (
            "event_guidance",
            "natal_psy_profile",
            "natal_shadow_integration",
            "natal_leadership_workstyle",
            "natal_creativity_joy",
            "natal_relationship_style",
            "natal_community_networks",
            "natal_values_security",
            "natal_evolution_path",
        ),
    },
    {
        "key": "astrologer_chat",
        "display_name": "Chat astrologue",
        "raw_use_cases": ("chat_astrologer", "chat"),
    },
    {
        "key": "daily_horoscope",
        "display_name": "Horoscope du jour",
        "raw_use_cases": (
            "guidance_daily",
            "horoscope_daily_free",
            "horoscope_daily_full",
            "daily_prediction",
        ),
    },
    {
        "key": "weekly_horoscope",
        "display_name": "Horoscope hebdomadaire",
        "raw_use_cases": ("guidance_weekly",),
    },
)

_AI_METRIC_CATEGORY_BY_KEY = {item["key"]: item for item in _AI_METRIC_CATEGORY_DEFINITIONS}
_AI_METRIC_CATEGORY_BY_RAW_USE_CASE = {
    raw_use_case: item
    for item in _AI_METRIC_CATEGORY_DEFINITIONS
    for raw_use_case in item["raw_use_cases"]
}


def _derive_failed_call_error_code(log: LlmCallLogModel) -> str:
    if log.fallback_triggered:
        return "FALLBACK_TRIGGERED"
    if log.repair_attempted:
        return "REPAIR_FAILED"
    if log.evidence_warnings_count > 0:
        return "VALIDATION_ERROR"
    return "LLM_CALL_ERROR"


def _resolve_start_date(period: str) -> datetime:
    if period == "7d":
        return datetime.now(UTC) - timedelta(days=7)
    return datetime.now(UTC) - timedelta(days=30)


def _empty_metric_row(category: dict[str, Any]) -> dict[str, Any]:
    return {
        "use_case": category["key"],
        "display_name": category["display_name"],
        "call_count": 0,
        "total_tokens": 0,
        "estimated_cost_usd": 0.0,
        "avg_latency_ms": 0,
        "error_rate": 0.0,
        "retry_rate": 0.0,
    }


def _resolve_metric_category_or_raw(use_case: str) -> tuple[dict[str, Any], tuple[str, ...]]:
    category = _AI_METRIC_CATEGORY_BY_KEY.get(use_case)
    if category is not None:
        return category, tuple(category["raw_use_cases"])
    fallback_category = {
        "key": use_case,
        "display_name": use_case,
        "raw_use_cases": (use_case,),
    }
    return fallback_category, (use_case,)


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
    start_date = _resolve_start_date(period)

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

    metrics_by_category = {
        category["key"]: _empty_metric_row(category) for category in _AI_METRIC_CATEGORY_DEFINITIONS
    }
    for r in results:
        category = _AI_METRIC_CATEGORY_BY_RAW_USE_CASE.get(r.use_case)
        if category is None:
            category = {
                "key": r.use_case,
                "display_name": r.use_case,
                "raw_use_cases": (r.use_case,),
            }
            metrics_by_category.setdefault(category["key"], _empty_metric_row(category))

        metric_row = metrics_by_category[category["key"]]
        row_call_count = int(r.call_count or 0)
        previous_call_count = int(metric_row["call_count"])
        metric_row["call_count"] = previous_call_count + row_call_count
        metric_row["total_tokens"] += int(r.total_tokens or 0)
        metric_row["estimated_cost_usd"] += float(r.total_cost or 0)
        accumulated_latency = metric_row["avg_latency_ms"] * previous_call_count
        accumulated_latency += int(r.avg_latency or 0) * row_call_count
        if metric_row["call_count"] > 0:
            metric_row["avg_latency_ms"] = int(accumulated_latency / metric_row["call_count"])
        total_error_count = metric_row["error_rate"] * previous_call_count
        total_error_count += float(r.error_count or 0)
        metric_row["error_rate"] = float(
            total_error_count / metric_row["call_count"] if metric_row["call_count"] > 0 else 0
        )

    metrics = list(metrics_by_category.values())
    metrics.sort(key=lambda item: item["display_name"])
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
    start_date = _resolve_start_date(period)
    category, raw_use_cases = _resolve_metric_category_or_raw(use_case)

    error_case = case((LlmCallLogModel.validation_status == LlmValidationStatus.ERROR, 1), else_=0)

    # 1. Summary
    summary_stmt = select(
        func.count(LlmCallLogModel.id).label("call_count"),
        func.sum(LlmCallLogModel.tokens_in + LlmCallLogModel.tokens_out).label("total_tokens"),
        func.sum(LlmCallLogModel.cost_usd_estimated).label("total_cost"),
        func.avg(LlmCallLogModel.latency_ms).label("avg_latency"),
        func.sum(error_case).label("error_count"),
    ).where(LlmCallLogModel.use_case.in_(raw_use_cases), LlmCallLogModel.timestamp >= start_date)
    s = db.execute(summary_stmt).first()
    if not s or s.call_count == 0:
        raise HTTPException(status_code=404, detail="No data for this use case")

    error_rate = (s.error_count / s.call_count) if s.call_count > 0 else 0
    metrics = {
        "use_case": category["key"],
        "display_name": category["display_name"],
        "call_count": s.call_count,
        "total_tokens": int(s.total_tokens or 0),
        "estimated_cost_usd": float(s.total_cost or 0),
        "avg_latency_ms": int(s.avg_latency or 0),
        "error_rate": float(error_rate),
    }

    # 2. Trend Data
    date_func = func.date(LlmCallLogModel.timestamp)
    trend_stmt = (
        select(date_func, func.count(LlmCallLogModel.id), func.sum(error_case))
        .where(LlmCallLogModel.use_case.in_(raw_use_cases), LlmCallLogModel.timestamp >= start_date)
        .group_by(date_func)
        .order_by(date_func)
    )
    trend_rows = db.execute(trend_stmt).all()
    trend_data = [
        {"date": str(r[0]), "call_count": r[1], "error_count": int(r[2] or 0)} for r in trend_rows
    ]

    # 3. Failed calls
    failed_stmt = (
        select(LlmCallLogModel)
        .where(
            LlmCallLogModel.use_case.in_(raw_use_cases),
            LlmCallLogModel.validation_status == LlmValidationStatus.ERROR,
        )
        .order_by(LlmCallLogModel.timestamp.desc())
        .limit(10)
    )
    failed_rows = db.scalars(failed_stmt).all()
    recent_failed_calls = [
        {
            "id": str(f.id),
            "timestamp": f.timestamp,
            "error_code": _derive_failed_call_error_code(f),
            "request_id_masked": f.request_id[:8] + "...",
        }
        for f in failed_rows
    ]

    return {
        "use_case": category["key"],
        "metrics": metrics,
        "trend_data": trend_data,
        "recent_failed_calls": recent_failed_calls,
    }
