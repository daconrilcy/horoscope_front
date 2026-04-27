from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.errors import raise_http_error
from app.api.v1.schemas.routers.admin.entitlements import (
    AdminEntitlementMatrixResponse,
    AdminEntitlementUpdate,
)
from app.core.request_id import resolve_request_id
from app.infra.db.models.product_entitlements import (
    AccessMode,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
)
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/entitlements", tags=["admin-entitlements"])


@router.get("/matrix", response_model=AdminEntitlementMatrixResponse)
def get_entitlement_matrix(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Generate the full plans x features matrix.
    """
    plans = db.scalars(select(PlanCatalogModel).order_by(PlanCatalogModel.id)).all()
    features = db.scalars(select(FeatureCatalogModel).order_by(FeatureCatalogModel.id)).all()

    # Load all bindings with their quotas
    bindings = (
        db.scalars(
            select(PlanFeatureBindingModel).options(joinedload(PlanFeatureBindingModel.quotas))
        )
        .unique()
        .all()
    )

    cells = {}
    for b in bindings:
        key = f"{b.plan_id}:{b.feature_id}"

        # Take the first quota if available (MVP simplification)
        quota = b.quotas[0] if b.quotas else None

        is_incoherent = b.access_mode == AccessMode.QUOTA and (not quota or quota.quota_limit <= 0)

        cells[key] = {
            "access_mode": b.access_mode.value,
            "is_enabled": b.is_enabled,
            "variant_code": b.variant_code,
            "quota_limit": quota.quota_limit if quota else None,
            "period": f"{quota.period_value} {quota.period_unit.value}" if quota else None,
            "is_incoherent": is_incoherent,
        }

    return {
        "plans": [
            {"id": p.id, "code": p.plan_code, "name": p.plan_name, "audience": p.audience.value}
            for p in plans
        ],
        "features": [
            {"id": f.id, "code": f.feature_code, "name": f.feature_name, "is_metered": f.is_metered}
            for f in features
        ],
        "cells": cells,
    }


@router.patch("/{plan_id}/{feature_id}")
def update_entitlement(
    plan_id: int,
    feature_id: int,
    payload: AdminEntitlementUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Update a specific plan-feature binding (quota, mode, enabled).
    """
    binding = db.scalar(
        select(PlanFeatureBindingModel)
        .where(
            PlanFeatureBindingModel.plan_id == plan_id,
            PlanFeatureBindingModel.feature_id == feature_id,
        )
        .options(joinedload(PlanFeatureBindingModel.quotas))
    )
    if not binding:
        raise_http_error(status_code=404, detail="Binding not found")

    before = {
        "access_mode": binding.access_mode.value,
        "is_enabled": binding.is_enabled,
        "quota_limit": binding.quotas[0].quota_limit if binding.quotas else None,
    }

    # Apply updates
    if payload.access_mode is not None:
        binding.access_mode = AccessMode(payload.access_mode)
    if payload.is_enabled is not None:
        binding.is_enabled = payload.is_enabled
    if payload.quota_limit is not None:
        if not binding.quotas:
            raise_http_error(status_code=400, detail="No quota record found to update")
        binding.quotas[0].quota_limit = payload.quota_limit

    # Audit log
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=resolve_request_id(request),
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="entitlement_quota_updated",
            target_type="plan_entitlement",
            target_id=f"{plan_id}:{feature_id}",
            status="success",
            details={
                "before": before,
                "after": {
                    "access_mode": binding.access_mode.value,
                    "is_enabled": binding.is_enabled,
                    "quota_limit": binding.quotas[0].quota_limit if binding.quotas else None,
                },
            },
        ),
    )
    db.commit()
    return {"status": "success"}
