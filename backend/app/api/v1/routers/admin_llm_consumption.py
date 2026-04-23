from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.datetime_provider import datetime_provider
from app.core.request_id import resolve_request_id
from app.infra.db.models.llm_observability import LlmCallLogModel
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.llm_canonical_consumption_service import (
    CanonicalConsumptionAggregate,
    CanonicalConsumptionFilters,
    Granularity,
    LlmCanonicalConsumptionService,
    Scope,
)

router = APIRouter(prefix="/v1/admin/llm/consumption", tags=["admin-llm-consumption"])


ConsumptionView = str
VALID_VIEWS = {"user", "subscription", "feature"}
MAX_PAGE_SIZE = 100
DEFAULT_DRILLDOWN_LIMIT = 50


class CanonicalConsumptionViewRow(BaseModel):
    period_start_utc: datetime
    granularity: Granularity
    user_id: int | None = None
    user_email: str | None = None
    subscription_plan: str | None = None
    feature: str | None = None
    subfeature: str | None = None
    locale: str | None = None
    executed_provider: str | None = None
    active_snapshot_version: str | None = None
    request_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    avg_latency_ms: float
    error_rate: float


class CanonicalConsumptionResponse(BaseModel):
    data: list[CanonicalConsumptionViewRow]
    meta: dict[str, Any]


class CanonicalConsumptionDrilldownRow(BaseModel):
    request_id: str
    timestamp: datetime
    feature: str | None = None
    subfeature: str | None = None
    provider: str | None = None
    active_snapshot_version: str | None = None
    manifest_entry_id: str | None = None
    validation_status: str


class CanonicalConsumptionDrilldownResponse(BaseModel):
    data: list[CanonicalConsumptionDrilldownRow]
    meta: dict[str, Any]


def _normalize_view(view: str) -> ConsumptionView:
    value = (view or "").strip().lower()
    if value not in VALID_VIEWS:
        return "user"
    return value


def _safe_sort_value(row: CanonicalConsumptionViewRow, field: str) -> Any:
    value = getattr(row, field, None)
    if value is None:
        return (1, "")
    if isinstance(value, datetime):
        return (0, value)
    if isinstance(value, (int, float)):
        return (0, value)
    return (0, str(value).lower())


def _resolve_bucket_end(granularity: Granularity, period_start_utc: datetime) -> datetime:
    if granularity == "month":
        if period_start_utc.month == 12:
            return period_start_utc.replace(year=period_start_utc.year + 1, month=1, day=1)
        return period_start_utc.replace(month=period_start_utc.month + 1, day=1)
    return period_start_utc.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


def _group_key(row: CanonicalConsumptionAggregate, view: ConsumptionView) -> tuple[Any, ...]:
    if view == "subscription":
        return (row.period_start_utc, row.subscription_plan)
    if view == "feature":
        return (row.period_start_utc, row.feature, row.subfeature)
    return (row.period_start_utc, row.user_id)


def _build_rows(
    *,
    aggregates: list[CanonicalConsumptionAggregate],
    view: ConsumptionView,
    granularity: Granularity,
    user_emails: dict[int, str],
) -> list[CanonicalConsumptionViewRow]:
    grouped: dict[tuple[Any, ...], list[CanonicalConsumptionAggregate]] = {}
    for aggregate in aggregates:
        grouped.setdefault(_group_key(aggregate, view), []).append(aggregate)

    result: list[CanonicalConsumptionViewRow] = []
    for entries in grouped.values():
        sample = entries[0]
        request_count = sum(item.call_count for item in entries)
        input_tokens = sum(item.input_tokens for item in entries)
        output_tokens = sum(item.output_tokens for item in entries)
        total_tokens = sum(item.total_tokens for item in entries)
        estimated_cost = float(sum(Decimal(str(item.estimated_cost)) for item in entries))
        # Filled later from raw llm_call_logs to avoid invalid math on pre-aggregated percentiles.
        avg_latency_ms = 0.0
        weighted_error_rate = (
            sum(item.error_rate * item.call_count for item in entries) / request_count
            if request_count
            else 0.0
        )

        row = CanonicalConsumptionViewRow(
            period_start_utc=sample.period_start_utc,
            granularity=granularity,
            request_count=request_count,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=round(estimated_cost, 8),
            avg_latency_ms=round(avg_latency_ms, 2),
            error_rate=round(weighted_error_rate, 6),
        )

        if view == "subscription":
            row.subscription_plan = sample.subscription_plan
        elif view == "feature":
            row.feature = sample.feature
            row.subfeature = sample.subfeature
        else:
            row.user_id = sample.user_id
            row.user_email = user_emails.get(sample.user_id) if sample.user_id is not None else None

        result.append(row)
    return result


