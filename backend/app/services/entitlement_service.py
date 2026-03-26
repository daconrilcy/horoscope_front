from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.infra.db.models.product_entitlements import (
    AccessMode,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.services.billing_service import BillingService
from app.services.entitlement_types import FeatureEntitlement, QuotaDefinition
from app.services.quota_usage_service import QuotaUsageService

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.services.billing_service import SubscriptionStatusData

logger = logging.getLogger(__name__)

_ACTIVE_BILLING_STATUSES = frozenset({"active", "trialing"})


class EntitlementService:
    @staticmethod
    def get_user_canonical_plan(db: Session, user_id: int) -> PlanCatalogModel | None:
        subscription: SubscriptionStatusData = BillingService.get_subscription_status(
            db, user_id=user_id
        )
        if not subscription.plan:
            return None

        plan_code = subscription.plan.code
        plan = db.scalar(
            select(PlanCatalogModel).where(PlanCatalogModel.plan_code == plan_code).limit(1)
        )

        if not plan:
            logger.warning(
                "Plan code '%s' found in billing but missing from plan_catalog for user %d",
                plan_code,
                user_id,
            )
            return None

        return plan

    @staticmethod
    def get_feature_entitlement(db: Session, user_id: int, feature_code: str) -> FeatureEntitlement:
        subscription: SubscriptionStatusData = BillingService.get_subscription_status(
            db, user_id=user_id
        )

        if not subscription.plan or subscription.status == "none":
            return FeatureEntitlement(
                plan_code="none",
                billing_status="none",
                is_enabled_by_plan=False,
                access_mode="unknown",
                variant_code=None,
                quotas=[],
                final_access=False,
                reason="no_plan",
            )

        plan_code = subscription.plan.code
        billing_status = subscription.status
        is_billing_active = billing_status in _ACTIVE_BILLING_STATUSES

        plan = db.scalar(
            select(PlanCatalogModel).where(PlanCatalogModel.plan_code == plan_code).limit(1)
        )
        feature = db.scalar(
            select(FeatureCatalogModel)
            .where(FeatureCatalogModel.feature_code == feature_code)
            .limit(1)
        )

        if not plan:
            logger.warning(
                "Canonical plan missing for billing plan_code '%s' and user %d. "
                "Falling back when possible.",
                plan_code,
                user_id,
            )

        if plan and feature:
            binding = db.scalar(
                select(PlanFeatureBindingModel)
                .where(
                    PlanFeatureBindingModel.plan_id == plan.id,
                    PlanFeatureBindingModel.feature_id == feature.id,
                )
                .limit(1)
            )

            if binding:
                is_enabled_by_plan = (
                    binding.is_enabled and binding.access_mode != AccessMode.DISABLED
                )
                quotas: list[QuotaDefinition] = []
                usage_states = []
                quota_exhausted = False
                evaluation_dt = datetime.now(timezone.utc)

                if binding.access_mode == AccessMode.QUOTA:
                    quota_models = db.scalars(
                        select(PlanFeatureQuotaModel).where(
                            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
                        )
                    ).all()

                    if not quota_models:
                        logger.warning(
                            "Binding %d has access_mode=quota but no quotas defined "
                            "for plan '%s' feature '%s'. Disabling access.",
                            binding.id,
                            plan_code,
                            feature_code,
                        )
                        is_enabled_by_plan = False
                    else:
                        quotas = [
                            QuotaDefinition(
                                quota_key=q.quota_key,
                                quota_limit=q.quota_limit,
                                period_unit=q.period_unit.value,
                                period_value=q.period_value,
                                reset_mode=q.reset_mode.value,
                            )
                            for q in quota_models
                        ]

                        unsupported_quota = next(
                            (quota for quota in quotas if quota.reset_mode == "rolling"),
                            None,
                        )
                        if unsupported_quota is not None:
                            logger.warning(
                                "Binding %d has unsupported rolling quota '%s' for plan '%s' "
                                "feature '%s'. Disabling access until rolling windows are "
                                "supported.",
                                binding.id,
                                unsupported_quota.quota_key,
                                plan_code,
                                feature_code,
                            )
                            is_enabled_by_plan = False
                        elif is_billing_active:
                            usage_states = [
                                QuotaUsageService.get_usage(
                                    db,
                                    user_id=user_id,
                                    feature_code=feature_code,
                                    quota=q,
                                    ref_dt=evaluation_dt,
                                )
                                for q in quotas
                            ]
                            quota_exhausted = any(s.exhausted for s in usage_states)

                final_access = is_billing_active and is_enabled_by_plan and not quota_exhausted
                if not is_billing_active:
                    reason = "billing_inactive"
                elif not is_enabled_by_plan:
                    reason = "disabled_by_plan"
                else:
                    reason = "canonical_binding"

                return FeatureEntitlement(
                    plan_code=plan_code,
                    billing_status=billing_status,
                    is_enabled_by_plan=is_enabled_by_plan,
                    access_mode=binding.access_mode.value,
                    variant_code=binding.variant_code,
                    quotas=quotas,
                    final_access=final_access,
                    reason=reason,
                    usage_states=usage_states,
                    quota_exhausted=quota_exhausted,
                )

            return FeatureEntitlement(
                plan_code=plan_code,
                billing_status=billing_status,
                is_enabled_by_plan=False,
                access_mode="unknown",
                variant_code=None,
                quotas=[],
                final_access=False,
                reason="billing_inactive" if not is_billing_active else "canonical_no_binding",
            )

        return FeatureEntitlement(
            plan_code=plan_code,
            billing_status=billing_status,
            is_enabled_by_plan=False,
            access_mode="unknown",
            variant_code=None,
            quotas=[],
            final_access=False,
            reason="billing_inactive" if not is_billing_active else "feature_unknown",
        )
