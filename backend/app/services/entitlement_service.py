from __future__ import annotations

import logging
from dataclasses import dataclass
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

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.services.billing_service import SubscriptionStatusData

logger = logging.getLogger(__name__)

_ACTIVE_BILLING_STATUSES = frozenset({"active", "trialing"})


@dataclass(frozen=True)
class QuotaDefinition:
    """Définition d'un quota pour une feature."""

    quota_key: str
    quota_limit: int
    period_unit: str
    period_value: int
    reset_mode: str


@dataclass
class FeatureEntitlement:
    """Droit d'accès calculé pour une feature."""

    plan_code: str
    billing_status: str
    is_enabled_by_plan: bool
    access_mode: str
    variant_code: str | None
    quotas: list[QuotaDefinition]
    final_access: bool
    reason: str


class EntitlementService:
    @staticmethod
    def get_user_canonical_plan(db: Session, user_id: int) -> PlanCatalogModel | None:
        subscription: SubscriptionStatusData = BillingService.get_subscription_status(db, user_id=user_id)
        if not subscription.plan:
            return None

        plan_code = subscription.plan.code
        plan = db.scalar(
            select(PlanCatalogModel)
            .where(PlanCatalogModel.plan_code == plan_code)
            .limit(1)
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
        subscription: SubscriptionStatusData = BillingService.get_subscription_status(db, user_id=user_id)

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
            select(PlanCatalogModel)
            .where(PlanCatalogModel.plan_code == plan_code)
            .limit(1)
        )
        feature = db.scalar(
            select(FeatureCatalogModel)
            .where(FeatureCatalogModel.feature_code == feature_code)
            .limit(1)
        )

        if not plan:
            logger.warning(
                "Canonical plan missing for billing plan_code '%s' and user %d. Falling back when possible.",
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
                is_enabled_by_plan = binding.is_enabled and binding.access_mode != AccessMode.DISABLED
                quotas: list[QuotaDefinition] = []

                if binding.access_mode == AccessMode.QUOTA:
                    quota_models = db.scalars(
                        select(PlanFeatureQuotaModel)
                        .where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
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

                final_access = is_billing_active and is_enabled_by_plan
                reason = "billing_inactive" if not is_billing_active else "canonical_binding"

                return FeatureEntitlement(
                    plan_code=plan_code,
                    billing_status=billing_status,
                    is_enabled_by_plan=is_enabled_by_plan,
                    access_mode=binding.access_mode.value,
                    variant_code=binding.variant_code,
                    quotas=quotas,
                    final_access=final_access,
                    reason=reason,
                )

            if feature_code == "astrologer_chat":
                fallback = EntitlementService._legacy_fallback(subscription, feature_code)
                if not is_billing_active:
                    fallback.final_access = False
                    fallback.reason = "billing_inactive"
                return fallback

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

        fallback = EntitlementService._legacy_fallback(subscription, feature_code)
        if not is_billing_active:
            fallback.final_access = False
            fallback.reason = "billing_inactive"
        return fallback

    @staticmethod
    def _legacy_fallback(subscription: SubscriptionStatusData, feature_code: str) -> FeatureEntitlement:
        plan_code = subscription.plan.code if subscription.plan else "none"
        billing_status = subscription.status
        is_billing_active = billing_status in _ACTIVE_BILLING_STATUSES

        if feature_code == "astrologer_chat":
            daily_limit = subscription.plan.daily_message_limit if subscription.plan else 0
            if daily_limit > 0:
                access_mode = AccessMode.QUOTA.value
                is_enabled_by_plan = True
                quotas: list[QuotaDefinition] = [
                    QuotaDefinition(
                        quota_key="messages",
                        quota_limit=daily_limit,
                        period_unit="day",
                        period_value=1,
                        reset_mode="calendar",
                    )
                ]
            else:
                access_mode = AccessMode.DISABLED.value
                is_enabled_by_plan = False
                quotas = []

            return FeatureEntitlement(
                plan_code=plan_code,
                billing_status=billing_status,
                is_enabled_by_plan=is_enabled_by_plan,
                access_mode=access_mode,
                variant_code=None,
                quotas=quotas,
                final_access=is_billing_active and is_enabled_by_plan,
                reason="legacy_fallback",
            )

        return FeatureEntitlement(
            plan_code=plan_code,
            billing_status=billing_status,
            is_enabled_by_plan=False,
            access_mode="unknown",
            variant_code=None,
            quotas=[],
            final_access=False,
            reason="feature_unknown",
        )
