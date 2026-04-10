from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.admin_exports import (
    AdminExportRequest,
    AdminGenerationExportRequest,
)
from app.core.request_id import resolve_request_id
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.llm_observability import LlmCallLogModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/exports", tags=["admin-exports"])


def _generate_csv_response(rows: list[dict[str, Any]], fieldnames: list[str], filename: str):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _record_export_audit(
    db: Session,
    request: Request,
    user: AuthenticatedUser,
    export_type: str,
    count: int,
    filters: dict,
):
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=user.id,
            actor_role=user.role,
            action="sensitive_data_exported",
            target_type="system",
            target_id=None,
            status="success",
            details={
                "export_type": export_type,
                "filters": filters,
                "record_count": count,
            },
        ),
    )
    db.commit()


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
    stmt = (
        select(
            LlmCallLogModel.id,
            LlmCallLogModel.timestamp.label("created_at"),
            LlmCallLogModel.use_case,
            LlmCallLogModel.model,
            LlmCallLogModel.validation_status.label("status"),
            LlmCallLogModel.tokens_in.label("tokens_prompt"),
            LlmCallLogModel.tokens_out.label("tokens_completion"),
            LlmCallLogModel.latency_ms,
            LlmCallLogModel.request_id,
        )
        .order_by(LlmCallLogModel.timestamp.desc())
        .limit(5000)
    )

    if payload.period:
        if payload.period.start:
            stmt = stmt.where(LlmCallLogModel.timestamp >= payload.period.start)
        if payload.period.end:
            stmt = stmt.where(LlmCallLogModel.timestamp <= payload.period.end)

    results = db.execute(stmt).all()
    rows = [dict(r._mapping) for r in results]

    # Process ISO dates for JSON
    for r in rows:
        if isinstance(r["created_at"], datetime):
            r["created_at"] = r["created_at"].isoformat()

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
    if payload.format == "json":
        return StreamingResponse(
            iter([json.dumps(rows, indent=2)]),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=generations_export.json"},
        )

    fieldnames = [
        "id",
        "created_at",
        "use_case",
        "model",
        "status",
        "tokens_prompt",
        "tokens_completion",
        "latency_ms",
        "request_id",
    ]
    return _generate_csv_response(rows, fieldnames, "generations_export.csv")


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
