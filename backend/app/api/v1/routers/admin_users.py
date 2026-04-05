from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.admin_users import (
    AdminUserDetailResponse,
    AdminUserSearchResponse,
    RevealStripeIdResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import UserSubscriptionModel
from app.infra.db.models.llm_observability import LlmCallLogModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    FeatureUsageCounterModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/users", tags=["admin-users"])


def _mask_id(raw_id: str | None) -> str | None:
    if not raw_id:
        return None
    if len(raw_id) <= 11:
        return raw_id
    return f"{raw_id[:7]}...{raw_id[-4:]}"


@router.get("", response_model=AdminUserSearchResponse)
def search_users(
    request: Request,
    q: str = Query(default=""),
    limit: int = Query(default=20, le=100),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Search users by email (partial) or ID (exact).
    """
    stmt = (
        select(
            UserModel.id,
            UserModel.email,
            UserModel.role,
            UserModel.created_at,
            StripeBillingProfileModel.entitlement_plan.label("plan_code"),
            StripeBillingProfileModel.subscription_status,
        )
        .outerjoin(StripeBillingProfileModel, StripeBillingProfileModel.user_id == UserModel.id)
        .order_by(UserModel.created_at.desc())
    )

    if q:
        if q == "payment_failure":
            stmt = stmt.join(UserSubscriptionModel, UserSubscriptionModel.user_id == UserModel.id).where(
                UserSubscriptionModel.failure_reason.is_not(None)
            )
        elif q.isdigit():
            stmt = stmt.where(or_(UserModel.email.ilike(f"%{q}%"), UserModel.id == int(q)))
        else:
            stmt = stmt.where(UserModel.email.ilike(f"%{q}%"))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    results = db.execute(stmt.limit(limit)).all()

    return {
        "data": [
            {
                "id": r.id,
                "email": r.email,
                "role": r.role,
                "created_at": r.created_at,
                "plan_code": r.plan_code,
                "subscription_status": r.subscription_status,
            }
            for r in results
        ],
        "total": total or 0,
    }


@router.get("/{user_id}", response_model=AdminUserDetailResponse)
def get_user_detail(
    user_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get full user detail including billing, quotas, logs, etc.
    """
    user = db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.scalar(
        select(StripeBillingProfileModel).where(StripeBillingProfileModel.user_id == user_id)
    )

    # Quotas logic (simplified for MVP)
    # 1. Current usage counters
    usage_counters = db.scalars(
        select(FeatureUsageCounterModel).where(FeatureUsageCounterModel.user_id == user_id)
    ).all()

    # 2. Map to display format
    quotas_data = []
    for c in usage_counters:
        # Try to find the limit in plan_catalog (complex JOIN, simplified for now)
        # We'll just return what we have in counters.
        # In a real impl, we'd resolve the effective plan and its limits.
        quotas_data.append(
            {
                "feature_code": c.feature_code,
                "used": c.used_count,
                "limit": None,  # Resolve later
                "period": f"{c.period_value} {c.period_unit.value}",
            }
        )

    # Recent LLM logs (20)
    llm_logs = db.execute(
        select(LlmCallLogModel)
        .where(LlmCallLogModel.request_id.in_(
            # This is tricky because LlmCallLogModel doesn't have user_id directly
            # but we can filter by trace_id or request_id if we have a mapping.
            # In our current schema, we don't have a direct link.
            # WORKAROUND: skip or use a search if possible.
            # Let's assume for now we don't have it easily.
            select(AuditEventModel.request_id).where(
                AuditEventModel.actor_user_id == user_id,
                AuditEventModel.action.in_(["chat_message_sent", "natal_interpretation_requested"])
            )
        ))
        .order_by(LlmCallLogModel.timestamp.desc())
        .limit(20)
    ).scalars().all() if False else [] # Disable for now due to complexity

    # Alternative: Recent audit events (10)
    audit_events = db.scalars(
        select(AuditEventModel)
        .where(or_(AuditEventModel.actor_user_id == user_id, 
                   (AuditEventModel.target_type == "user") & (AuditEventModel.target_id == str(user_id))))
        .order_by(AuditEventModel.created_at.desc())
        .limit(10)
    ).all()

    # Recent support tickets (5)
    tickets = db.scalars(
        select(SupportIncidentModel)
        .where(SupportIncidentModel.user_id == user_id)
        .order_by(SupportIncidentModel.created_at.desc())
        .limit(5)
    ).all()

    return {
        "data": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
            "is_active": True,
            "plan_code": profile.entitlement_plan if profile else "free",
            "subscription_status": profile.subscription_status if profile else None,
            "stripe_customer_id_masked": _mask_id(profile.stripe_customer_id) if profile else None,
            "payment_method_summary": None, # Resolve from Stripe profile if stored
            "last_invoice_amount_cents": None,
            "last_invoice_date": None,
            "quotas": quotas_data,
            "recent_llm_logs": [], # TODO
            "recent_tickets": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "created_at": t.created_at
                } for t in tickets
            ],
            "recent_audit_events": [
                {
                    "id": a.id,
                    "action": a.action,
                    "actor_role": a.actor_role,
                    "created_at": a.created_at
                } for a in audit_events
            ]
        }
    }


@router.post("/{user_id}/reveal-stripe-id", response_model=RevealStripeIdResponse)
def reveal_stripe_id(
    user_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Reveal the full Stripe customer ID and log the action.
    """
    request_id = resolve_request_id(request)
    profile = db.scalar(
        select(StripeBillingProfileModel).where(StripeBillingProfileModel.user_id == user_id)
    )
    if not profile or not profile.stripe_customer_id:
        raise HTTPException(status_code=404, detail="Stripe profile not found")

    # Audit log
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="sensitive_data_revealed",
            target_type="user",
            target_id=str(user_id),
            status="success",
            details={"field": "stripe_customer_id"},
        ),
    )
    db.commit()

    return {"stripe_customer_id": profile.stripe_customer_id}
