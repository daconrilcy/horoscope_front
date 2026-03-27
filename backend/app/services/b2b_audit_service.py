from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    FeatureCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.services.b2b_canonical_plan_resolver import resolve_b2b_canonical_plan
from app.services.entitlement_types import QuotaDefinition, UsageState
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
        "canonical_quota", "canonical_unlimited", "canonical_disabled", "settings_fallback"
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
        # 1. Base query for active enterprise accounts
        stmt = select(EnterpriseAccountModel).where(EnterpriseAccountModel.status == "active")
        all_accounts = db.scalars(stmt).all()
        
        if not all_accounts:
            return [], 0

        # 2. Pre-fetch related data to avoid N+1 queries
        account_ids = [acc.id for acc in all_accounts]
        
        # account_id -> billing_plan_binding
        acc_plan_stmt = select(EnterpriseAccountBillingPlanModel).where(
            EnterpriseAccountBillingPlanModel.enterprise_account_id.in_(account_ids)
        )
        acc_plans = {ap.enterprise_account_id: ap for ap in db.scalars(acc_plan_stmt).all()}
        
        # plan_id -> enterprise_plan
        plan_ids = [ap.plan_id for ap in acc_plans.values()]
        ent_plans = {}
        if plan_ids:
            ent_plan_stmt = select(EnterpriseBillingPlanModel).where(
                EnterpriseBillingPlanModel.id.in_(plan_ids)
            )
            ent_plans = {p.id: p for p in db.scalars(ent_plan_stmt).all()}

        entries: list[B2BAuditEntry] = []
        for account in all_accounts:
            acc_plan = acc_plans.get(account.id)
            ent_plan = ent_plans.get(acc_plan.plan_id) if acc_plan else None
            
            entry = B2BAuditService._audit_account(db, account, acc_plan=acc_plan, ent_plan=ent_plan)
            
            # Apply filters
            if resolution_source_filter and entry.resolution_source != resolution_source_filter:
                continue
            
            if blocker_only and entry.resolution_source not in ("settings_fallback", "canonical_disabled"):
                continue
                
            entries.append(entry)

        # 3. Pagination
        total_count = len(entries)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_entries = entries[start_idx:end_idx]

        return paginated_entries, total_count

    @staticmethod
    def _audit_account(
        db: Session, 
        account: EnterpriseAccountModel,
        *,
        acc_plan: EnterpriseAccountBillingPlanModel | None = None,
        ent_plan: EnterpriseBillingPlanModel | None = None,
    ) -> B2BAuditEntry:
        # Initial default values
        enterprise_plan_id = ent_plan.id if ent_plan else None
        enterprise_plan_code = ent_plan.code if ent_plan else None
        canonical_plan_id = None
        canonical_plan_code = None
        admin_user_id_present = account.admin_user_id is not None

        # 1. Check admin_user_id
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

        # 2. Resolve plans
        # Use provided or fetch if missing (fallback for unit tests or specific calls)
        if not acc_plan:
            acc_plan = db.scalar(
                select(EnterpriseAccountBillingPlanModel)
                .where(EnterpriseAccountBillingPlanModel.enterprise_account_id == account.id)
                .limit(1)
            )
        
        enterprise_plan = ent_plan # variable for manual review check
        if acc_plan and not enterprise_plan:
            enterprise_plan = db.scalar(
                select(EnterpriseBillingPlanModel).where(EnterpriseBillingPlanModel.id == acc_plan.plan_id)
            )
        
        if enterprise_plan:
            enterprise_plan_id = enterprise_plan.id
            enterprise_plan_code = enterprise_plan.code

        canonical_plan = resolve_b2b_canonical_plan(db, account.id)
        if canonical_plan:
            canonical_plan_id = canonical_plan.id
            canonical_plan_code = canonical_plan.plan_code
        else:
            # Fallback check for manual review
            is_manual = enterprise_plan is not None and enterprise_plan.included_monthly_units == 0
            return B2BAuditEntry(
                account_id=account.id,
                company_name=account.company_name,
                enterprise_plan_id=enterprise_plan_id,
                enterprise_plan_code=enterprise_plan_code,
                canonical_plan_id=None,
                canonical_plan_code=None,
                feature_code=B2BAuditService.FEATURE_CODE,
                resolution_source="settings_fallback",
                reason="manual_review_required" if is_manual else "no_canonical_plan",
                binding_status=None,
                quota_limit=None,
                remaining=None,
                window_end=None,
                admin_user_id_present=True,
                manual_review_required=is_manual,
            )

        # 3. Resolve binding
        binding = db.scalar(
            select(PlanFeatureBindingModel)
            .join(FeatureCatalogModel, PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id)
            .where(
                PlanFeatureBindingModel.plan_id == canonical_plan.id,
                FeatureCatalogModel.feature_code == B2BAuditService.FEATURE_CODE,
            )
        )

        if not binding:
            is_manual = enterprise_plan is not None and enterprise_plan.included_monthly_units == 0
            return B2BAuditEntry(
                account_id=account.id,
                company_name=account.company_name,
                enterprise_plan_id=enterprise_plan_id,
                enterprise_plan_code=enterprise_plan_code,
                canonical_plan_id=canonical_plan_id,
                canonical_plan_code=canonical_plan_code,
                feature_code=B2BAuditService.FEATURE_CODE,
                resolution_source="settings_fallback",
                reason="manual_review_required" if is_manual else "no_binding",
                binding_status="missing",
                quota_limit=None,
                remaining=None,
                window_end=None,
                admin_user_id_present=True,
                manual_review_required=is_manual,
            )

        # 4. Resolve status
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

        if binding.access_mode == AccessMode.QUOTA:
            quotas_models = db.scalars(
                select(PlanFeatureQuotaModel).where(
                    PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
                )
            ).all()

            if not quotas_models:
                is_manual = enterprise_plan is not None and enterprise_plan.included_monthly_units == 0
                return B2BAuditEntry(
                    account_id=account.id,
                    company_name=account.company_name,
                    enterprise_plan_id=enterprise_plan_id,
                    enterprise_plan_code=enterprise_plan_code,
                    canonical_plan_id=canonical_plan_id,
                    canonical_plan_code=canonical_plan_code,
                    feature_code=B2BAuditService.FEATURE_CODE,
                    resolution_source="settings_fallback",
                    reason="manual_review_required" if is_manual else "no_binding", # logically no quota defined
                    binding_status="quota",
                    quota_limit=None,
                    remaining=None,
                    window_end=None,
                    admin_user_id_present=True,
                    manual_review_required=is_manual,
                )

            # For B2B audit, we take the first quota (usually only one: calls/month)
            q_model = quotas_models[0]
            quota_def = QuotaDefinition(
                quota_key=q_model.quota_key,
                quota_limit=q_model.quota_limit,
                period_unit=q_model.period_unit.value,
                period_value=q_model.period_value,
                reset_mode=q_model.reset_mode.value,
            )
            
            # Read-only usage call
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

        # Fallback (should not happen with AccessMode enum)
        return B2BAuditEntry(
            account_id=account.id,
            company_name=account.company_name,
            enterprise_plan_id=enterprise_plan_id,
            enterprise_plan_code=enterprise_plan_code,
            canonical_plan_id=canonical_plan_id,
            canonical_plan_code=canonical_plan_code,
            feature_code=B2BAuditService.FEATURE_CODE,
            resolution_source="settings_fallback",
            reason="no_binding",
            binding_status=None,
            quota_limit=None,
            remaining=None,
            window_end=None,
            admin_user_id_present=True,
            manual_review_required=False,
        )