def _resolve_exact_average_latencies(
    *,
    db: Session,
    rows: list[CanonicalConsumptionViewRow],
    view: ConsumptionView,
    filters: CanonicalConsumptionFilters,
) -> None:
    normalized_calls = LlmCanonicalConsumptionService._normalized_calls(db=db, filters=filters)
    grouped_latencies: dict[tuple[Any, ...], list[int]] = {}
    for call in normalized_calls:
        period_start = LlmCanonicalConsumptionService._period_start_utc(
            timestamp=call.timestamp,
            granularity=filters.granularity,
        )
        if view == "user":
            key = (period_start, call.user_id)
        elif view == "subscription":
            key = (period_start, call.subscription_plan)
        else:
            key = (period_start, call.feature, call.subfeature)
        grouped_latencies.setdefault(key, []).append(int(call.latency_ms))

    for row in rows:
        if view == "user":
            key = (row.period_start_utc, row.user_id)
        elif view == "subscription":
            key = (row.period_start_utc, row.subscription_plan)
        else:
            key = (row.period_start_utc, row.feature, row.subfeature)
        latencies = grouped_latencies.get(key, [])
        row.avg_latency_ms = round(sum(latencies) / len(latencies), 2) if latencies else 0.0


def _apply_search(
    rows: list[CanonicalConsumptionViewRow], search: str | None
) -> list[CanonicalConsumptionViewRow]:
    if not search:
        return rows
    needle = search.strip().lower()
    if not needle:
        return rows
    filtered: list[CanonicalConsumptionViewRow] = []
    for row in rows:
        haystack = " ".join(
            str(value or "")
            for value in (
                row.user_email,
                row.user_id,
                row.subscription_plan,
                row.feature,
                row.subfeature,
                row.period_start_utc.isoformat(),
            )
        ).lower()
        if needle in haystack:
            filtered.append(row)
    return filtered


def _rows_to_csv(rows: list[CanonicalConsumptionViewRow], view: ConsumptionView) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        "period_start_utc",
        "granularity",
        "request_count",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "estimated_cost",
        "avg_latency_ms",
        "error_rate",
    ]
    if view == "user":
        headers.extend(["user_id", "user_email"])
    elif view == "subscription":
        headers.append("subscription_plan")
    else:
        headers.extend(["feature", "subfeature"])
    writer.writerow(headers)
    for row in rows:
        values = [
            row.period_start_utc.isoformat(),
            row.granularity,
            row.request_count,
            row.input_tokens,
            row.output_tokens,
            row.total_tokens,
            row.estimated_cost,
            row.avg_latency_ms,
            row.error_rate,
        ]
        if view == "user":
            values.extend([row.user_id, row.user_email or ""])
        elif view == "subscription":
            values.append(row.subscription_plan or "")
        else:
            values.extend([row.feature or "", row.subfeature or ""])
        writer.writerow(values)
    return output.getvalue()


