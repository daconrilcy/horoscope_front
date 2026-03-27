from __future__ import annotations

import logging
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    FeatureCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.services.b2b_api_entitlement_gate import B2BApiAccessDeniedError
from app.services.b2b_canonical_plan_resolver import resolve_b2b_canonical_plan
from app.services.enterprise_quota_usage_service import EnterpriseQuotaUsageService
from app.services.entitlement_types import QuotaDefinition

logger = logging.getLogger(__name__)


class B2BCanonicalUsageSummary(BaseModel):
    source: str = "canonical"
    access_mode: str  # "quota" | "unlimited"
    quota_key: str | None = None
    limit: int | None = None
    used: int | None = None
    remaining: int | None = None
    window_end: datetime | None = None


class B2BCanonicalUsageSummaryService:
    FEATURE_CODE = "b2b_api_access"

    @staticmethod
    def get_summary(db: Session, *, account_id: int) -> B2BCanonicalUsageSummary:
        # 1. Charger l'EnterpriseAccountModel (vérifier existence)
        account = db.scalar(
            select(EnterpriseAccountModel).where(EnterpriseAccountModel.id == account_id)
        )
        if not account:
            logger.warning(
                "b2b_usage_summary_blocked account_id=%s code=%s",
                account_id,
                "b2b_account_not_found",
            )
            raise B2BApiAccessDeniedError(
                code="b2b_account_not_configured",
                details={"reason": "account_not_found"},
            )

        # 2. Résoudre le plan canonique B2B
        canonical_plan = resolve_b2b_canonical_plan(db, account_id)
        if not canonical_plan:
            logger.warning(
                "b2b_usage_summary_blocked account_id=%s code=%s",
                account_id,
                "b2b_no_canonical_plan",
            )
            raise B2BApiAccessDeniedError(
                code="b2b_no_canonical_plan", details={"account_id": account_id}
            )

        # 3. Lire le binding b2b_api_access
        binding_stmt = (
            select(PlanFeatureBindingModel)
            .join(FeatureCatalogModel, PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id)
            .where(
                PlanFeatureBindingModel.plan_id == canonical_plan.id,
                FeatureCatalogModel.feature_code == B2BCanonicalUsageSummaryService.FEATURE_CODE,
            )
        )
        binding = db.scalar(binding_stmt)
        if not binding:
            logger.warning(
                "b2b_usage_summary_blocked account_id=%s code=%s", account_id, "b2b_no_binding"
            )
            raise B2BApiAccessDeniedError(code="b2b_no_binding", details={"account_id": account_id})

        # 4. Selon l'access_mode
        if not binding.is_enabled or binding.access_mode == AccessMode.DISABLED:
            raise B2BApiAccessDeniedError(
                code="b2b_api_access_denied",
                details={"reason": "disabled_by_plan"},
            )

        if binding.access_mode == AccessMode.UNLIMITED:
            return B2BCanonicalUsageSummary(access_mode="unlimited")

        if binding.access_mode == AccessMode.QUOTA:
            # Charger les quotas
            quotas_models = db.scalars(
                select(PlanFeatureQuotaModel).where(
                    PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
                )
            ).all()

            if not quotas_models:
                logger.warning(
                    "b2b_usage_summary_blocked account_id=%s code=%s",
                    account_id,
                    "b2b_no_quota_defined",
                )
                raise B2BApiAccessDeniedError(
                    code="b2b_no_quota_defined", details={"account_id": account_id}
                )

            # Lire l'usage pour chaque quota (lecture seule)
            states = []
            for q_model in quotas_models:
                quota_def = QuotaDefinition(
                    quota_key=q_model.quota_key,
                    quota_limit=q_model.quota_limit,
                    period_unit=q_model.period_unit.value,
                    period_value=q_model.period_value,
                    reset_mode=q_model.reset_mode.value,
                )
                state = EnterpriseQuotaUsageService.get_usage(
                    db,
                    account_id=account_id,
                    feature_code=B2BCanonicalUsageSummaryService.FEATURE_CODE,
                    quota=quota_def,
                )
                states.append(state)

            # Sélectionner le quota avec le remaining le plus bas (le plus restrictif)
            most_restrictive = min(states, key=lambda s: s.remaining)

            return B2BCanonicalUsageSummary(
                access_mode="quota",
                quota_key=most_restrictive.quota_key,
                limit=most_restrictive.quota_limit,
                used=most_restrictive.used,
                remaining=most_restrictive.remaining,
                window_end=most_restrictive.window_end,
            )

        logger.warning(
            "b2b_usage_summary_blocked account_id=%s code=%s",
            account_id,
            "b2b_unknown_access_mode",
        )
        raise B2BApiAccessDeniedError(
            code="b2b_unknown_access_mode",
            details={"access_mode": str(binding.access_mode)},
        )
