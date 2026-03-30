import logging

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.models.enterprise_billing import EnterpriseBillingPlanModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
    SourceOrigin,
)
from scripts.backfill_plan_catalog_from_legacy import (
    BackfillReport,
    backfill_b2b_plans,
    backfill_b2c_plans,
    ensure_b2b_feature,
    ensure_b2c_chat_feature,
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
            FeatureCatalogModel.feature_code == "astrologer_chat",
        )
    ).scalar_one_or_none()
    assert binding is not None
    assert binding.access_mode == AccessMode.QUOTA
    assert binding.source_origin == "migrated_from_billing_plan"

    quota = db_session.execute(
        select(PlanFeatureQuotaModel).where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
        )
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
            FeatureCatalogModel.feature_code == "astrologer_chat",
        )
    ).scalar_one_or_none()
    assert binding.access_mode == AccessMode.DISABLED

    quota_count = (
        db_session.execute(
            select(PlanFeatureQuotaModel).where(
                PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
            )
        )
        .scalars()
        .all()
    )
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
            FeatureCatalogModel.feature_code == "b2b_api_access",
        )
    ).scalar_one_or_none()
    assert binding.access_mode == AccessMode.QUOTA

    quota = db_session.execute(
        select(PlanFeatureQuotaModel).where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
        )
    ).scalar_one_or_none()
    assert quota.quota_limit == 1000
    assert quota.period_unit == PeriodUnit.MONTH


def test_backfill_idempotence(db_session: Session):
    db_session.add(
        BillingPlanModel(
            code="idemp",
            display_name="Idemp",
            monthly_price_cents=10,
            currency="EUR",
            daily_message_limit=10,
            is_active=True,
        )
    )
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
    assert (
        len(db_session.execute(select(PlanFeatureBindingModel)).scalars().all()) == count_bindings
    )
    assert len(db_session.execute(select(PlanFeatureQuotaModel)).scalars().all()) == count_quotas


def test_backfill_updates_manual_plans_and_bindings(db_session: Session):
    # 1. Setup manual data in canonique
    manual_plan = PlanCatalogModel(
        plan_code="basic", plan_name="Basic Manual", audience=Audience.B2C, source_type="manual"
    )
    db_session.add(manual_plan)
    db_session.flush()

    chat_feat = FeatureCatalogModel(
        feature_code="astrologer_chat", feature_name="Chat", is_metered=True
    )
    db_session.add(chat_feat)
    db_session.flush()

    manual_binding = PlanFeatureBindingModel(
        plan_id=manual_plan.id,
        feature_id=chat_feat.id,
        access_mode=AccessMode.UNLIMITED,  # Manual says unlimited
        source_origin="manual",
    )
    db_session.add(manual_binding)
    db_session.flush()

    # 2. Setup matching legacy plan with DIFFERENT values
    legacy_plan = BillingPlanModel(
        code="basic",
        display_name="Basic Legacy",
        monthly_price_cents=500,
        currency="EUR",
        daily_message_limit=10,  # Legacy says 10 (Quota)
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
    assert (
        manual_binding.access_mode == AccessMode.QUOTA
    )  # Unlimited was overwritten by legacy Quota
    assert manual_binding.source_origin == "migrated_from_billing_plan"

    quota = db_session.execute(
        select(PlanFeatureQuotaModel).where(
            PlanFeatureQuotaModel.plan_feature_binding_id == manual_binding.id
        )
    ).scalar_one_or_none()
    assert quota is not None
    assert quota.quota_limit == 10
    assert quota.source_origin == "migrated_from_billing_plan"


def test_backfill_b2b_zero_units_logs_warning_and_creates_no_binding(
    db_session: Session, caplog: pytest.LogCaptureFixture
):
    """included_monthly_units=0 doit logger un warning et ne créer aucun binding."""
    legacy_plan = EnterpriseBillingPlanModel(
        code="ent-zero",
        display_name="Enterprise Zero",
        monthly_fixed_cents=1000,
        included_monthly_units=0,
        overage_unit_price_cents=0,
        currency="EUR",
        is_active=True,
    )
    db_session.add(legacy_plan)
    db_session.commit()

    with caplog.at_level(logging.WARNING, logger="app.services.backfill_plan_catalog_service"):
        backfill_b2b_plans(db_session)

    # Le plan doit exister dans plan_catalog
    plan = db_session.execute(
        select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "ent-zero")
    ).scalar_one_or_none()
    assert plan is not None
    assert plan.audience == Audience.B2B

    # Aucun binding ne doit avoir été créé
    bindings = (
        db_session.execute(
            select(PlanFeatureBindingModel).where(PlanFeatureBindingModel.plan_id == plan.id)
        )
        .scalars()
        .all()
    )
    assert len(bindings) == 0

    # Un warning doit avoir été émis
    assert any("manual-review-required" in r.message for r in caplog.records)


