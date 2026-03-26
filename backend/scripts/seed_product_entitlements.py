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
from collections.abc import Iterable

from sqlalchemy import select

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
from app.infra.db.session import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _quota_identity(quota: dict) -> tuple[str, PeriodUnit, int, ResetMode]:
    return (
        quota["quota_key"],
        quota["period_unit"],
        quota["period_value"],
        quota["reset_mode"],
    )


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
                "is_enabled": False,
                "access_mode": AccessMode.DISABLED,
                "variant_code": None,
                "quotas": [],
            },
            "astrologer_chat": {
                "is_enabled": False,
                "access_mode": AccessMode.DISABLED,
                "variant_code": None,
                "quotas": [],
            },
            "thematic_consultation": {
                "is_enabled": False,
                "access_mode": AccessMode.DISABLED,
                "variant_code": None,
                "quotas": [],
            },
        },
        "trial": {
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
                        "quota_key": "consultations",
                        "quota_limit": 1,
                        "period_unit": PeriodUnit.WEEK,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
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
                        "quota_key": "messages",
                        "quota_limit": 5,
                        "period_unit": PeriodUnit.DAY,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
            },
            "thematic_consultation": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": [
                    {
                        "quota_key": "consultations",
                        "quota_limit": 1,
                        "period_unit": PeriodUnit.WEEK,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
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
                        "quota_key": "messages",
                        "quota_limit": 2000,
                        "period_unit": PeriodUnit.MONTH,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
            },
            "thematic_consultation": {
                "is_enabled": True,
                "access_mode": AccessMode.QUOTA,
                "variant_code": None,
                "quotas": [
                    {
                        "quota_key": "consultations",
                        "quota_limit": 2,
                        "period_unit": PeriodUnit.DAY,
                        "period_value": 1,
                        "reset_mode": ResetMode.CALENDAR,
                    }
                ],
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
                    "is_metered": False,
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

            def upsert_binding_and_quotas(
                plan_code: str,
                feature_code: str,
                *,
                is_enabled: bool,
                access_mode: AccessMode,
                variant_code: str | None = None,
                quotas: Iterable[dict] = (),
            ) -> None:
                plan_id = plans[plan_code].id
                feature_id = features[feature_code].id

                binding = db.execute(
                    select(PlanFeatureBindingModel).where(
                        PlanFeatureBindingModel.plan_id == plan_id,
                        PlanFeatureBindingModel.feature_id == feature_id,
                    )
                ).scalar_one_or_none()

                if binding is None:
                    logger.info("Creating binding %s -> %s...", plan_code, feature_code)
                    binding = PlanFeatureBindingModel(
                        plan_id=plan_id,
                        feature_id=feature_id,
                        is_enabled=is_enabled,
                        access_mode=access_mode,
                        variant_code=variant_code,
                        source_origin=SourceOrigin.MANUAL,
                    )
                    db.add(binding)
                    db.flush()
                else:
                    logger.info(
                        "Binding %s -> %s already exists. Updating...", plan_code, feature_code
                    )
                    binding.is_enabled = is_enabled
                    binding.access_mode = access_mode
                    binding.variant_code = variant_code
                    binding.source_origin = SourceOrigin.MANUAL
                    db.flush()

                desired_quotas = list(quotas)
                desired_keys = {_quota_identity(q) for q in desired_quotas}

                existing_quotas = (
                    db.execute(
                        select(PlanFeatureQuotaModel).where(
                            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
                        )
                    )
                    .scalars()
                    .all()
                )

                for existing in existing_quotas:
                    identity = (
                        existing.quota_key,
                        existing.period_unit,
                        existing.period_value,
                        existing.reset_mode,
                    )
                    if identity not in desired_keys:
                        logger.info(
                            "  Removing stale quota %s for %s -> %s...",
                            existing.quota_key,
                            plan_code,
                            feature_code,
                        )
                        db.delete(existing)

                for q_data in desired_quotas:
                    quota = db.execute(
                        select(PlanFeatureQuotaModel).where(
                            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id,
                            PlanFeatureQuotaModel.quota_key == q_data["quota_key"],
                            PlanFeatureQuotaModel.period_unit == q_data["period_unit"],
                            PlanFeatureQuotaModel.period_value == q_data["period_value"],
                            PlanFeatureQuotaModel.reset_mode == q_data["reset_mode"],
                        )
                    ).scalar_one_or_none()

                    if quota is None:
                        logger.info(
                            "  Creating quota %s for %s -> %s...",
                            q_data["quota_key"],
                            plan_code,
                            feature_code,
                        )
                        quota = PlanFeatureQuotaModel(
                            plan_feature_binding_id=binding.id,
                            source_origin=SourceOrigin.MANUAL,
                            **q_data,
                        )
                        db.add(quota)
                    else:
                        logger.info(
                            "  Quota %s for %s -> %s already exists. Updating...",
                            q_data["quota_key"],
                            plan_code,
                            feature_code,
                        )
                        quota.quota_limit = q_data["quota_limit"]
                        quota.source_origin = SourceOrigin.MANUAL

                db.flush()

            for plan_code, features_config in desired_bindings.items():
                for feature_code, binding_config in features_config.items():
                    upsert_binding_and_quotas(plan_code, feature_code, **binding_config)

            db.commit()
            print("\nSeeding complete.")
        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed()
