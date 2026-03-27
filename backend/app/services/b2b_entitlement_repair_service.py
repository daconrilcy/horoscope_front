from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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
    PeriodUnit,
    ResetMode,
    SourceOrigin,
)
from app.infra.db.models.user import UserModel
from app.services.b2b_audit_service import B2BAuditService

logger = logging.getLogger(__name__)

class RepairValidationError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

@dataclass
class RepairBlockerEntry:
    account_id: int
    company_name: str
    reason: str
    recommended_action: Literal["set_admin_user", "classify_zero_units", "schema_constraint_violation"]

@dataclass
class RepairRunReport:
    accounts_scanned: int = 0
    plans_created: int = 0
    bindings_created: int = 0
    quotas_created: int = 0
    skipped_already_canonical: int = 0
    remaining_blockers: list[RepairBlockerEntry] = field(default_factory=list)
    dry_run: bool = False

class B2BEntitlementRepairService:
    FEATURE_CODE = "b2b_api_access"

    @classmethod
    def run_auto_repair(cls, db: Session, *, dry_run: bool = False) -> RepairRunReport:
        report = RepairRunReport(dry_run=dry_run)
        
        all_accounts = db.scalars(
            select(EnterpriseAccountModel).where(EnterpriseAccountModel.status == "active")
        ).all()
        report.accounts_scanned = len(all_accounts)
        
        if not all_accounts:
            return report

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

        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == cls.FEATURE_CODE)
        )
        if not feature:
            raise RuntimeError(f"Feature {cls.FEATURE_CODE} not found in catalog")

        for account in all_accounts:
            # Use savepoint to isolate account repair
            with db.begin_nested():
                account_plan = account_plans.get(account.id)
                enterprise_plan = (
                    enterprise_plans.get(account_plan.plan_id) if account_plan is not None else None
                )
                
                # Recalculate state to decide repair
                audit_entry = B2BAuditService._audit_account(
                    db,
                    account,
                    acc_plan=account_plan,
                    ent_plan=enterprise_plan,
                    canonical_plan=canonical_plans.get(account_plan.plan_id) if account_plan else None,
                    binding=bindings.get(canonical_plans[account_plan.plan_id].id) if account_plan and account_plan.plan_id in canonical_plans else None,
                    quota_models=quotas.get(bindings[canonical_plans[account_plan.plan_id].id].id) if account_plan and account_plan.plan_id in canonical_plans and canonical_plans[account_plan.plan_id].id in bindings else None,
                )

                if audit_entry.resolution_source in {"canonical_quota", "canonical_unlimited", "canonical_disabled"}:
                    report.skipped_already_canonical += 1
                    continue

                if audit_entry.reason == "admin_user_id_missing":
                    report.remaining_blockers.append(RepairBlockerEntry(
                        account_id=account.id,
                        company_name=account.company_name,
                        reason=audit_entry.reason,
                        recommended_action="set_admin_user"
                    ))
                    continue

                if audit_entry.reason == "manual_review_required":
                    report.remaining_blockers.append(RepairBlockerEntry(
                        account_id=account.id,
                        company_name=account.company_name,
                        reason=audit_entry.reason,
                        recommended_action="classify_zero_units"
                    ))
                    continue

                # Auto-repairable cases
                current_canonical_plan = canonical_plans.get(account_plan.plan_id) if account_plan else None
                
                try:
                    # Case: no_canonical_plan
                    if audit_entry.reason == "no_canonical_plan" and enterprise_plan:
                        created, current_canonical_plan = cls._backfill_canonical_plan(
                            db, account, enterprise_plan, dry_run, report
                        )
                        if created:
                            report.plans_created += 1
                    
                    # Case: no_binding with included_monthly_units > 0
                    if current_canonical_plan and enterprise_plan and enterprise_plan.included_monthly_units > 0:
                        # Check if binding already exists
                        binding_exists = db.scalar(
                            select(PlanFeatureBindingModel).where(
                                PlanFeatureBindingModel.plan_id == current_canonical_plan.id,
                                PlanFeatureBindingModel.feature_id == feature.id
                            )
                        ) is not None
                        
                        if not binding_exists:
                            b_created, q_created = cls._backfill_binding_and_quota(
                                db, current_canonical_plan, enterprise_plan, feature, dry_run, report
                            )
                            if b_created:
                                report.bindings_created += 1
                            if q_created:
                                report.quotas_created += 1

                except IntegrityError as e:
                    # Rollback only this account's changes (automatic via with db.begin_nested())
                    logger.warning(f"IntegrityError during repair for account {account.id}: {e}")
                    report.remaining_blockers.append(RepairBlockerEntry(
                        account_id=account.id,
                        company_name=account.company_name,
                        reason="schema_constraint_violation",
                        recommended_action="schema_constraint_violation"
                    ))
                    continue

        if not dry_run:
            db.commit()

        return report

    @classmethod
    def _backfill_canonical_plan(
        cls, db: Session, account: EnterpriseAccountModel, enterprise_plan: EnterpriseBillingPlanModel, 
        dry_run: bool, report: RepairRunReport
    ) -> tuple[bool, PlanCatalogModel | None]:
        existing = db.scalar(
            select(PlanCatalogModel).where(
                PlanCatalogModel.source_type == SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
                PlanCatalogModel.source_id == enterprise_plan.id,
                PlanCatalogModel.audience == Audience.B2B,
            )
        )
        if existing:
            return False, existing

        if not dry_run:
            new_plan = PlanCatalogModel(
                plan_code=enterprise_plan.code,
                plan_name=enterprise_plan.display_name,
                audience=Audience.B2B,
                source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
                source_id=enterprise_plan.id,
                is_active=enterprise_plan.is_active,
            )
            db.add(new_plan)
            db.flush()
            return True, new_plan
        # Dry run: return a dummy object to allow chaining
        dummy_plan = PlanCatalogModel(id=-1, plan_code=enterprise_plan.code)
        return True, dummy_plan

    @classmethod
    def _backfill_binding_and_quota(
        cls, db: Session, canonical_plan: PlanCatalogModel, enterprise_plan: EnterpriseBillingPlanModel,
        feature: FeatureCatalogModel, dry_run: bool, report: RepairRunReport
    ) -> tuple[bool, bool]:
        if not dry_run:
            binding = PlanFeatureBindingModel(
                plan_id=canonical_plan.id,
                feature_id=feature.id,
                access_mode=AccessMode.QUOTA,
                is_enabled=True,
                source_origin=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
            )
            db.add(binding)
            db.flush()
            
            quota = PlanFeatureQuotaModel(
                plan_feature_binding_id=binding.id,
                quota_key="calls",
                quota_limit=enterprise_plan.included_monthly_units,
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                source_origin=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
            )
            db.add(quota)
            db.flush()
            return True, True
        return True, True

    @classmethod
    def set_admin_user(cls, db: Session, *, account_id: int, user_id: int) -> dict:
        account = db.get(EnterpriseAccountModel, account_id)
        if not account or account.status != "active":
            raise RepairValidationError(code="account_not_found_or_inactive", message="Account not found or inactive")
        
        if account.admin_user_id is not None:
            raise RepairValidationError(code="admin_user_already_set", message="Admin user already set for this account")
        
        user = db.get(UserModel, user_id)
        if not user:
            raise RepairValidationError(code="user_not_found", message="User not found")
        
        # Check if user is already admin of another account
        other_account = db.scalar(
            select(EnterpriseAccountModel).where(EnterpriseAccountModel.admin_user_id == user_id)
        )
        if other_account:
            raise RepairValidationError(
                code="user_already_admin_of_another_account", 
                message=f"User is already admin of account {other_account.id}"
            )
        
        account.admin_user_id = user_id
        db.commit()
        return {"account_id": account_id, "user_id": user_id, "status": "ok"}

    @classmethod
    def classify_zero_units(cls, db: Session, *, canonical_plan_id: int, access_mode: str, quota_limit: int | None) -> dict:
        # AC 14: Validation rules in order
        plan = db.get(PlanCatalogModel, canonical_plan_id)
        if not plan or plan.audience != Audience.B2B or not plan.is_active:
            raise RepairValidationError(code="canonical_plan_not_found", message="Canonical plan not found or inactive")
        
        # Resolve enterprise plan to check zero units
        enterprise_plan = None
        if plan.source_type == SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value:
            enterprise_plan = db.get(EnterpriseBillingPlanModel, plan.source_id)
        
        if not enterprise_plan or enterprise_plan.included_monthly_units != 0:
            raise RepairValidationError(
                code="canonical_plan_not_zero_units_eligible", 
                message="Plan not eligible for zero units classification"
            )
        
        if access_mode == "quota" and quota_limit is None:
            raise RepairValidationError(
                code="quota_limit_required_for_quota_mode",
                message="quota_limit is required when access_mode is 'quota'"
            )
        
        if access_mode != "quota" and quota_limit is not None:
            raise RepairValidationError(
                code="quota_limit_forbidden_for_non_quota_mode",
                message=f"quota_limit must be null for access_mode '{access_mode}'"
            )

        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == cls.FEATURE_CODE)
        )
        if not feature:
            raise RuntimeError(f"Feature {cls.FEATURE_CODE} not found")
        
        binding = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == canonical_plan_id,
                PlanFeatureBindingModel.feature_id == feature.id
            )
        )
        
        access_mode_enum = AccessMode(access_mode)
        
        # Check if already configured identical
        if binding and binding.access_mode == access_mode_enum:
            if access_mode_enum != AccessMode.QUOTA:
                return {"canonical_plan_id": canonical_plan_id, "access_mode": access_mode, "quota_limit": None, "status": "already_configured"}
            
            quota = db.scalar(
                select(PlanFeatureQuotaModel).where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
            )
            if quota and quota.quota_limit == quota_limit:
                return {"canonical_plan_id": canonical_plan_id, "access_mode": access_mode, "quota_limit": quota_limit, "status": "already_configured"}

        status = "updated" if binding else "created"
        
        if not binding:
            binding = PlanFeatureBindingModel(
                plan_id=canonical_plan_id,
                feature_id=feature.id,
                access_mode=access_mode_enum,
                is_enabled=(access_mode_enum != AccessMode.DISABLED),
                source_origin=SourceOrigin.MANUAL.value
            )
            db.add(binding)
            db.flush()
        else:
            # Reclassify
            # AC 18: Supprimer les quotas existants si on passe en non-QUOTA
            if binding.access_mode == AccessMode.QUOTA and access_mode_enum != AccessMode.QUOTA:
                for q in db.scalars(select(PlanFeatureQuotaModel).where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)).all():
                    db.delete(q)
            
            binding.access_mode = access_mode_enum
            binding.is_enabled = (access_mode_enum != AccessMode.DISABLED)
            binding.source_origin = SourceOrigin.MANUAL.value
            db.add(binding)
            db.flush()

        if access_mode_enum == AccessMode.QUOTA:
            quota = db.scalar(
                select(PlanFeatureQuotaModel).where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
            )
            if quota:
                quota.quota_limit = quota_limit
                quota.source_origin = SourceOrigin.MANUAL.value
            else:
                quota = PlanFeatureQuotaModel(
                    plan_feature_binding_id=binding.id,
                    quota_key="calls",
                    quota_limit=quota_limit,
                    period_unit=PeriodUnit.MONTH,
                    period_value=1,
                    reset_mode=ResetMode.CALENDAR,
                    source_origin=SourceOrigin.MANUAL.value
                )
            db.add(quota)

        db.commit()
        return {"canonical_plan_id": canonical_plan_id, "access_mode": access_mode, "quota_limit": quota_limit, "status": status}