def test_backfill_collision_on_binding_logs_warning_without_overwriting(
    db_session: Session, caplog: pytest.LogCaptureFixture
):
    """Un binding avec une origine non overridable ne doit pas être écrasé."""
    non_overridable_origin = SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value

    # Plan canonique existant
    plan = PlanCatalogModel(
        plan_code="basic-conflict",
        plan_name="Basic Conflict",
        audience=Audience.B2C,
        source_type="manual",
    )
    db_session.add(plan)
    db_session.flush()

    chat_feat = FeatureCatalogModel(
        feature_code="astrologer_chat", feature_name="Chat", is_metered=True
    )
    db_session.add(chat_feat)
    db_session.flush()

    # Binding avec une origine tierce (non manual, non migrated_from_billing_plan)
    existing_binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=chat_feat.id,
        access_mode=AccessMode.UNLIMITED,
        source_origin=non_overridable_origin,
    )
    db_session.add(existing_binding)
    db_session.commit()

    # Plan legacy correspondant
    legacy_plan = BillingPlanModel(
        code="basic-conflict",
        display_name="Basic Conflict Legacy",
        monthly_price_cents=500,
        currency="EUR",
        daily_message_limit=5,
        is_active=True,
    )
    db_session.add(legacy_plan)
    db_session.commit()

    with caplog.at_level(logging.WARNING, logger="app.services.backfill_plan_catalog_service"):
        backfill_b2c_plans(db_session)

    # Le binding doit être inchangé
    db_session.refresh(existing_binding)
    assert existing_binding.access_mode == AccessMode.UNLIMITED
    assert existing_binding.source_origin == non_overridable_origin

    # Aucun quota ne doit avoir été créé
    quotas = (
        db_session.execute(
            select(PlanFeatureQuotaModel).where(
                PlanFeatureQuotaModel.plan_feature_binding_id == existing_binding.id
            )
        )
        .scalars()
        .all()
    )
    assert len(quotas) == 0

    # Un warning doit avoir été émis
    assert any("Collision on binding" in r.message for r in caplog.records)


def test_backfill_non_mapped_columns_absent_from_canonical(db_session: Session):
    """Les colonnes pricing (monthly_price_cents, currency, etc.) ne doivent pas
    apparaître dans les tables canoniques."""
    legacy_plan = BillingPlanModel(
        code="priced-plan",
        display_name="Priced Plan",
        monthly_price_cents=9900,
        currency="EUR",
        daily_message_limit=20,
        is_active=True,
    )
    db_session.add(legacy_plan)
    db_session.commit()

    backfill_b2c_plans(db_session)

    # Exactement 1 plan créé, sans champ pricing
    plans = db_session.execute(select(PlanCatalogModel)).scalars().all()
    assert len(plans) == 1
    assert not hasattr(plans[0], "monthly_price_cents")
    assert not hasattr(plans[0], "currency")

    # Exactement 1 binding (astrologer_chat) et 1 quota (messages/day)
    bindings = db_session.execute(select(PlanFeatureBindingModel)).scalars().all()
    assert len(bindings) == 1

    quotas = db_session.execute(select(PlanFeatureQuotaModel)).scalars().all()
    assert len(quotas) == 1
    assert quotas[0].quota_key == "messages"


