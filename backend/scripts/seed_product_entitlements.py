"""Initialise le catalogue canonique des entitlements produit.

Le script crée ou met à jour les plans B2C, leurs features et les bindings
runtime utilisés par les gates publics.
"""

from __future__ import annotations

import logging

from sqlalchemy import select

from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    SourceOrigin,
)
from app.infra.db.session import SessionLocal
from app.services.canonical_entitlement.audit.mutation_service import (
    CanonicalEntitlementMutationService,
    CanonicalMutationContext,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


_SEED_CONTEXT = CanonicalMutationContext(
    actor_type="script",
    actor_identifier="seed_product_entitlements.py",
)


def seed() -> None:
    desired_bindings: dict[str, dict[str, dict]] = {
        "free": {
            "horoscope_daily": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": "summary_only",
                "quotas": [],
            },
        },
        "trial": {
            "horoscope_daily": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": "full",
                "quotas": [],
            },
        },
        "basic": {
            "horoscope_daily": {
                "is_enabled": True,
                "access_mode": AccessMode.UNLIMITED,
                "variant_code": "full",
                "quotas": [],
            },
        },
        "premium": {
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
