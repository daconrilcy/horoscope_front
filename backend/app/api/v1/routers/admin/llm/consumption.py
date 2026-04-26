"""Routeur admin de lecture et drilldown de consommation canonique LLM."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.constants import DEFAULT_DRILLDOWN_LIMIT, MAX_PAGE_SIZE
from app.api.v1.router_logic.admin.llm.consumption import (
    _apply_search,
    _build_rows,
    _normalize_view,
    _resolve_exact_average_latencies,
    _rows_to_csv,
    _safe_sort_value,
)
from app.api.v1.schemas.routers.admin.llm.consumption import (
    CanonicalConsumptionDrilldownResponse,
    CanonicalConsumptionDrilldownRow,
    CanonicalConsumptionResponse,
)
from app.core.datetime_provider import datetime_provider
from app.core.request_id import resolve_request_id
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.llm_observability.consumption_service import (
    CanonicalConsumptionFilters,
    Granularity,
    LlmCanonicalConsumptionService,
    Scope,
)

router = APIRouter(prefix="/v1/admin/llm/consumption", tags=["admin-llm-consumption"])


ConsumptionView = str


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
    capped_limit = max(1, min(limit, DEFAULT_DRILLDOWN_LIMIT))
    data = LlmCanonicalConsumptionService.get_drilldown_entries(
        db=db,
        view=selected_view,  # type: ignore[arg-type]
        granularity=granularity,
        period_start_utc=period_start_utc,
        user_id=user_id,
        subscription_plan=subscription_plan,
        feature=feature,
        subfeature=subfeature,
        limit=capped_limit,
    )
    return {
        "data": [CanonicalConsumptionDrilldownRow(**item.model_dump()) for item in data],
        "meta": {
            "request_id": request_id,
            "view": selected_view,
            "granularity": granularity,
            "period_start_utc": (
                period_start_utc.isoformat()
                if isinstance(period_start_utc, datetime)
                else datetime_provider.utcnow().isoformat()
            ),
            "limit": capped_limit,
            "count": len(data),
            "order": "timestamp_desc",
            "safe_by_design": True,
        },
    }
