from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.llm_canonical_consumption_service import (
    CanonicalConsumptionAggregate,
    CanonicalConsumptionFilters,
    Granularity,
    LlmCanonicalConsumptionService,
    Scope,
)

router = APIRouter(prefix="/v1/admin/llm/consumption", tags=["admin-llm-consumption"])


class CanonicalConsumptionResponse(BaseModel):
    data: list[CanonicalConsumptionAggregate]
    meta: dict[str, Any]


@router.get("/canonical", response_model=CanonicalConsumptionResponse)
def get_canonical_consumption(
    request: Request,
    granularity: Granularity = "day",
    scope: Scope = "nominal",
    from_utc: datetime | None = None,
    to_utc: datetime | None = None,
    user_id: int | None = None,
    feature: str | None = None,
    subfeature: str | None = None,
    subscription_plan: str | None = None,
    locale: str | None = None,
    executed_provider: str | None = None,
    active_snapshot_version: str | None = None,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
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
    aggregates = LlmCanonicalConsumptionService.get_aggregates(db=db, filters=filters)
    return {
        "data": aggregates,
        "meta": {
            "request_id": request_id,
            "granularity": granularity,
            "scope": scope,
            "count": len(aggregates),
            "timezone": "UTC",
        },
    }
