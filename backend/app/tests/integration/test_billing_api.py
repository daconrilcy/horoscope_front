import pytest
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
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.infra.observability.metrics import reset_metrics
from app.main import app
from app.services.billing.service import BillingService

client = TestClient(app)


def _cleanup_tables() -> None:
    BillingService.reset_subscription_status_cache()
    reset_metrics()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            UserDailyQuotaUsageModel,
            UserSubscriptionModel,
            BillingPlanModel,
            StripeBillingProfileModel,
            UserModel,
        ):
            db.execute(delete(model))

        # Seed canonical features
        feature = FeatureCatalogModel(
            feature_code="astrologer_chat",
            feature_name="Astrologer chat",
            is_metered=True,
        )
        db.add(feature)
        db.flush()

        # Seed basic plan
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

        # Seed premium plan
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


def _register_and_get_access_token() -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": "billing-api-user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]


def test_billing_subscription_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/billing/subscription")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_billing_plans_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/billing/plans")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_decommissioned_endpoints_return_404() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    for path in ["/v1/billing/checkout", "/v1/billing/retry", "/v1/billing/plan-change"]:
        resp = client.post(path, headers=headers, json={})
        assert resp.status_code == 404


def test_billing_plans_are_available_for_authenticated_user() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        BillingService.ensure_default_plans(db)
        db.commit()

    response = client.get("/v1/billing/plans", headers=headers)
    assert response.status_code == 200
    payload = response.json()["data"]
    codes = {plan["code"] for plan in payload}
    assert {"basic", "premium"}.issubset(codes)
    assert "trial" not in codes


def test_billing_plans_normalize_zero_prices_for_canonical_plans() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        db.add_all(
            [
                BillingPlanModel(
                    code="basic",
                    display_name="Basic",
                    monthly_price_cents=0,
                    currency="EUR",
                    daily_message_limit=50,
                    is_visible_to_users=True,
                    is_available_to_users=True,
                    is_active=True,
                ),
                BillingPlanModel(
                    code="premium",
                    display_name="Premium",
                    monthly_price_cents=0,
                    currency="EUR",
                    daily_message_limit=1000,
                    is_visible_to_users=True,
                    is_available_to_users=True,
                    is_active=True,
                ),
            ]
        )
        db.commit()

    response = client.get("/v1/billing/plans", headers=headers)
    assert response.status_code == 200
    payload = {plan["code"]: plan for plan in response.json()["data"]}
    assert payload["basic"]["monthly_price_cents"] == 900
    assert payload["premium"]["monthly_price_cents"] == 2900


def test_billing_plans_hide_user_invisible_trial_plan() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        db.add_all(
            [
                BillingPlanModel(
                    code="trial",
                    display_name="Trial",
                    monthly_price_cents=0,
                    currency="EUR",
                    daily_message_limit=1,
                    is_visible_to_users=False,
                    is_available_to_users=False,
                    is_active=True,
                ),
                BillingPlanModel(
                    code="basic",
                    display_name="Basic",
                    monthly_price_cents=900,
                    currency="EUR",
                    daily_message_limit=50,
                    is_visible_to_users=True,
                    is_available_to_users=True,
                    is_active=True,
                ),
            ]
        )
        db.commit()

    response = client.get("/v1/billing/plans", headers=headers)

    assert response.status_code == 200
    payload = {plan["code"]: plan for plan in response.json()["data"]}
    assert "trial" not in payload
    assert payload["basic"]["is_visible_to_users"] is True
    assert payload["basic"]["is_available_to_users"] is True


def test_billing_subscription_status_with_stripe_profile() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email="billing-api-user@example.com").one()
        db.add(
            StripeBillingProfileModel(
                user_id=user.id,
                subscription_status="active",
                entitlement_plan="basic",
            )
        )
        db.commit()

    status = client.get("/v1/billing/subscription", headers=headers)
    assert status.status_code == 200
    payload = status.json()["data"]
    assert payload["status"] == "active"
    assert payload["plan"]["code"] == "basic"


def test_billing_subscription_status_with_legacy_fallback() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email="billing-api-user@example.com").one()
        plans = BillingService.ensure_default_plans(db)
        plan = plans["basic"]
        db.add(
            UserSubscriptionModel(
                user_id=user.id,
                plan_id=plan.id,
                status="active",
            )
        )
        db.commit()

    status = client.get("/v1/billing/subscription", headers=headers)
    assert status.status_code == 200
    payload = status.json()["data"]
    assert payload["status"] == "active"
    assert payload["plan"]["code"] == "basic"  # Canonical code


@pytest.mark.parametrize(
    ("subscription_status", "entitlement_plan", "expected_status", "expected_plan_code"),
    [
        ("active", "basic", "active", "basic"),
        ("trialing", "basic", "active", "basic"),
        ("incomplete", "free", "inactive", None),
    ],
)
def test_billing_subscription_matrix(
    subscription_status: str,
    entitlement_plan: str,
    expected_status: str,
    expected_plan_code: str | None,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email="billing-api-user@example.com").one()
        db.add(
            StripeBillingProfileModel(
                user_id=user.id,
                subscription_status=subscription_status,
                entitlement_plan=entitlement_plan,
            )
        )
        db.commit()

    status = client.get("/v1/billing/subscription", headers=headers)
    assert status.status_code == 200
    payload = status.json()["data"]
    assert payload["status"] == expected_status
    if expected_plan_code:
        assert payload["plan"]["code"] == expected_plan_code
    else:
        assert payload["plan"] is None


def test_billing_token_usage_returns_aggregated_usage() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email="billing-api-user@example.com").one()
        db.add_all(
            [
                UserTokenUsageLogModel(
                    user_id=user.id,
                    feature_code="astrologer_chat",
                    provider_model="gpt-4o-mini",
                    tokens_in=100,
                    tokens_out=40,
                    tokens_total=140,
                    request_id="rid-chat-1",
                ),
                UserTokenUsageLogModel(
                    user_id=user.id,
                    feature_code="thematic_consultation",
                    provider_model="gpt-4o",
                    tokens_in=250,
                    tokens_out=90,
                    tokens_total=340,
                    request_id="rid-consult-1",
                ),
            ]
        )
        db.commit()

    response = client.get("/v1/billing/token-usage?period=all", headers=headers)
    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["period"]["unit"] == "all"
    assert payload["summary"] == {
        "tokens_total": 480,
        "tokens_in": 350,
        "tokens_out": 130,
    }

    by_feature = {entry["feature_code"]: entry for entry in payload["by_feature"]}
    assert by_feature["astrologer_chat"] == {
        "feature_code": "astrologer_chat",
        "tokens_total": 140,
        "tokens_in": 100,
        "tokens_out": 40,
    }
    assert by_feature["thematic_consultation"] == {
        "feature_code": "thematic_consultation",
        "tokens_total": 340,
        "tokens_in": 250,
        "tokens_out": 90,
    }
