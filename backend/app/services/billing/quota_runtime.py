"""Resout le quota courant expose par le domaine billing."""

from __future__ import annotations

from sqlalchemy import asc, case, desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.services.billing.models import CurrentQuotaData
from app.services.entitlement.entitlement_types import QuotaDefinition
from app.services.quota_usage_service import QuotaUsageService


def resolve_current_quota(
    db: Session,
    *,
    user_id: int,
    feature_code: str,
    plan_code: str,
) -> CurrentQuotaData | None:
    """Resout le quota courant de la feature principale exposee par billing."""
    plan = db.scalar(
        select(PlanCatalogModel)
        .where(
            PlanCatalogModel.plan_code == plan_code,
            PlanCatalogModel.audience == Audience.B2C,
            PlanCatalogModel.is_active.is_(True),
        )
        .limit(1)
    )
    if plan is None:
        return None

    feature = db.scalar(
        select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == feature_code).limit(1)
    )
    if feature is None:
        return None

    binding = db.scalar(
        select(PlanFeatureBindingModel)
        .where(
            PlanFeatureBindingModel.plan_id == plan.id,
            PlanFeatureBindingModel.feature_id == feature.id,
            PlanFeatureBindingModel.is_enabled.is_(True),
            PlanFeatureBindingModel.access_mode == AccessMode.QUOTA,
        )
        .limit(1)
    )
    if binding is None:
        return None

    quota_row = db.scalar(
        select(PlanFeatureQuotaModel)
        .where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
        .order_by(
            asc(PlanFeatureQuotaModel.quota_key),
            desc(case((PlanFeatureQuotaModel.period_unit == "month", 1), else_=0)),
            asc(PlanFeatureQuotaModel.period_value),
        )
        .limit(1)
    )
    if quota_row is None:
        return None

    quota_definition = QuotaDefinition(
        quota_key=quota_row.quota_key,
        quota_limit=quota_row.quota_limit,
        period_unit=quota_row.period_unit.value,
        period_value=quota_row.period_value,
        reset_mode=quota_row.reset_mode.value,
    )
    usage = QuotaUsageService.get_usage(
        db,
        user_id=user_id,
        feature_code=feature_code,
        quota=quota_definition,
    )
    return CurrentQuotaData(
        feature_code=feature_code,
        quota_key=usage.quota_key,
        quota_limit=usage.quota_limit,
        consumed=usage.used,
        remaining=usage.remaining,
        period_unit=usage.period_unit,
        period_value=usage.period_value,
        reset_mode=usage.reset_mode,
        window_start=usage.window_start,
        window_end=usage.window_end,
    )
