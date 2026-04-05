from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
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
            UserModel.is_suspended,
            UserModel.is_locked,
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
                "is_suspended": r.is_suspended,
                "is_locked": r.is_locked,
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
    usage_counters = db.scalars(
        select(FeatureUsageCounterModel).where(FeatureUsageCounterModel.user_id == user_id)
    ).all()

    quotas_data = []
    for c in usage_counters:
        quotas_data.append(
            {
                "feature_code": c.feature_code,
                "used": c.used_count,
                "limit": None,
                "period": f"{c.period_value} {c.period_unit.value}",
            }
        )

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
            "is_suspended": user.is_suspended,
            "is_locked": user.is_locked,
            "plan_code": profile.entitlement_plan if profile else "free",
            "subscription_status": profile.subscription_status if profile else None,
            "stripe_customer_id_masked": _mask_id(profile.stripe_customer_id) if profile else None,
            "payment_method_summary": None,
            "last_invoice_amount_cents": None,
            "last_invoice_date": None,
            "quotas": quotas_data,
            "recent_llm_logs": [],
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
    request_id = resolve_request_id(request)
    profile = db.scalar(
        select(StripeBillingProfileModel).where(StripeBillingProfileModel.user_id == user_id)
    )
    if not profile or not profile.stripe_customer_id:
        raise HTTPException(status_code=404, detail="Stripe profile not found")

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


@router.post("/{user_id}/suspend")
def suspend_user(
    user_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    user = db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    before = {"is_suspended": user.is_suspended}
    user.is_suspended = True
    
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="account_suspended",
            target_type="user",
            target_id=str(user_id),
            status="success",
            details={"before": before, "after": {"is_suspended": True}},
        ),
    )
    db.commit()
    return {"status": "success"}


@router.post("/{user_id}/unsuspend")
def unsuspend_user(
    user_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    user = db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    before = {"is_suspended": user.is_suspended}
    user.is_suspended = False
    
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="account_reactivated",
            target_type="user",
            target_id=str(user_id),
            status="success",
            details={"before": before, "after": {"is_suspended": False}},
        ),
    )
    db.commit()
    return {"status": "success"}


@router.post("/{user_id}/unlock")
def unlock_user(
    user_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    user = db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    before = {"is_locked": user.is_locked}
    user.is_locked = False
    
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="account_unlocked",
            target_type="user",
            target_id=str(user_id),
            status="success",
            details={"before": before, "after": {"is_locked": False}},
        ),
    )
    db.commit()
    return {"status": "success"}


@router.post("/{user_id}/reset-quota")
def reset_user_quota(
    user_id: int,
    request: Request,
    feature_code: str = Body(embed=True),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    # Reset all counters for this user and feature
    counters = db.scalars(
        select(FeatureUsageCounterModel)
        .where(FeatureUsageCounterModel.user_id == user_id, 
               FeatureUsageCounterModel.feature_code == feature_code)
    ).all()
    
    for c in counters:
        before_val = c.used_count
        c.used_count = 0
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id=resolve_request_id(request),
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="quota_reset",
                target_type="user",
                target_id=str(user_id),
                status="success",
                details={"feature_code": feature_code, "before": before_val, "after": 0},
            ),
        )
    
    db.commit()
    return {"status": "success"}
