from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    FeatureCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.services.b2b_canonical_plan_resolver import resolve_b2b_canonical_plan
from app.services.entitlement_types import QuotaDefinition, UsageState
from app.services.quota_usage_service import QuotaExhaustedError, QuotaUsageService

logger = logging.getLogger(__name__)


class B2BApiAccessDeniedError(Exception):
    def __init__(
        self,
        code: str,
        message: str = "B2B API access denied",
        details: dict | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{message} (code={code})")


class B2BApiQuotaExceededError(Exception):
    def __init__(
        self,
        code: str,
        message: str = "B2B API quota exceeded",
        details: dict | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{message} (code={code})")


@dataclass
class B2BApiEntitlementResult:
    path: Literal["canonical_quota", "canonical_unlimited", "settings_fallback"]
    usage_states: list[UsageState] = field(default_factory=list)
    source: str = "canonical"


class B2BApiEntitlementGate:
    FEATURE_CODE = "b2b_api_access"

    @staticmethod
    def check_and_consume(db: Session, *, account_id: int) -> B2BApiEntitlementResult:
        # 1. Charger l'EnterpriseAccountModel -> admin_user_id
        account = db.scalar(
            select(EnterpriseAccountModel).where(EnterpriseAccountModel.id == account_id)
        )
        if not account or account.admin_user_id is None:
            logger.warning(
                "b2b_api_entitlement_gate.admin_user_id_missing account_id=%s", account_id
            )
            return B2BApiEntitlementResult(path="settings_fallback")

        admin_user_id = account.admin_user_id

        # 2. Résoudre le plan canonique B2B
        canonical_plan = resolve_b2b_canonical_plan(db, account_id)
        if not canonical_plan:
            return B2BApiEntitlementResult(path="settings_fallback")

        # 3. Lire le binding b2b_api_access
        binding_stmt = (
            select(PlanFeatureBindingModel)
            .join(FeatureCatalogModel, PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id)
            .where(
                PlanFeatureBindingModel.plan_id == canonical_plan.id,
                FeatureCatalogModel.feature_code == B2BApiEntitlementGate.FEATURE_CODE,
            )
        )
        binding = db.scalar(binding_stmt)
        if not binding:
            return B2BApiEntitlementResult(path="settings_fallback")

        # 4. Selon l'access_mode
        if not binding.is_enabled or binding.access_mode == AccessMode.DISABLED:
            # AC: 4 — le canonique gagne même si settings permissifs
            raise B2BApiAccessDeniedError(
                code="b2b_api_access_denied",
                details={"reason": "disabled_by_plan"},
            )

        if binding.access_mode == AccessMode.UNLIMITED:
            return B2BApiEntitlementResult(path="canonical_unlimited")

        if binding.access_mode == AccessMode.QUOTA:
            # Charger les quotas
            quotas_models = db.scalars(
                select(PlanFeatureQuotaModel).where(
                    PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
                )
            ).all()

            if not quotas_models:
                # AC: 8 - cas manual-review-required / non bindé
                return B2BApiEntitlementResult(path="settings_fallback")

            # Consommer (AC: 2)
            consumed_states: list[UsageState] = []
            for q_model in quotas_models:
                quota_def = QuotaDefinition(
                    quota_key=q_model.quota_key,
                    quota_limit=q_model.quota_limit,
                    period_unit=q_model.period_unit.value,
                    period_value=q_model.period_value,
                    reset_mode=q_model.reset_mode.value,
                )
                try:
                    state = QuotaUsageService.consume(
                        db,
                        user_id=admin_user_id,
                        feature_code=B2BApiEntitlementGate.FEATURE_CODE,
                        quota=quota_def,
                        amount=1,
                    )
                    consumed_states.append(state)
                except QuotaExhaustedError as exc:
                    # AC: 5
                    raise B2BApiQuotaExceededError(
                        code="b2b_api_quota_exceeded",
                        details={
                            "quota_key": exc.quota_key,
                            "used": str(exc.used),
                            "limit": str(exc.limit),
                        },
                    ) from exc

            return B2BApiEntitlementResult(path="canonical_quota", usage_states=consumed_states)

        return B2BApiEntitlementResult(path="settings_fallback")
