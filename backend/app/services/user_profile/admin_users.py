"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.services.billing.service import BillingService
from app.services.entitlement.entitlement_types import QuotaDefinition
from app.services.quota.usage_service import QuotaUsageService

logger = logging.getLogger(__name__)


def _mask_id(raw_id: str | None) -> str | None:
    if not raw_id:
        return None
    if len(raw_id) <= 11:
        return raw_id
    return f"{raw_id[:7]}...{raw_id[-4:]}"


def _build_user_quotas(*, db: Session, user_id: int, plan_code: str) -> list[dict[str, object]]:
    quotas_by_key: dict[tuple[str, str, str, int, str], dict[str, object]] = {}
    period_order = {"day": 0, "week": 1, "month": 2, "year": 3, "lifetime": 4}

    if plan_code:
        try:
            plan = db.scalar(
                select(PlanCatalogModel)
                .where(
                    PlanCatalogModel.plan_code == plan_code,
                    PlanCatalogModel.audience == Audience.B2C,
                    PlanCatalogModel.is_active.is_(True),
                )
                .limit(1)
            )
            feature = db.scalar(
                select(FeatureCatalogModel)
                .where(
                    FeatureCatalogModel.feature_code == BillingService._BILLING_QUOTA_FEATURE,
                    FeatureCatalogModel.is_active.is_(True),
                )
                .limit(1)
            )
        except Exception:
            logger.warning("admin_user_detail_quota_resolution_failed user_id=%s", user_id)
        else:
            if plan is not None and feature is not None:
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
                if binding is not None:
                    quota_rows = db.scalars(
                        select(PlanFeatureQuotaModel)
                        .where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
                        .order_by(
                            asc(PlanFeatureQuotaModel.period_value),
                            asc(PlanFeatureQuotaModel.period_unit),
                            asc(PlanFeatureQuotaModel.quota_key),
                        )
                    ).all()
                    for quota_row in quota_rows:
                        usage = QuotaUsageService.get_usage(
                            db,
                            user_id=user_id,
                            feature_code=feature.feature_code,
                            quota=QuotaDefinition(
                                quota_key=quota_row.quota_key,
                                quota_limit=quota_row.quota_limit,
                                period_unit=quota_row.period_unit.value,
                                period_value=quota_row.period_value,
                                reset_mode=quota_row.reset_mode.value,
                            ),
                        )
                        quotas_by_key[
                            (
                                usage.feature_code,
                                usage.quota_key,
                                usage.period_unit,
                                usage.period_value,
                                usage.reset_mode,
                            )
                        ] = {
                            "feature_code": usage.feature_code,
                            "used": usage.used,
                            "limit": usage.quota_limit,
                            "period": f"{usage.period_value} {usage.period_unit}",
                        }

    usage_counters = db.scalars(
        select(FeatureUsageCounterModel).where(FeatureUsageCounterModel.user_id == user_id)
    ).all()
    for counter in usage_counters:
        quotas_by_key.setdefault(
            (
                counter.feature_code,
                counter.quota_key,
                counter.period_unit.value,
                counter.period_value,
                counter.reset_mode.value,
            ),
            {
                "feature_code": counter.feature_code,
                "used": counter.used_count,
                "limit": None,
                "period": f"{counter.period_value} {counter.period_unit.value}",
            },
        )

    return sorted(
        quotas_by_key.values(),
        key=lambda item: (
            str(item["feature_code"]),
            period_order.get(str(item["period"]).split(" ", maxsplit=1)[-1], 99),
            str(item["period"]),
        ),
    )