@router.get("/canonical", response_model=CanonicalConsumptionResponse)
def get_canonical_consumption(
    request: Request,
    view: str = "user",
    granularity: Granularity = "day",
    scope: Scope = "nominal",
    refresh: bool = False,
    from_utc: datetime | None = None,
    to_utc: datetime | None = None,
    user_id: int | None = None,
    feature: str | None = None,
    subfeature: str | None = None,
    subscription_plan: str | None = None,
    locale: str | None = None,
    executed_provider: str | None = None,
    active_snapshot_version: str | None = None,
    search: str | None = None,
    sort_by: str = "period_start_utc",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 25,
    export: str | None = None,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    selected_view = _normalize_view(view)
    filters = CanonicalConsumptionFilters(
        granularity=granularity,
        scope=scope,
        from_utc=from_utc,
        to_utc=to_utc,
        user_id=user_id,
        feature=feature,
        subfeature=subfeature,
        subscription_plan=subscription_plan,
        locale=locale,
        executed_provider=executed_provider,
        active_snapshot_version=active_snapshot_version,
    )
    aggregates = LlmCanonicalConsumptionService.get_aggregates(
        db=db,
        filters=filters,
        refresh=refresh,
    )
    user_emails: dict[int, str] = {}
    user_ids = sorted({item.user_id for item in aggregates if item.user_id is not None})
    if user_ids:
        rows = db.execute(
            select(UserModel.id, UserModel.email).where(UserModel.id.in_(user_ids))
        ).all()
        user_emails = {int(row.id): str(row.email) for row in rows}
    rows = _build_rows(
        aggregates=aggregates,
        view=selected_view,
        granularity=granularity,
        user_emails=user_emails,
    )
    _resolve_exact_average_latencies(
        db=db,
        rows=rows,
        view=selected_view,
        filters=filters,
    )
    rows = _apply_search(rows, search)

    allowed_sort_fields = {
        "period_start_utc",
        "request_count",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "estimated_cost",
        "avg_latency_ms",
        "error_rate",
        "user_id",
        "user_email",
        "subscription_plan",
        "feature",
        "subfeature",
    }
    resolved_sort_by = sort_by if sort_by in allowed_sort_fields else "period_start_utc"
    reverse_sort = (sort_order or "").lower() != "asc"
    rows.sort(key=lambda row: _safe_sort_value(row, resolved_sort_by), reverse=reverse_sort)

    if export and export.lower() == "csv":
        csv_payload = _rows_to_csv(rows, selected_view)
        filename = f"llm-consumption-{selected_view}-{granularity}.csv"
        return StreamingResponse(
            iter([csv_payload]),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    safe_page = max(page, 1)
    safe_page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    total = len(rows)
    start = (safe_page - 1) * safe_page_size
    paged_rows = rows[start : start + safe_page_size]

    return {
        "data": paged_rows,
        "meta": {
            "request_id": request_id,
            "view": selected_view,
            "granularity": granularity,
            "scope": scope,
            "refresh": refresh,
            "count": total,
            "page": safe_page,
            "page_size": safe_page_size,
            "sort_by": resolved_sort_by,
            "sort_order": "desc" if reverse_sort else "asc",
            "default_granularity_behavior": "aggregated_by_selected_period",
            "timezone": "UTC",
        },
    }


@router.get("/canonical/drilldown", response_model=CanonicalConsumptionDrilldownResponse)
def get_canonical_consumption_drilldown(
    request: Request,
    view: str = "user",
    granularity: Granularity = "day",
    period_start_utc: datetime | None = None,
    user_id: int | None = None,
    subscription_plan: str | None = None,
    feature: str | None = None,
    subfeature: str | None = None,
    limit: int = DEFAULT_DRILLDOWN_LIMIT,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    selected_view = _normalize_view(view)
    if period_start_utc is None:
        period_start_utc = datetime_provider.utcnow()
    period_start = (
        period_start_utc
        if period_start_utc.tzinfo
        else period_start_utc.replace(tzinfo=timezone.utc)
    )
    period_end = _resolve_bucket_end(granularity, period_start)

    stmt = (
        select(LlmCallLogModel)
        .where(LlmCallLogModel.timestamp >= period_start)
        .where(LlmCallLogModel.timestamp < period_end)
    )
    capped_limit = max(1, min(limit, DEFAULT_DRILLDOWN_LIMIT))
    if selected_view == "user":
        if user_id is not None:
            call_ids_subquery = (
                select(UserTokenUsageLogModel.llm_call_log_id)
                .join(
                    LlmCallLogModel,
                    UserTokenUsageLogModel.llm_call_log_id == LlmCallLogModel.id,
                )
                .where(UserTokenUsageLogModel.user_id == user_id)
                .where(LlmCallLogModel.timestamp >= period_start)
                .where(LlmCallLogModel.timestamp < period_end)
                .group_by(UserTokenUsageLogModel.llm_call_log_id)
                .order_by(desc(func.max(LlmCallLogModel.timestamp)))
                .limit(capped_limit)
                .subquery()
            )
            stmt = select(LlmCallLogModel).where(
                LlmCallLogModel.id.in_(select(call_ids_subquery.c.llm_call_log_id))
            )
        else:
            ambiguous_call_ids_subquery = (
                select(UserTokenUsageLogModel.llm_call_log_id)
                .join(
                    LlmCallLogModel,
                    UserTokenUsageLogModel.llm_call_log_id == LlmCallLogModel.id,
                )
                .where(LlmCallLogModel.timestamp >= period_start)
                .where(LlmCallLogModel.timestamp < period_end)
                .group_by(UserTokenUsageLogModel.llm_call_log_id)
                .having(func.count(func.distinct(UserTokenUsageLogModel.user_id)) > 1)
                .order_by(desc(func.max(LlmCallLogModel.timestamp)))
                .limit(capped_limit)
                .subquery()
            )
            stmt = select(LlmCallLogModel).where(
                LlmCallLogModel.id.in_(select(ambiguous_call_ids_subquery.c.llm_call_log_id))
            )
    elif selected_view == "subscription":
        if subscription_plan is not None:
            stmt = stmt.where(LlmCallLogModel.plan == subscription_plan)
    else:
        if feature is not None:
            stmt = stmt.where(LlmCallLogModel.feature == feature)
        if subfeature is None:
            stmt = stmt.where(LlmCallLogModel.subfeature.is_(None))
        else:
            stmt = stmt.where(LlmCallLogModel.subfeature == subfeature)

    logs = (
        db.execute(stmt.order_by(desc(LlmCallLogModel.timestamp)).limit(capped_limit))
        .scalars()
        .all()
    )
    data = [
        CanonicalConsumptionDrilldownRow(
            request_id=item.request_id,
            timestamp=item.timestamp,
            feature=item.feature,
            subfeature=item.subfeature,
            provider=item.executed_provider or item.provider,
            active_snapshot_version=item.active_snapshot_version,
            manifest_entry_id=item.manifest_entry_id,
            validation_status=str(item.validation_status),
        )
        for item in logs
    ]
    return {
        "data": data,
        "meta": {
            "request_id": request_id,
            "view": selected_view,
            "granularity": granularity,
            "period_start_utc": period_start.isoformat(),
            "limit": capped_limit,
            "count": len(data),
            "order": "timestamp_desc",
            "safe_by_design": True,
        },
    }
