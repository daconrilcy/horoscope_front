from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    SourceOrigin,
)
from app.services.b2b_canonical_plan_resolver import resolve_b2b_canonical_plan
from app.services.entitlement_types import QuotaDefinition
from app.services.quota_usage_service import QuotaUsageService


@dataclass
class B2BAuditEntry:
    account_id: int
    company_name: str
    enterprise_plan_id: int | None
    enterprise_plan_code: str | None
    canonical_plan_id: int | None
    canonical_plan_code: str | None
    feature_code: str
    resolution_source: Literal[
        "canonical_quota",
        "canonical_unlimited",
        "canonical_disabled",
        "settings_fallback",
    ]
    reason: Literal[
        "admin_user_id_missing",
        "no_canonical_plan",
        "no_binding",
        "disabled_by_plan",
        "unlimited_access",
        "quota_binding_active",
        "manual_review_required",
    ]
    binding_status: Literal["quota", "unlimited", "disabled", "missing"] | None
    quota_limit: int | None
    remaining: int | None
    window_end: datetime | None
    admin_user_id_present: bool
    manual_review_required: bool


class B2BAuditService:
    FEATURE_CODE = "b2b_api_access"

    @staticmethod
    def list_b2b_entitlement_audit(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 20,
        resolution_source_filter: str | None = None,
        blocker_only: bool = False,
    ) -> tuple[list[B2BAuditEntry], int]:
        all_accounts = db.scalars(
            select(EnterpriseAccountModel).where(EnterpriseAccountModel.status == "active")
        ).all()
        if not all_accounts:
            return [], 0

        account_ids = [account.id for account in all_accounts]
        account_plans = {
            account_plan.enterprise_account_id: account_plan
            for account_plan in db.scalars(
                select(EnterpriseAccountBillingPlanModel).where(
                    EnterpriseAccountBillingPlanModel.enterprise_account_id.in_(account_ids)
                )
            ).all()
        }

        plan_ids = [account_plan.plan_id for account_plan in account_plans.values()]
        enterprise_plans = (
            {
                plan.id: plan
                for plan in db.scalars(
                    select(EnterpriseBillingPlanModel).where(
                        EnterpriseBillingPlanModel.id.in_(plan_ids)
                    )
                ).all()
            }
            if plan_ids
            else {}
        )

        canonical_plans = B2BAuditService._prefetch_canonical_plans(db, plan_ids)
        bindings = B2BAuditService._prefetch_bindings(
            db,
            canonical_plan_ids=[plan.id for plan in canonical_plans.values()],
        )
        quotas = B2BAuditService._prefetch_quotas(
            db,
            binding_ids=[binding.id for binding in bindings.values()],
        )

        entries: list[B2BAuditEntry] = []
        for account in all_accounts:
            account_plan = account_plans.get(account.id)
            enterprise_plan = (
                enterprise_plans.get(account_plan.plan_id) if account_plan is not None else None
            )
            canonical_plan = (
                canonical_plans.get(account_plan.plan_id) if account_plan is not None else None
            )
            binding = bindings.get(canonical_plan.id) if canonical_plan is not None else None
            quota_models = quotas.get(binding.id) if binding is not None else None

            entry = B2BAuditService._audit_account(
                db,
                account,
                acc_plan=account_plan,
                ent_plan=enterprise_plan,
                canonical_plan=canonical_plan,
                binding=binding,
                quota_models=quota_models,
            )

            if resolution_source_filter and entry.resolution_source != resolution_source_filter:
                continue
            if blocker_only and entry.resolution_source != "settings_fallback":
                continue

            entries.append(entry)

        total_count = len(entries)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return entries[start_idx:end_idx], total_count

    @staticmethod
    def _prefetch_canonical_plans(
        db: Session,
        enterprise_plan_ids: list[int],
    ) -> dict[int, PlanCatalogModel]:
        if not enterprise_plan_ids:
            return {}

        return {
            plan.source_id: plan
            for plan in db.scalars(
                select(PlanCatalogModel).where(
                    PlanCatalogModel.source_type
                    == SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
                    PlanCatalogModel.source_id.in_(enterprise_plan_ids),
                    PlanCatalogModel.audience == Audience.B2B,
                    PlanCatalogModel.is_active,
                )
            ).all()
            if plan.source_id is not None
        }

    @staticmethod
    def _prefetch_bindings(
        db: Session,
        *,
        canonical_plan_ids: list[int],
    ) -> dict[int, PlanFeatureBindingModel]:
        if not canonical_plan_ids:
            return {}

        return {
            binding.plan_id: binding
            for binding in db.scalars(
                select(PlanFeatureBindingModel)
                .join(
                    FeatureCatalogModel,
                    PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id,
                )
                .where(
                    PlanFeatureBindingModel.plan_id.in_(canonical_plan_ids),
                    FeatureCatalogModel.feature_code == B2BAuditService.FEATURE_CODE,
                )
            ).all()
        }

    @staticmethod
    def _prefetch_quotas(
        db: Session,
        *,
        binding_ids: list[int],
    ) -> dict[int, list[PlanFeatureQuotaModel]]:
        if not binding_ids:
            return {}

        quotas_by_binding: dict[int, list[PlanFeatureQuotaModel]] = {
            binding_id: [] for binding_id in binding_ids
        }
        for quota in db.scalars(
            select(PlanFeatureQuotaModel).where(
                PlanFeatureQuotaModel.plan_feature_binding_id.in_(binding_ids)
            )
        ).all():
            quotas_by_binding.setdefault(quota.plan_feature_binding_id, []).append(quota)
        return quotas_by_binding

    @staticmethod
    def _audit_account(
        db: Session,
        account: EnterpriseAccountModel,
        *,
        acc_plan: EnterpriseAccountBillingPlanModel | None = None,
        ent_plan: EnterpriseBillingPlanModel | None = None,
        canonical_plan: PlanCatalogModel | None = None,
        binding: PlanFeatureBindingModel | None = None,
        quota_models: list[PlanFeatureQuotaModel] | None = None,
    ) -> B2BAuditEntry:
        enterprise_plan = ent_plan
        if acc_plan is None:
            acc_plan = db.scalar(
                select(EnterpriseAccountBillingPlanModel)
                .where(EnterpriseAccountBillingPlanModel.enterprise_account_id == account.id)
                .limit(1)
            )

        if acc_plan is not None and enterprise_plan is None:
            enterprise_plan = db.scalar(
                select(EnterpriseBillingPlanModel)
                .where(EnterpriseBillingPlanModel.id == acc_plan.plan_id)
                .limit(1)
            )

        enterprise_plan_id = enterprise_plan.id if enterprise_plan is not None else None
        enterprise_plan_code = enterprise_plan.code if enterprise_plan is not None else None
        admin_user_id_present = account.admin_user_id is not None

        if not admin_user_id_present:
            return B2BAuditEntry(
                account_id=account.id,
                company_name=account.company_name,
                enterprise_plan_id=enterprise_plan_id,
                enterprise_plan_code=enterprise_plan_code,
                canonical_plan_id=None,
                canonical_plan_code=None,
                feature_code=B2BAuditService.FEATURE_CODE,
                resolution_source="settings_fallback",
                reason="admin_user_id_missing",
                binding_status=None,
                quota_limit=None,
                remaining=None,
                window_end=None,
                admin_user_id_present=False,
                manual_review_required=False,
            )

        if canonical_plan is None:
            canonical_plan = resolve_b2b_canonical_plan(db, account.id)

        if canonical_plan is None:
            manual_review_required = B2BAuditService._is_manual_review_required(
                enterprise_plan,
                binding=None,
                quota_models=None,
            )
            return B2BAuditEntry(
                account_id=account.id,
                company_name=account.company_name,
                enterprise_plan_id=enterprise_plan_id,
                enterprise_plan_code=enterprise_plan_code,
                canonical_plan_id=None,
                canonical_plan_code=None,
                feature_code=B2BAuditService.FEATURE_CODE,
                resolution_source="settings_fallback",
                reason=(
                    "manual_review_required" if manual_review_required else "no_canonical_plan"
                ),
                binding_status=None,
                quota_limit=None,
                remaining=None,
                window_end=None,
                admin_user_id_present=True,
                manual_review_required=manual_review_required,
            )

        canonical_plan_id = canonical_plan.id
        canonical_plan_code = canonical_plan.plan_code

        if binding is None:
            binding = db.scalar(
                select(PlanFeatureBindingModel)
                .join(
                    FeatureCatalogModel,
                    PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id,
                )
                .where(
                    PlanFeatureBindingModel.plan_id == canonical_plan.id,
                    FeatureCatalogModel.feature_code == B2BAuditService.FEATURE_CODE,
                )
                .limit(1)
            )

        if binding is None:
            manual_review_required = B2BAuditService._is_manual_review_required(
                enterprise_plan,
                binding=None,
                quota_models=None,
            )
            return B2BAuditEntry(
                account_id=account.id,
                company_name=account.company_name,
                enterprise_plan_id=enterprise_plan_id,
                enterprise_plan_code=enterprise_plan_code,
                canonical_plan_id=canonical_plan_id,
                canonical_plan_code=canonical_plan_code,
                feature_code=B2BAuditService.FEATURE_CODE,
                resolution_source="settings_fallback",
                reason="manual_review_required" if manual_review_required else "no_binding",
                binding_status="missing",
                quota_limit=None,
                remaining=None,
                window_end=None,
                admin_user_id_present=True,
                manual_review_required=manual_review_required,
            )

        if not binding.is_enabled or binding.access_mode == AccessMode.DISABLED:
            return B2BAuditEntry(
                account_id=account.id,
                company_name=account.company_name,
                enterprise_plan_id=enterprise_plan_id,
                enterprise_plan_code=enterprise_plan_code,
                canonical_plan_id=canonical_plan_id,
                canonical_plan_code=canonical_plan_code,
                feature_code=B2BAuditService.FEATURE_CODE,
                resolution_source="canonical_disabled",
                reason="disabled_by_plan",
                binding_status="disabled",
                quota_limit=None,
                remaining=None,
                window_end=None,
                admin_user_id_present=True,
                manual_review_required=False,
            )

        if binding.access_mode == AccessMode.UNLIMITED:
            return B2BAuditEntry(
                account_id=account.id,
                company_name=account.company_name,
                enterprise_plan_id=enterprise_plan_id,
                enterprise_plan_code=enterprise_plan_code,
                canonical_plan_id=canonical_plan_id,
                canonical_plan_code=canonical_plan_code,
                feature_code=B2BAuditService.FEATURE_CODE,
                resolution_source="canonical_unlimited",
                reason="unlimited_access",
                binding_status="unlimited",
                quota_limit=None,
                remaining=None,
                window_end=None,
                admin_user_id_present=True,
                manual_review_required=False,
            )

        if quota_models is None:
            quota_models = db.scalars(
                select(PlanFeatureQuotaModel).where(
                    PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
                )
            ).all()

        valid_quota_models = [
            quota_model for quota_model in quota_models if quota_model.quota_limit > 0
        ]
        manual_review_required = B2BAuditService._is_manual_review_required(
            enterprise_plan,
            binding=binding,
            quota_models=valid_quota_models,
        )
        if not valid_quota_models:
            return B2BAuditEntry(
                account_id=account.id,
                company_name=account.company_name,
                enterprise_plan_id=enterprise_plan_id,
                enterprise_plan_code=enterprise_plan_code,
                canonical_plan_id=canonical_plan_id,
                canonical_plan_code=canonical_plan_code,
                feature_code=B2BAuditService.FEATURE_CODE,
                resolution_source="settings_fallback",
                reason="manual_review_required" if manual_review_required else "no_binding",
                binding_status="quota",
                quota_limit=None,
                remaining=None,
                window_end=None,
                admin_user_id_present=True,
                manual_review_required=manual_review_required,
            )

        quota_model = valid_quota_models[0]
        quota_def = QuotaDefinition(
            quota_key=quota_model.quota_key,
            quota_limit=quota_model.quota_limit,
            period_unit=quota_model.period_unit.value,
            period_value=quota_model.period_value,
            reset_mode=quota_model.reset_mode.value,
        )
        usage_state = QuotaUsageService.get_usage(
            db,
            user_id=account.admin_user_id,
            feature_code=B2BAuditService.FEATURE_CODE,
            quota=quota_def,
        )
        return B2BAuditEntry(
            account_id=account.id,
            company_name=account.company_name,
            enterprise_plan_id=enterprise_plan_id,
            enterprise_plan_code=enterprise_plan_code,
            canonical_plan_id=canonical_plan_id,
            canonical_plan_code=canonical_plan_code,
            feature_code=B2BAuditService.FEATURE_CODE,
            resolution_source="canonical_quota",
            reason="quota_binding_active",
            binding_status="quota",
            quota_limit=usage_state.quota_limit,
            remaining=usage_state.remaining,
            window_end=usage_state.window_end,
            admin_user_id_present=True,
            manual_review_required=False,
        )

    @staticmethod
    def _is_manual_review_required(
        enterprise_plan: EnterpriseBillingPlanModel | None,
        *,
        binding: PlanFeatureBindingModel | None,
        quota_models: list[PlanFeatureQuotaModel] | None,
    ) -> bool:
        if enterprise_plan is None or enterprise_plan.included_monthly_units != 0:
            return False
        if binding is None:
            return True
        if quota_models is None:
            return True
        return len(quota_models) == 0
