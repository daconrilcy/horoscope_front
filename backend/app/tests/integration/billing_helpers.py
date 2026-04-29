# Helpers partages pour les tests d'integration de l'API billing.
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.billing import (
    BillingPlanModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.observability.metrics import reset_metrics
from app.main import app
from app.services.billing.service import BillingService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def cleanup_billing_tables() -> None:
    """Recree le schema et les donnees minimales billing attendues par les tests."""
    BillingService.reset_subscription_status_cache()
    reset_metrics()
    engine = app_test_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with open_app_test_db_session() as db:
        for model in (
            UserDailyQuotaUsageModel,
            UserSubscriptionModel,
            BillingPlanModel,
            StripeBillingProfileModel,
            UserModel,
        ):
            db.execute(delete(model))

        feature = FeatureCatalogModel(
            feature_code="astrologer_chat",
            feature_name="Astrologer chat",
            is_metered=True,
        )
        db.add(feature)
        db.flush()

        p_basic = PlanCatalogModel(
            plan_code="basic",
            plan_name="Basic",
            audience=Audience.B2C,
        )
        db.add(p_basic)
        db.flush()

        b_basic = PlanFeatureBindingModel(
            plan_id=p_basic.id,
            feature_id=feature.id,
            access_mode=AccessMode.QUOTA,
            is_enabled=True,
        )
        db.add(b_basic)
        db.flush()

        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b_basic.id,
                quota_key="tokens",
                quota_limit=50_000,
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )

        p_premium = PlanCatalogModel(
            plan_code="premium",
            plan_name="Premium",
            audience=Audience.B2C,
        )
        db.add(p_premium)
        db.flush()

        b_premium = PlanFeatureBindingModel(
            plan_id=p_premium.id,
            feature_id=feature.id,
            access_mode=AccessMode.QUOTA,
            is_enabled=True,
        )
        db.add(b_premium)
        db.flush()

        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b_premium.id,
                quota_key="tokens",
                quota_limit=1_500_000,
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )

        db.commit()


def register_and_get_billing_access_token() -> str:
    """Inscrit l'utilisateur billing de test et retourne son jeton d'acces."""
    register = client.post(
        "/v1/auth/register",
        json={"email": "billing-api-user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]
