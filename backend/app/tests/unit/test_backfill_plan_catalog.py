import pytest
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
    SourceOrigin,
    PeriodUnit,
    ResetMode,
)

from scripts.backfill_plan_catalog_from_legacy import (
    backfill_b2c_plans,
    backfill_b2b_plans,
    ensure_b2b_feature,
    BackfillReport,
)

def test_backfill_b2c_creates_plans_and_quotas(db_session: Session):
    # Setup legacy data
    legacy_plan = BillingPlanModel(
        code="basic-legacy",
        display_name="Basic Legacy",
        monthly_price_cents=500,
        currency="EUR",
        daily_message_limit=10,
        is_active=True,
    )
    db_session.add(legacy_plan)
    db_session.commit()

    # Run backfill
    report = BackfillReport()
    backfill_b2c_plans(db_session, report)
    db_session.commit()

    assert report.plans_created == 1
    assert report.bindings_created == 1
    assert report.quotas_created == 1

    # Verify plan_catalog
    plan = db_session.execute(
        select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "basic-legacy")
    ).scalar_one_or_none()
    assert plan is not None
    assert plan.plan_name == "Basic Legacy"
    assert plan.audience == Audience.B2C
    assert plan.source_type == "migrated_from_billing_plan"
    assert plan.source_id == legacy_plan.id

    # Verify binding and quota
    binding = db_session.execute(
        select(PlanFeatureBindingModel)
        .join(FeatureCatalogModel)
        .where(
            PlanFeatureBindingModel.plan_id == plan.id,
            FeatureCatalogModel.feature_code == "astrologer_chat"
        )
    ).scalar_one_or_none()
    assert binding is not None
    assert binding.access_mode == AccessMode.QUOTA
    assert binding.source_origin == "migrated_from_billing_plan"

    quota = db_session.execute(
        select(PlanFeatureQuotaModel).where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
    ).scalar_one_or_none()
    assert quota is not None
    assert quota.quota_limit == 10
    assert quota.period_unit == PeriodUnit.DAY
    assert quota.period_value == 1
    assert quota.reset_mode == ResetMode.CALENDAR

def test_backfill_b2c_disabled_when_limit_is_zero(db_session: Session):
    legacy_plan = BillingPlanModel(
        code="free-legacy",
        display_name="Free Legacy",
        monthly_price_cents=0,
        currency="EUR",
        daily_message_limit=0,
        is_active=True,
    )
    db_session.add(legacy_plan)
    db_session.commit()

    backfill_b2c_plans(db_session)

    plan = db_session.execute(
        select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "free-legacy")
    ).scalar_one_or_none()
    
    binding = db_session.execute(
        select(PlanFeatureBindingModel)
        .join(FeatureCatalogModel)
        .where(
            PlanFeatureBindingModel.plan_id == plan.id,
            FeatureCatalogModel.feature_code == "astrologer_chat"
        )
    ).scalar_one_or_none()
    assert binding.access_mode == AccessMode.DISABLED
    
    quota_count = db_session.execute(
        select(PlanFeatureQuotaModel).where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
    ).scalars().all()
    assert len(quota_count) == 0

def test_backfill_b2b_creates_plans_and_quotas(db_session: Session):
    ensure_b2b_feature(db_session)
    legacy_plan = EnterpriseBillingPlanModel(
        code="ent-standard",
        display_name="Enterprise Standard",
        monthly_fixed_cents=5000,
        included_monthly_units=1000,
        overage_unit_price_cents=2,
        currency="EUR",
        is_active=True,
    )
    db_session.add(legacy_plan)
    db_session.commit()

    backfill_b2b_plans(db_session)

    plan = db_session.execute(
        select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "ent-standard")
    ).scalar_one_or_none()
    assert plan.audience == Audience.B2B
    assert plan.source_type == "migrated_from_enterprise_plan"

    binding = db_session.execute(
        select(PlanFeatureBindingModel)
        .join(FeatureCatalogModel)
        .where(
            PlanFeatureBindingModel.plan_id == plan.id,
            FeatureCatalogModel.feature_code == "b2b_api_access"
        )
    ).scalar_one_or_none()
    assert binding.access_mode == AccessMode.QUOTA

    quota = db_session.execute(
        select(PlanFeatureQuotaModel).where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
    ).scalar_one_or_none()
    assert quota.quota_limit == 1000
    assert quota.period_unit == PeriodUnit.MONTH

def test_backfill_idempotence(db_session: Session):
    db_session.add(BillingPlanModel(
        code="idemp", display_name="Idemp", monthly_price_cents=10, 
        currency="EUR", daily_message_limit=10, is_active=True
    ))
    db_session.commit()

    # First run
    backfill_b2c_plans(db_session)
    db_session.commit()
    count_plans = len(db_session.execute(select(PlanCatalogModel)).scalars().all())
    count_bindings = len(db_session.execute(select(PlanFeatureBindingModel)).scalars().all())
    count_quotas = len(db_session.execute(select(PlanFeatureQuotaModel)).scalars().all())

    # Second run
    backfill_b2c_plans(db_session)
    db_session.commit()
    
    assert len(db_session.execute(select(PlanCatalogModel)).scalars().all()) == count_plans
    assert len(db_session.execute(select(PlanFeatureBindingModel)).scalars().all()) == count_bindings
    assert len(db_session.execute(select(PlanFeatureQuotaModel)).scalars().all()) == count_quotas

def test_backfill_updates_manual_plans_and_bindings(db_session: Session):
    # 1. Setup manual data in canonique
    manual_plan = PlanCatalogModel(
        plan_code="basic",
        plan_name="Basic Manual",
        audience=Audience.B2C,
        source_type="manual"
    )
    db_session.add(manual_plan)
    db_session.flush()
    
    chat_feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat", is_metered=True)
    db_session.add(chat_feat)
    db_session.flush()
    
    manual_binding = PlanFeatureBindingModel(
        plan_id=manual_plan.id,
        feature_id=chat_feat.id,
        access_mode=AccessMode.UNLIMITED, # Manual says unlimited
        source_origin="manual"
    )
    db_session.add(manual_binding)
    db_session.flush()
    
    # 2. Setup matching legacy plan with DIFFERENT values
    legacy_plan = BillingPlanModel(
        code="basic",
        display_name="Basic Legacy",
        monthly_price_cents=500,
        currency="EUR",
        daily_message_limit=10, # Legacy says 10 (Quota)
        is_active=True,
    )
    db_session.add(legacy_plan)
    db_session.commit()

    # 3. Run backfill
    backfill_b2c_plans(db_session)
    db_session.commit()

    # 4. Verify updates
    db_session.refresh(manual_plan)
    assert manual_plan.source_type == "migrated_from_billing_plan"
    assert manual_plan.source_id == legacy_plan.id
    assert manual_plan.plan_name == "Basic Legacy"
    
    db_session.refresh(manual_binding)
    assert manual_binding.access_mode == AccessMode.QUOTA # Unlimited was overwritten by legacy Quota
    assert manual_binding.source_origin == "migrated_from_billing_plan"
    
    quota = db_session.execute(
        select(PlanFeatureQuotaModel).where(PlanFeatureQuotaModel.plan_feature_binding_id == manual_binding.id)
    ).scalar_one_or_none()
    assert quota is not None
    assert quota.quota_limit == 10
    assert quota.source_origin == "migrated_from_billing_plan"
