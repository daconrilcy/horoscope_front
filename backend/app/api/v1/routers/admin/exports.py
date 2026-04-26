"""Routeur d exports admin avec consommation canonique LLM normalisee."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.router_logic.admin.exports import (
    _generate_csv_response,
    _record_export_audit,
)
from app.api.v1.schemas.admin_exports import (
    AdminExportRequest,
    AdminGenerationExportRequest,
)
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.llm_observability.consumption_service import LlmCanonicalConsumptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/exports", tags=["admin-exports"])

GEN_EXPORT_COMPAT_DEPRECATION_WARNING = (
    '299 - "Deprecated field: use_case_compat is compatibility-only and will be removed after '
    '2026-09-30. Use feature/subfeature/subscription_plan instead."'
)
GEN_EXPORT_COMPAT_DEPRECATION_SUNSET = "Tue, 30 Sep 2026 23:59:59 GMT"


@router.post("/users")
def export_users(
    request: Request,
    payload: AdminExportRequest,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    stmt = (
        select(
            UserModel.id,
            UserModel.email,
            UserModel.role,
            UserModel.is_suspended,
            UserModel.email_unsubscribed,
            UserModel.created_at,
            StripeBillingProfileModel.entitlement_plan.label("plan_code"),
            StripeBillingProfileModel.subscription_status,
            StripeBillingProfileModel.stripe_customer_id,
        )
        .outerjoin(StripeBillingProfileModel, StripeBillingProfileModel.user_id == UserModel.id)
        .order_by(UserModel.created_at.desc())
        .limit(5000)
    )

    if payload.period:
        if payload.period.start:
            stmt = stmt.where(UserModel.created_at >= payload.period.start)
        if payload.period.end:
            stmt = stmt.where(UserModel.created_at <= payload.period.end)

    results = db.execute(stmt).all()
    rows = [dict(r._mapping) for r in results]

    # 1. Audit
    _record_export_audit(
        db,
        request,
        current_user,
        "users",
        len(rows),
        payload.model_dump(mode="json"),
    )

    # 2. Return CSV
    fieldnames = [
        "id",
        "email",
        "role",
        "is_suspended",
        "email_unsubscribed",
        "created_at",
        "plan_code",
        "subscription_status",
        "stripe_customer_id",
    ]
    return _generate_csv_response(rows, fieldnames, "users_export.csv")


@router.post("/generations")
def export_generations(
    request: Request,
    payload: AdminGenerationExportRequest,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    rows = [
        row.model_dump(mode="json")
        for row in LlmCanonicalConsumptionService.get_export_rows(
            db,
            from_utc=payload.period.start if payload.period else None,
            to_utc=payload.period.end if payload.period else None,
        )
    ]

    # 1. Audit
    _record_export_audit(
        db,
        request,
        current_user,
        "generations",
        len(rows),
        payload.model_dump(mode="json"),
    )

    # 2. Return File
    deprecation_headers = {
        "Warning": GEN_EXPORT_COMPAT_DEPRECATION_WARNING,
        "Sunset": GEN_EXPORT_COMPAT_DEPRECATION_SUNSET,
        "X-Deprecated-Fields": "use_case_compat",
    }
    if payload.format == "json":
        return StreamingResponse(
            iter([json.dumps(rows, indent=2)]),
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=generations_export.json",
                **deprecation_headers,
            },
        )

    fieldnames = [
        "id",
        "created_at",
        "feature",
        "subfeature",
        "subscription_plan",
        "executed_provider",
        "active_snapshot_version",
        "taxonomy_scope",
        "use_case_compat",
        "model",
        "status",
        "tokens_prompt",
        "tokens_completion",
        "latency_ms",
        "request_id",
    ]
    return _generate_csv_response(
        rows,
        fieldnames,
        "generations_export.csv",
        extra_headers=deprecation_headers,
    )


@router.post("/billing")
def export_billing(
    request: Request,
    payload: AdminExportRequest,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    stmt = (
        select(
            UserSubscriptionModel.user_id,
            UserModel.email,
            BillingPlanModel.code.label("plan_code"),
            UserSubscriptionModel.status.label("subscription_status"),
            BillingPlanModel.monthly_price_cents,
            UserSubscriptionModel.created_at.label("started_at"),
            UserSubscriptionModel.failure_reason,
        )
        .join(UserModel, UserModel.id == UserSubscriptionModel.user_id)
        .join(BillingPlanModel, BillingPlanModel.id == UserSubscriptionModel.plan_id)
        .order_by(UserSubscriptionModel.created_at.desc())
        .limit(5000)
    )

    if payload.period:
        if payload.period.start:
            stmt = stmt.where(UserSubscriptionModel.created_at >= payload.period.start)
        if payload.period.end:
            stmt = stmt.where(UserSubscriptionModel.created_at <= payload.period.end)

    results = db.execute(stmt).all()
    rows = [dict(r._mapping) for r in results]

    # 1. Audit
    _record_export_audit(
        db,
        request,
        current_user,
        "billing",
        len(rows),
        payload.model_dump(mode="json"),
    )

    # 2. Return CSV
    fieldnames = [
        "user_id",
        "email",
        "plan_code",
        "subscription_status",
        "monthly_price_cents",
        "started_at",
        "failure_reason",
    ]
    return _generate_csv_response(rows, fieldnames, "billing_export.csv")
