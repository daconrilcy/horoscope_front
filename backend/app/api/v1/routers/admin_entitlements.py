from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.admin_entitlements import AdminEntitlementMatrixResponse
from app.infra.db.models.product_entitlements import (
    AccessMode,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
)
from app.infra.db.session import get_db_session

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
    bindings = db.scalars(
        select(PlanFeatureBindingModel)
        .options(joinedload(PlanFeatureBindingModel.quotas))
    ).unique().all()

    cells = {}
    for b in bindings:
        key = f"{b.plan_id}:{b.feature_id}"
        
        # Take the first quota if available (MVP simplification)
        quota = b.quotas[0] if b.quotas else None
        
        is_incoherent = (b.access_mode == AccessMode.QUOTA and (not quota or quota.quota_limit <= 0))
        
        cells[key] = {
            "access_mode": b.access_mode.value,
            "is_enabled": b.is_enabled,
            "variant_code": b.variant_code,
            "quota_limit": quota.quota_limit if quota else None,
            "period": f"{quota.period_value} {quota.period_unit.value}" if quota else None,
            "is_incoherent": is_incoherent
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
        "cells": cells
    }
