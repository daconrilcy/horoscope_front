from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
)
from app.infra.db.models.product_entitlements import (
    Audience,
    PlanCatalogModel,
    SourceOrigin,
)


def resolve_b2b_canonical_plan(db: Session, account_id: int) -> PlanCatalogModel | None:
    # account_id -> enterprise_account_billing_plans
    account_plan = db.scalar(
        select(EnterpriseAccountBillingPlanModel)
        .where(EnterpriseAccountBillingPlanModel.enterprise_account_id == account_id)
        .limit(1)
    )
    if not account_plan:
        return None

    # plan_id -> plan_catalog
    canonical_plan = db.scalar(
        select(PlanCatalogModel)
        .where(
            PlanCatalogModel.source_type == SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
            PlanCatalogModel.source_id == account_plan.plan_id,
            PlanCatalogModel.audience == Audience.B2B,
            PlanCatalogModel.is_active == True,
        )
        .limit(1)
    )
    return canonical_plan
