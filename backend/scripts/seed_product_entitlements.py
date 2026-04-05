"""Seed script for product entitlements.

This script initializes the canonical product entitlements catalog:
- Plans: free, trial, basic, premium
- Features: natal_chart_short, natal_chart_long, astrologer_chat, thematic_consultation
- Bindings and quotas for each plan.

Run:
    python backend/scripts/seed_product_entitlements.py
"""

from __future__ import annotations

import logging

from sqlalchemy import select

from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    ResetMode,
    SourceOrigin,
)
from app.infra.db.session import SessionLocal
from app.services.canonical_entitlement_mutation_service import (
    CanonicalEntitlementMutationService,
    CanonicalMutationContext,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


_SEED_CONTEXT = CanonicalMutationContext(
    actor_type="script",
    actor_identifier="seed_product_entitlements.py",
)


def _single_lifetime_interpretation_quota() -> list[dict[str, object]]:
    return [
        {
            "quota_key": "interpretations",
            "quota_limit": 1,
            "period_unit": PeriodUnit.LIFETIME,
            "period_value": 1,
            "reset_mode": ResetMode.LIFETIME,
        }
    ]


def seed() -> None:
    desired_bindings: dict[str, dict[str, dict]] = {
        "free": {
            "natal_chart_short": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": None,
                "quotas": [],
            },
            "natal_chart_long": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": "free_short",
                "quotas": [],
            },
            "astrologer_chat": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": [
                    {
                        "quota_key": "messages",
                        "quota_limit": 1,
                        "period_unit": PeriodUnit.WEEK,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
            },
            "thematic_consultation": {
                "is_enabled": False,
                "access_mode": AccessMode.DISABLED,
                "variant_code": None,
                "quotas": [],
            },
            "horoscope_daily": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": "summary_only",
                "quotas": [],
            },
        },
        "trial": {
            "natal_chart_short": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": _single_lifetime_interpretation_quota(),
            },
            "natal_chart_long": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": "single_astrologer",
                "quotas": [
                    {
                        "quota_key": "interpretations",
                        "quota_limit": 1,
                        "period_unit": PeriodUnit.LIFETIME,
                        "period_value": 1,
                        "reset_mode": ResetMode.LIFETIME,
                    }
                ],
            },
            "astrologer_chat": {
                "is_enabled": False,
                "access_mode": AccessMode.DISABLED,
                "variant_code": None,
                "quotas": [],
            },
            "thematic_consultation": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": [
                    {
                        "quota_key": "tokens",
                        "quota_limit": 5000,
                        "period_unit": PeriodUnit.WEEK,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
            },
            "horoscope_daily": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": "full",
                "quotas": [],
            },
        },
        "basic": {
            "natal_chart_short": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": None,
                "quotas": [],
            },
            "natal_chart_long": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": "single_astrologer",
                "quotas": [
                    {
                        "quota_key": "interpretations",
                        "quota_limit": 1,
                        "period_unit": PeriodUnit.LIFETIME,
                        "period_value": 1,
                        "reset_mode": ResetMode.LIFETIME,
                    }
                ],
            },
            "astrologer_chat": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": [
                    {
                        "quota_key": "tokens",
                        "quota_limit": 10000,
                        "period_unit": PeriodUnit.DAY,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    },
                    {
                        "quota_key": "tokens",
                        "quota_limit": 50000,
                        "period_unit": PeriodUnit.WEEK,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    },
                    {
                        "quota_key": "tokens",
                        "quota_limit": 200000,
                        "period_unit": PeriodUnit.MONTH,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    },
                ],
            },
            "thematic_consultation": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": [
                    {
                        "quota_key": "tokens",
                        "quota_limit": 20000,
                        "period_unit": PeriodUnit.WEEK,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
            },
            "horoscope_daily": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": "full",
                "quotas": [],
            },
        },
        "premium": {
            "natal_chart_short": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": None,
                "quotas": [],
            },
            "natal_chart_long": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": "multi_astrologer",
                "quotas": [
                    {
                        "quota_key": "interpretations",
                        "quota_limit": 5,
                        "period_unit": PeriodUnit.LIFETIME,
                        "period_value": 1,
                        "reset_mode": ResetMode.LIFETIME,
                    }
                ],
            },
            "astrologer_chat": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": [
                    {
                        "quota_key": "tokens",
                        "quota_limit": 50000,
                        "period_unit": PeriodUnit.DAY,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    },
                    {
                        "quota_key": "tokens",
                        "quota_limit": 375000,
                        "period_unit": PeriodUnit.WEEK,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    },
                    {
                        "quota_key": "tokens",
                        "quota_limit": 1500000,
                        "period_unit": PeriodUnit.MONTH,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    },
                ],
            },
            "thematic_consultation": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": [
                    {
                        "quota_key": "tokens",
                        "quota_limit": 200000,
                        "period_unit": PeriodUnit.MONTH,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
            },
            "horoscope_daily": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": "full",
                "quotas": [],
            },
        },
    }

    with SessionLocal() as db:
        try:
            plans_data = [
                {
                    "plan_code": "free",
                    "plan_name": "Free Plan",
                    "audience": Audience.B2C,
                    "source_type": "manual",
                },
                {
                    "plan_code": "trial",
                    "plan_name": "Trial Plan",
                    "audience": Audience.B2C,
                    "source_type": "manual",
                },
                {
                    "plan_code": "basic",
                    "plan_name": "Basic Plan",
                    "audience": Audience.B2C,
                    "source_type": "manual",
                },
                {
                    "plan_code": "premium",
                    "plan_name": "Premium Plan",
                    "audience": Audience.B2C,
                    "source_type": "manual",
                },
            ]

            plans: dict[str, PlanCatalogModel] = {}
            for p_data in plans_data:
                plan = db.execute(
                    select(PlanCatalogModel).where(
                        PlanCatalogModel.plan_code == p_data["plan_code"]
                    )
                ).scalar_one_or_none()
                if plan is None:
                    logger.info("Creating plan '%s'...", p_data["plan_code"])
                    plan = PlanCatalogModel(**p_data)
                    db.add(plan)
                    db.flush()
                else:
                    logger.info("Plan '%s' already exists. Updating...", p_data["plan_code"])
                    plan.plan_name = p_data["plan_name"]
                    plan.audience = p_data["audience"]
                    plan.source_type = p_data["source_type"]
                    plan.is_active = True
                    db.flush()
                plans[p_data["plan_code"]] = plan

            features_data = [
                {
                    "feature_code": "natal_chart_short",
                    "feature_name": "Natal Chart Short",
                    "is_metered": True,
                },
                {
                    "feature_code": "natal_chart_long",
                    "feature_name": "Natal Chart Long",
                    "is_metered": True,
                },
                {
                    "feature_code": "astrologer_chat",
                    "feature_name": "Astrologer Chat",
                    "is_metered": True,
                },
                {
                    "feature_code": "thematic_consultation",
                    "feature_name": "Thematic Consultation",
                    "is_metered": True,
                },
                {
                    "feature_code": "horoscope_daily",
                    "feature_name": "Horoscope Daily",
                    "is_metered": False,
                },
            ]

            features: dict[str, FeatureCatalogModel] = {}
            for f_data in features_data:
                feature = db.execute(
                    select(FeatureCatalogModel).where(
                        FeatureCatalogModel.feature_code == f_data["feature_code"]
                    )
                ).scalar_one_or_none()
                if feature is None:
                    logger.info("Creating feature '%s'...", f_data["feature_code"])
                    feature = FeatureCatalogModel(**f_data)
                    db.add(feature)
                    db.flush()
                else:
                    logger.info("Feature '%s' already exists. Updating...", f_data["feature_code"])
                    feature.feature_name = f_data["feature_name"]
                    feature.is_metered = f_data["is_metered"]
                    feature.is_active = True
                    db.flush()
                features[f_data["feature_code"]] = feature

            for plan_code, features_config in desired_bindings.items():
                for feature_code, binding_config in features_config.items():
                    logger.info("Upserting binding %s -> %s...", plan_code, feature_code)
                    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
                        db,
                        plan=plans[plan_code],
                        feature_code=feature_code,
                        source_origin=SourceOrigin.MANUAL,
                        mutation_context=_SEED_CONTEXT,
                        **binding_config,
                    )

            db.commit()
            print("\nSeeding complete.")
        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed()
