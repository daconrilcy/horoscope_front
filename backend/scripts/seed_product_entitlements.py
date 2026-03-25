"""Seed script for product entitlements.

This script initializes the canonical product entitlements catalog:
- Plans: free, trial, basic, premium
- Features: natal_chart_short, natal_chart_long, astrologer_chat, thematic_consultation
- Bindings and Quotas for each plan.

Run:
    python backend/scripts/seed_product_entitlements.py
"""

import logging
from sqlalchemy import select
from app.infra.db.models.product_entitlements import (
    PlanCatalogModel,
    FeatureCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    Audience,
    AccessMode,
    PeriodUnit,
    ResetMode,
    SourceOrigin,
)
from app.infra.db.session import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def seed():
    db = SessionLocal()
    try:
        # 1. Seed Plans
        plans_data = [
            {"plan_code": "free", "plan_name": "Free Plan", "audience": Audience.B2C},
            {"plan_code": "trial", "plan_name": "Trial Plan", "audience": Audience.B2C},
            {"plan_code": "basic", "plan_name": "Basic Plan", "audience": Audience.B2C},
            {"plan_code": "premium", "plan_name": "Premium Plan", "audience": Audience.B2C},
        ]

        plans = {}
        for p_data in plans_data:
            plan = db.execute(
                select(PlanCatalogModel).where(PlanCatalogModel.plan_code == p_data["plan_code"])
            ).scalar_one_or_none()
            if not plan:
                logger.info(f"Creating plan '{p_data['plan_code']}'...")
                plan = PlanCatalogModel(**p_data)
                db.add(plan)
                db.flush()
            else:
                logger.info(f"Plan '{p_data['plan_code']}' already exists.")
            plans[p_data["plan_code"]] = plan

        # 2. Seed Features
        features_data = [
            {"feature_code": "natal_chart_short", "feature_name": "Natal Chart Short", "is_metered": False},
            {"feature_code": "natal_chart_long", "feature_name": "Natal Chart Long", "is_metered": True},
            {"feature_code": "astrologer_chat", "feature_name": "Astrologer Chat", "is_metered": True},
            {"feature_code": "thematic_consultation", "feature_name": "Thematic Consultation", "is_metered": True},
        ]

        features = {}
        for f_data in features_data:
            feature = db.execute(
                select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == f_data["feature_code"])
            ).scalar_one_or_none()
            if not feature:
                logger.info(f"Creating feature '{f_data['feature_code']}'...")
                feature = FeatureCatalogModel(**f_data)
                db.add(feature)
                db.flush()
            else:
                logger.info(f"Feature '{f_data['feature_code']}' already exists.")
            features[f_data["feature_code"]] = feature

        # 3. Seed Bindings and Quotas
        
        # Helper to upsert binding and quotas
        def upsert_binding_and_quotas(plan_code, feature_code, is_enabled, access_mode, variant_code=None, quotas=None):
            plan_id = plans[plan_code].id
            feature_id = features[feature_code].id
            
            binding = db.execute(
                select(PlanFeatureBindingModel).where(
                    PlanFeatureBindingModel.plan_id == plan_id,
                    PlanFeatureBindingModel.feature_id == feature_id
                )
            ).scalar_one_or_none()
            
            if not binding:
                logger.info(f"Creating binding {plan_code} -> {feature_code}...")
                binding = PlanFeatureBindingModel(
                    plan_id=plan_id,
                    feature_id=feature_id,
                    is_enabled=is_enabled,
                    access_mode=access_mode,
                    variant_code=variant_code,
                    source_origin=SourceOrigin.MANUAL
                )
                db.add(binding)
                db.flush()
            else:
                logger.info(f"Binding {plan_code} -> {feature_code} already exists. Updating...")
                binding.is_enabled = is_enabled
                binding.access_mode = access_mode
                binding.variant_code = variant_code
                db.flush()
            
            if quotas:
                for q_data in quotas:
                    quota = db.execute(
                        select(PlanFeatureQuotaModel).where(
                            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id,
                            PlanFeatureQuotaModel.quota_key == q_data["quota_key"],
                            PlanFeatureQuotaModel.period_unit == q_data["period_unit"],
                            PlanFeatureQuotaModel.period_value == q_data["period_value"],
                            PlanFeatureQuotaModel.reset_mode == q_data["reset_mode"]
                        )
                    ).scalar_one_or_none()
                    
                    if not quota:
                        logger.info(f"  Creating quota {q_data['quota_key']} for {plan_code} -> {feature_code}...")
                        quota = PlanFeatureQuotaModel(
                            plan_feature_binding_id=binding.id,
                            **q_data,
                            source_origin=SourceOrigin.MANUAL
                        )
                        db.add(quota)
                    else:
                        logger.info(f"  Quota {q_data['quota_key']} for {plan_code} -> {feature_code} already exists. Updating limit...")
                        quota.quota_limit = q_data["quota_limit"]
                db.flush()

        # FREE Plan Bindings
        upsert_binding_and_quotas("free", "natal_chart_short", True, AccessMode.UNLIMITED)
        upsert_binding_and_quotas("free", "natal_chart_long", False, AccessMode.DISABLED)
        upsert_binding_and_quotas("free", "astrologer_chat", False, AccessMode.DISABLED)
        upsert_binding_and_quotas("free", "thematic_consultation", False, AccessMode.DISABLED)

        # TRIAL Plan Bindings
        upsert_binding_and_quotas("trial", "natal_chart_short", True, AccessMode.UNLIMITED)
        upsert_binding_and_quotas("trial", "natal_chart_long", True, AccessMode.QUOTA, "single_astrologer", [
            {"quota_key": "interpretations", "quota_limit": 1, "period_unit": PeriodUnit.LIFETIME, "period_value": 1, "reset_mode": ResetMode.LIFETIME}
        ])
        upsert_binding_and_quotas("trial", "astrologer_chat", False, AccessMode.DISABLED)
        upsert_binding_and_quotas("trial", "thematic_consultation", True, AccessMode.QUOTA, None, [
            {"quota_key": "consultations", "quota_limit": 1, "period_unit": PeriodUnit.WEEK, "period_value": 1, "reset_mode": ResetMode.CALENDAR}
        ])

        # BASIC Plan Bindings
        upsert_binding_and_quotas("basic", "natal_chart_short", True, AccessMode.UNLIMITED)
        upsert_binding_and_quotas("basic", "natal_chart_long", True, AccessMode.QUOTA, "single_astrologer", [
            {"quota_key": "interpretations", "quota_limit": 1, "period_unit": PeriodUnit.LIFETIME, "period_value": 1, "reset_mode": ResetMode.LIFETIME}
        ])
        upsert_binding_and_quotas("basic", "astrologer_chat", True, AccessMode.QUOTA, None, [
            {"quota_key": "messages", "quota_limit": 5, "period_unit": PeriodUnit.DAY, "period_value": 1, "reset_mode": ResetMode.CALENDAR}
        ])
        upsert_binding_and_quotas("basic", "thematic_consultation", True, AccessMode.QUOTA, None, [
            {"quota_key": "consultations", "quota_limit": 1, "period_unit": PeriodUnit.WEEK, "period_value": 1, "reset_mode": ResetMode.CALENDAR}
        ])

        # PREMIUM Plan Bindings
        upsert_binding_and_quotas("premium", "natal_chart_short", True, AccessMode.UNLIMITED)
        upsert_binding_and_quotas("premium", "natal_chart_long", True, AccessMode.QUOTA, "multi_astrologer", [
            {"quota_key": "interpretations", "quota_limit": 5, "period_unit": PeriodUnit.LIFETIME, "period_value": 1, "reset_mode": ResetMode.LIFETIME}
        ])
        upsert_binding_and_quotas("premium", "astrologer_chat", True, AccessMode.QUOTA, None, [
            {"quota_key": "messages", "quota_limit": 2000, "period_unit": PeriodUnit.MONTH, "period_value": 1, "reset_mode": ResetMode.CALENDAR}
        ])
        upsert_binding_and_quotas("premium", "thematic_consultation", True, AccessMode.QUOTA, None, [
            {"quota_key": "consultations", "quota_limit": 2, "period_unit": PeriodUnit.DAY, "period_value": 1, "reset_mode": ResetMode.CALENDAR}
        ])

        db.commit()
        print("\nSeeding complete.")
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        print(f"Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
