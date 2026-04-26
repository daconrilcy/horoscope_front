from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.router_logic.admin.ai import (
    _build_target_filters,
    _derive_failed_call_error_code,
    _empty_metric_row,
    _legacy_removed_filter,
    _resolve_metric_category,
    _resolve_metric_category_or_raw,
    _resolve_start_date,
)
from app.api.v1.schemas.admin_ai import (
    AdminAiMetricsResponse,
    AdminAiUseCaseDetailResponse,
)
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.session import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/ai", tags=["admin-ai"])


_AI_METRIC_CATEGORY_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "key": "natal_theme_short_free",
        "display_name": "Theme natal short free",
        "targets": ({"feature": "natal", "subfeature": "interpretation", "plan": "free"},),
    },
    {
        "key": "natal_theme_short_paid",
        "display_name": "Theme natal short basic/premium",
        "targets": (
            {"feature": "natal", "subfeature": "short", "plan": "basic"},
            {"feature": "natal", "subfeature": "short", "plan": "premium"},
        ),
    },
    {
        "key": "natal_theme_complete_paid",
        "display_name": "Theme natal complete basic/premium",
        "targets": (
            {"feature": "natal", "subfeature": "interpretation", "plan": "basic"},
            {"feature": "natal", "subfeature": "interpretation", "plan": "premium"},
        ),
    },
    {
        "key": "thematic_consultations",
        "display_name": "Consultations thematiques",
        "targets": (
            {"feature": "guidance", "subfeature": "event"},
            {"feature": "natal", "subfeature": "psy_profile"},
            {"feature": "natal", "subfeature": "shadow_integration"},
            {"feature": "natal", "subfeature": "leadership_workstyle"},
            {"feature": "natal", "subfeature": "creativity_joy"},
            {"feature": "natal", "subfeature": "relationship_style"},
            {"feature": "natal", "subfeature": "community_networks"},
            {"feature": "natal", "subfeature": "values_security"},
            {"feature": "natal", "subfeature": "evolution_path"},
        ),
    },
    {
        "key": "astrologer_chat",
        "display_name": "Chat astrologue",
        "targets": ({"feature": "chat", "subfeature": "astrologer"},),
    },
    {
        "key": "daily_horoscope",
        "display_name": "Horoscope du jour",
        "targets": ({"feature": "horoscope_daily", "subfeature": "narration"},),
    },
    {
        "key": "weekly_horoscope",
        "display_name": "Horoscope hebdomadaire",
        "targets": ({"feature": "guidance", "subfeature": "weekly"},),
    },
)

_AI_METRIC_CATEGORY_BY_KEY = {item["key"]: item for item in _AI_METRIC_CATEGORY_DEFINITIONS}
_REMOVED_LEGACY_USE_CASES = frozenset(
    {"daily_prediction", "horoscope_daily_free", "horoscope_daily_full", "chat", "chat_astrologer"}
)


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

    stmt = select(LlmCallLogModel).where(LlmCallLogModel.timestamp >= start_date)

    results = db.execute(stmt).scalars().all()

    metrics_by_category = {
        category["key"]: _empty_metric_row(category) for category in _AI_METRIC_CATEGORY_DEFINITIONS
    }
    for r in results:
        category = _resolve_metric_category(r)
        metrics_by_category.setdefault(category["key"], _empty_metric_row(category))

        metric_row = metrics_by_category[category["key"]]
        row_call_count = 1
        previous_call_count = int(metric_row["call_count"])
        metric_row["call_count"] = previous_call_count + row_call_count
        metric_row["total_tokens"] += int((r.tokens_in or 0) + (r.tokens_out or 0))
        metric_row["estimated_cost_usd"] += float(r.cost_usd_estimated or 0)
        accumulated_latency = metric_row["avg_latency_ms"] * previous_call_count
        accumulated_latency += int(r.latency_ms or 0) * row_call_count
        if metric_row["call_count"] > 0:
            metric_row["avg_latency_ms"] = int(accumulated_latency / metric_row["call_count"])
        total_error_count = metric_row["error_rate"] * previous_call_count
        total_error_count += float(1 if r.validation_status == LlmValidationStatus.ERROR else 0)
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
    ).where(LlmCallLogModel.timestamp >= start_date)
    if use_case == "legacy_removed" and raw_use_cases:
        summary_stmt = summary_stmt.where(_legacy_removed_filter())
    elif category.get("targets"):
        summary_stmt = summary_stmt.where(or_(*_build_target_filters(category)))
    else:
        summary_stmt = summary_stmt.where(LlmCallLogModel.feature == use_case)
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
        .where(LlmCallLogModel.timestamp >= start_date)
        .group_by(date_func)
        .order_by(date_func)
    )
    if use_case == "legacy_removed" and raw_use_cases:
        trend_stmt = trend_stmt.where(_legacy_removed_filter())
    elif category.get("targets"):
        trend_stmt = trend_stmt.where(or_(*_build_target_filters(category)))
    else:
        trend_stmt = trend_stmt.where(LlmCallLogModel.feature == use_case)
    trend_rows = db.execute(trend_stmt).all()
    trend_data = [
        {"date": str(r[0]), "call_count": r[1], "error_count": int(r[2] or 0)} for r in trend_rows
    ]

    # 3. Failed calls
    failed_stmt = (
        select(LlmCallLogModel)
        .where(
            LlmCallLogModel.validation_status == LlmValidationStatus.ERROR,
        )
        .order_by(LlmCallLogModel.timestamp.desc())
        .limit(10)
    )
    if use_case == "legacy_removed" and raw_use_cases:
        failed_stmt = failed_stmt.where(_legacy_removed_filter())
    elif category.get("targets"):
        failed_stmt = failed_stmt.where(or_(*_build_target_filters(category)))
    else:
        failed_stmt = failed_stmt.where(LlmCallLogModel.feature == use_case)
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