def test_backfill_unmatched_manual_plan_kept_and_logged(
    db_session: Session, caplog: pytest.LogCaptureFixture
):
    """Un plan canonique B2C avec source_type='manual' sans match dans billing_plans
    doit être conservé en l'état et journalisé."""
    orphan = PlanCatalogModel(
        plan_code="orphan-manual",
        plan_name="Orphan Manual",
        audience=Audience.B2C,
        source_type="manual",
    )
    db_session.add(orphan)
    db_session.commit()

    report = BackfillReport()
    with caplog.at_level(logging.INFO):
        backfill_b2c_plans(db_session, report)

    # Le plan doit toujours exister, inchangé
    refreshed = db_session.execute(
        select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "orphan-manual")
    ).scalar_one_or_none()
    assert refreshed is not None
    assert refreshed.source_type == "manual"

    # Un message doit tracer l'absence de correspondance
    assert any("orphan-manual" in r.message for r in caplog.records)
    assert len(report.unmatched_manual_plans) == 1


def test_backfill_b2b_stale_migrated_binding_on_zero_units_raises_anomaly(
    db_session: Session, caplog: pytest.LogCaptureFixture
):
    """Une anomalie est tracée si un binding migré subsiste avec zero unité mensuelle."""
    b2b_feature = ensure_b2b_feature(db_session)
    db_session.flush()

    # Plan canonique B2B avec binding migré existant
    plan = PlanCatalogModel(
        plan_code="ent-stale",
        plan_name="Enterprise Stale",
        audience=Audience.B2B,
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        source_id=1,
        is_active=True,
    )
    db_session.add(plan)
    db_session.flush()

    stale_binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=b2b_feature.id,
        access_mode=AccessMode.QUOTA,
        source_origin=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
    )
    db_session.add(stale_binding)

    # Plan legacy correspondant avec 0 unités
    legacy_plan = EnterpriseBillingPlanModel(
        code="ent-stale",
        display_name="Enterprise Stale",
        monthly_fixed_cents=0,
        included_monthly_units=0,
        overage_unit_price_cents=0,
        currency="EUR",
        is_active=True,
    )
    db_session.add(legacy_plan)
    db_session.commit()

    report = BackfillReport()
    with caplog.at_level(logging.WARNING, logger="app.services.backfill_plan_catalog_service"):
        backfill_b2b_plans(db_session, report)

    # Le binding ne doit pas avoir été modifié
    db_session.refresh(stale_binding)
    assert stale_binding.access_mode == AccessMode.QUOTA
    assert stale_binding.source_origin == SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value

    # Une anomalie doit être enregistrée
    assert len(report.anomalies) >= 1
    assert any("ent-stale" in a for a in report.anomalies)
    assert any("manual-review-required" in r.message for r in caplog.records)


def test_backfill_idempotence_tracks_unchanged_counters(db_session: Session):
    """Lors d'une seconde exécution sans changement, les compteurs unchanged
    doivent être incrémentés (pas created/updated)."""
    db_session.add(
        BillingPlanModel(
            code="stable",
            display_name="Stable",
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=5,
            is_active=True,
        )
    )
    db_session.commit()

    # Première exécution
    backfill_b2c_plans(db_session)
    db_session.commit()

    # Deuxième exécution
    report2 = BackfillReport()
    backfill_b2c_plans(db_session, report2)

    assert report2.plans_created == 0
    assert report2.plans_unchanged == 1
    assert report2.bindings_created == 0
    assert report2.bindings_unchanged == 1
    assert report2.quotas_created == 0
    assert report2.quotas_unchanged == 1


def test_ensure_b2c_chat_feature_reuses_seeded_feature_without_duplicate(db_session: Session):
    seeded_feature = FeatureCatalogModel(
        feature_code="astrologer_chat",
        feature_name="Astrologer Chat",
        description="Seeded canonical feature",
        is_metered=True,
        is_active=True,
    )
    db_session.add(seeded_feature)
    db_session.commit()

    feature = ensure_b2c_chat_feature(db_session)
    db_session.commit()

    assert feature.id == seeded_feature.id
    features = db_session.execute(
        select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "astrologer_chat")
    ).scalars().all()
    assert len(features) == 1
