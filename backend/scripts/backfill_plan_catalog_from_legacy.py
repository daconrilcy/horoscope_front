"""Backfill script to populate canonical plan catalog from legacy billing tables.

This script is idempotent and maps:
- billing_plans -> plan_catalog (B2C) + astrologer_chat quotas
- enterprise_billing_plans -> plan_catalog (B2B) + b2b_api_access quotas
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.models.enterprise_billing import EnterpriseBillingPlanModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
    PeriodUnit,
    SourceOrigin,
)
from app.infra.db.session import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

B2B_FEATURE_CODE = "b2b_api_access"
B2C_CHAT_FEATURE_CODE = "astrologer_chat"

class BackfillReport:
    def __init__(self):
        self.plans_created = 0
        self.plans_updated = 0
        self.plans_skipped = 0
        self.bindings_created = 0
        self.bindings_updated = 0
        self.bindings_skipped = 0
        self.quotas_created = 0
        self.quotas_updated = 0
        self.quotas_skipped = 0
        self.processed_b2c = 0
        self.processed_b2b = 0

def ensure_b2b_feature(db: Session) -> FeatureCatalogModel:
    """Ensure the B2B API access feature exists in the catalog."""
    feature = db.execute(
        select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == B2B_FEATURE_CODE)
    ).scalar_one_or_none()
    
    if feature is None:
        logger.info("Creating feature '%s'...", B2B_FEATURE_CODE)
        feature = FeatureCatalogModel(
            feature_code=B2B_FEATURE_CODE,
            feature_name="B2B API Access",
            description="Accès volumétrique à l'API astrologique pour les comptes entreprise",
            is_metered=True,
            is_active=True,
        )
        db.add(feature)
        db.flush()
    return feature

def ensure_b2c_chat_feature(db: Session) -> FeatureCatalogModel:
    """Ensure the B2C chat feature exists in the catalog."""
    feature = db.execute(
        select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == B2C_CHAT_FEATURE_CODE)
    ).scalar_one_or_none()
    
    if feature is None:
        logger.info("Creating feature '%s'...", B2C_CHAT_FEATURE_CODE)
        feature = FeatureCatalogModel(
            feature_code=B2C_CHAT_FEATURE_CODE,
            feature_name="Astrologer Chat",
            is_metered=True,
            is_active=True,
        )
        db.add(feature)
        db.flush()
    return feature

def _upsert_plan(
    db: Session, 
    code: str, 
    name: str, 
    audience: Audience, 
    source_type: str, 
    source_id: int,
    is_active: bool,
    report: BackfillReport
) -> PlanCatalogModel:
    """Upsert a plan in the catalog, respecting the collision policy."""
    plan = db.execute(
        select(PlanCatalogModel).where(PlanCatalogModel.plan_code == code)
    ).scalar_one_or_none()
    
    if plan is None:
        logger.info("Creating plan '%s' (audience=%s, source=%s)...", code, audience.value, source_type)
        plan = PlanCatalogModel(
            plan_code=code,
            plan_name=name,
            audience=audience,
            source_type=source_type,
            source_id=source_id,
            is_active=is_active,
        )
        db.add(plan)
        report.plans_created += 1
    else:
        # Collision policy: if manual or already migrated from same source, update.
        if plan.source_type in {"manual", source_type}:
            logger.info("Updating plan '%s' (source was %s)...", code, plan.source_type)
            plan.plan_name = name
            plan.audience = audience
            plan.source_type = source_type
            plan.source_id = source_id
            plan.is_active = is_active
            report.plans_updated += 1
        else:
            logger.warning(
                "Collision on plan '%s': existing source_type='%s' is not manual nor '%s'. Skipping update.",
                code, plan.source_type, source_type
            )
            report.plans_skipped += 1
    db.flush()
    return plan

def _upsert_binding(
    db: Session,
    plan_id: int,
    feature_id: int,
    access_mode: AccessMode,
    source_origin: str,
    report: BackfillReport
) -> PlanFeatureBindingModel:
    """Upsert a feature binding for a plan, respecting the collision policy."""
    binding = db.execute(
        select(PlanFeatureBindingModel).where(
            PlanFeatureBindingModel.plan_id == plan_id,
            PlanFeatureBindingModel.feature_id == feature_id,
        )
    ).scalar_one_or_none()
    
    if binding is None:
        binding = PlanFeatureBindingModel(
            plan_id=plan_id,
            feature_id=feature_id,
            is_enabled=(access_mode != AccessMode.DISABLED),
            access_mode=access_mode,
            source_origin=source_origin,
        )
        db.add(binding)
        report.bindings_created += 1
    else:
        if binding.source_origin in {"manual", source_origin}:
            binding.access_mode = access_mode
            binding.is_enabled = (access_mode != AccessMode.DISABLED)
            binding.source_origin = source_origin
            report.bindings_updated += 1
        else:
            logger.warning(
                "Collision on binding plan_id=%s feature_id=%s: existing source_origin='%s'. Skipping.",
                plan_id, feature_id, binding.source_origin
            )
            report.bindings_skipped += 1
    db.flush()
    return binding

def _upsert_quota(
    db: Session,
    binding_id: int,
    quota_key: str,
    limit: int,
    unit: PeriodUnit,
    value: int,
    reset: ResetMode,
    source_origin: str,
    report: BackfillReport
) -> None:
    """Upsert a quota for a binding, respecting the collision policy."""
    quota = db.execute(
        select(PlanFeatureQuotaModel).where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding_id,
            PlanFeatureQuotaModel.quota_key == quota_key,
            PlanFeatureQuotaModel.period_unit == unit,
            PlanFeatureQuotaModel.period_value == value,
            PlanFeatureQuotaModel.reset_mode == reset,
        )
    ).scalar_one_or_none()
    
    if quota is None:
        quota = PlanFeatureQuotaModel(
            plan_feature_binding_id=binding_id,
            quota_key=quota_key,
            quota_limit=limit,
            period_unit=unit,
            period_value=value,
            reset_mode=reset,
            source_origin=source_origin,
        )
        db.add(quota)
        report.quotas_created += 1
    else:
        if quota.source_origin in {"manual", source_origin}:
            quota.quota_limit = limit
            quota.source_origin = source_origin
            report.quotas_updated += 1
        else:
            logger.warning("Collision on quota key='%s' for binding_id=%s. Skipping.", quota_key, binding_id)
            report.quotas_skipped += 1
    db.flush()

def backfill_b2c_plans(db: Session, report: BackfillReport | None = None) -> None:
    if report is None:
        report = BackfillReport()
    chat_feature = ensure_b2c_chat_feature(db)
    
    legacy_plans = db.execute(select(BillingPlanModel)).scalars().all()
    for legacy in legacy_plans:
        report.processed_b2c += 1
        plan = _upsert_plan(
            db,
            code=legacy.code,
            name=legacy.display_name,
            audience=Audience.B2C,
            source_type="migrated_from_billing_plan",
            source_id=legacy.id,
            is_active=legacy.is_active,
            report=report
        )
        
        # Mapping daily_message_limit
        access_mode = AccessMode.QUOTA if legacy.daily_message_limit > 0 else AccessMode.DISABLED
        binding = _upsert_binding(
            db,
            plan_id=plan.id,
            feature_id=chat_feature.id,
            access_mode=access_mode,
            source_origin="migrated_from_billing_plan",
            report=report
        )
        
        if access_mode == AccessMode.QUOTA:
            _upsert_quota(
                db,
                binding_id=binding.id,
                quota_key="messages",
                limit=legacy.daily_message_limit,
                unit=PeriodUnit.DAY,
                value=1,
                reset=ResetMode.CALENDAR,
                source_origin="migrated_from_billing_plan",
                report=report
            )
        else:
            # If disabled, ensure no migrated quota exists
            existing_quotas = db.execute(
                select(PlanFeatureQuotaModel).where(
                    PlanFeatureQuotaModel.plan_feature_binding_id == binding.id,
                    PlanFeatureQuotaModel.source_origin == "migrated_from_billing_plan"
                )
            ).scalars().all()
            for q in existing_quotas:
                db.delete(q)

def backfill_b2b_plans(db: Session, report: BackfillReport | None = None) -> None:
    if report is None:
        report = BackfillReport()
    b2b_feature = ensure_b2b_feature(db)
    
    legacy_plans = db.execute(select(EnterpriseBillingPlanModel)).scalars().all()
    for legacy in legacy_plans:
        report.processed_b2b += 1
        plan = _upsert_plan(
            db,
            code=legacy.code,
            name=legacy.display_name,
            audience=Audience.B2B,
            source_type="migrated_from_enterprise_plan",
            source_id=legacy.id,
            is_active=legacy.is_active,
            report=report
        )
        
        # Mapping included_monthly_units
        if legacy.included_monthly_units > 0:
            binding = _upsert_binding(
                db,
                plan_id=plan.id,
                feature_id=b2b_feature.id,
                access_mode=AccessMode.QUOTA,
                source_origin="migrated_from_enterprise_plan",
                report=report
            )
            _upsert_quota(
                db,
                binding_id=binding.id,
                quota_key="calls",
                limit=legacy.included_monthly_units,
                unit=PeriodUnit.MONTH,
                value=1,
                reset=ResetMode.CALENDAR,
                source_origin="migrated_from_enterprise_plan",
                report=report
            )
        elif legacy.included_monthly_units == 0:
            logger.warning(
                "enterprise_plan '%s' (id=%s) -> included_monthly_units=0: manual-review-required as per spec.",
                legacy.code, legacy.id
            )
            # We don't create/update binding automatically for 0 units in B2B as per spec

def run_backfill() -> None:
    logger.info("=== BACKFILL PLAN CATALOG FROM LEGACY START ===")
    report = BackfillReport()
    with SessionLocal() as db:
        try:
            backfill_b2c_plans(db, report)
            backfill_b2b_plans(db, report)
            db.commit()
            
            logger.info("B2C plans processed: %s", report.processed_b2c)
            logger.info("B2B plans processed: %s", report.processed_b2b)
            logger.info("Plans: %s created, %s updated, %s skipped", report.plans_created, report.plans_updated, report.plans_skipped)
            logger.info("Bindings: %s created, %s updated, %s skipped", report.bindings_created, report.bindings_updated, report.bindings_skipped)
            logger.info("Quotas: %s created, %s updated, %s skipped", report.quotas_created, report.quotas_updated, report.quotas_skipped)
            logger.info("Ignored legacy columns: monthly_price_cents, currency, overage_unit_price_cents, monthly_fixed_cents")
            logger.info("Non-migrated: settings.b2b_daily_usage_limit, settings.b2b_monthly_usage_limit")
            logger.info("=== BACKFILL COMPLETED ===")
        except Exception as e:
            db.rollback()
            logger.error("Backfill failed: %s", e)
            raise

if __name__ == "__main__":
    run_backfill()
