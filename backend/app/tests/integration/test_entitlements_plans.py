from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.base import Base
from app.infra.db.models.billing import BillingPlanModel
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
from app.main import app
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def _override_auth(user_id=42, role="user"):
    def _override():
        return AuthenticatedUser(
            id=user_id,
            role=role,
            email=f"test_{user_id}@example.com",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    return _override


def _cleanup_db():
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())


def test_get_plans_catalog_unauthenticated():
    _cleanup_db()
    response = client.get("/v1/entitlements/plans")
    assert response.status_code == 401


def test_get_plans_catalog_success():
    _cleanup_db()

    # 1. Setup Data
    with open_app_test_db_session() as db_session:
        # Features
        f1 = FeatureCatalogModel(feature_code="natal_chart_short", feature_name="Short Chart")
        f2 = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
        # We need all 5 canonical features for exhaustivity check
        f3 = FeatureCatalogModel(feature_code="natal_chart_long", feature_name="Long Chart")
        f4 = FeatureCatalogModel(feature_code="thematic_consultation", feature_name="Thematic")
        f5 = FeatureCatalogModel(feature_code="horoscope_daily", feature_name="Horoscope Daily")
        db_session.add_all([f1, f2, f3, f4, f5])
        db_session.commit()

        # Plans
        p_free = PlanCatalogModel(
            plan_code="free", plan_name="Free Plan", audience=Audience.B2C, is_active=True
        )
        p_basic = PlanCatalogModel(
            plan_code="basic", plan_name="Basic Plan", audience=Audience.B2C, is_active=True
        )
        p_trial = PlanCatalogModel(
            plan_code="trial", plan_name="Trial Plan", audience=Audience.B2C, is_active=True
        )
        db_session.add_all([p_free, p_basic, p_trial])
        db_session.commit()

        # Billing Plans (Prices)
        bp_basic = BillingPlanModel(
            code="basic",
            display_name="Basic",
            monthly_price_cents=900,
            currency="EUR",
            daily_message_limit=5,
            is_visible_to_users=True,
            is_available_to_users=True,
            is_active=True,
        )
        bp_trial = BillingPlanModel(
            code="trial",
            display_name="Trial",
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=1,
            is_visible_to_users=False,
            is_available_to_users=False,
            is_active=True,
        )
        db_session.add_all([bp_basic, bp_trial])
        db_session.commit()

        # Bindings
        # Plan free only has natal_chart_short
        b1 = PlanFeatureBindingModel(
            plan_id=p_free.id,
            feature_id=f1.id,
            access_mode=AccessMode.UNLIMITED,
            is_enabled=True,
        )
        # Plan basic has astrologer_chat with quota
        b2 = PlanFeatureBindingModel(
            plan_id=p_basic.id, feature_id=f2.id, access_mode=AccessMode.QUOTA, is_enabled=True
        )
        db_session.add_all([b1, b2])
        db_session.commit()

        # Quotas
        q1 = PlanFeatureQuotaModel(
            plan_feature_binding_id=b2.id,
            quota_key="tokens",
            quota_limit=10,
            period_unit=PeriodUnit.MONTH,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        q2 = PlanFeatureQuotaModel(
            plan_feature_binding_id=b2.id,
            quota_key="tokens",
            quota_limit=2,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db_session.add_all([q1, q2])
        db_session.commit()

    # Overrides
    app.dependency_overrides[require_authenticated_user] = _override_auth()

    # 2. Call API
    response = client.get("/v1/entitlements/plans")

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()["data"]

    # Plans order: free, basic (trial masqué)
    assert len(data) == 2
    assert data[0]["plan_code"] == "free"
    assert data[0]["monthly_price_cents"] == 0
    assert data[0]["processing_priority"] == "low"
    assert data[1]["plan_code"] == "basic"
    assert data[1]["monthly_price_cents"] == 900
    assert data[1]["processing_priority"] == "medium"

    # Features exhaustivity (AC1)
    # Even though plan free only has 1 binding, it should return all 5 features
    assert len(data[0]["features"]) == 5
    codes_free = [f["feature_code"] for f in data[0]["features"]]
    assert set(codes_free) == {
        "natal_chart_short",
        "natal_chart_long",
        "astrologer_chat",
        "thematic_consultation",
        "horoscope_daily",
    }
    # find natal_chart_short
    short_feat = next(f for f in data[0]["features"] if f["feature_code"] == "natal_chart_short")
    assert short_feat["is_enabled"] is True
    # find natal_chart_long
    long_feat = next(f for f in data[0]["features"] if f["feature_code"] == "natal_chart_long")
    assert long_feat["is_enabled"] is False  # natal_chart_long not in plan

    assert len(data[1]["features"]) == 5
    chat_feat = next(f for f in data[1]["features"] if f["feature_code"] == "astrologer_chat")
    assert chat_feat["is_enabled"] is True
    assert chat_feat["access_mode"] == "quota"
    assert len(chat_feat["quotas"]) == 2
    assert [quota["period_unit"] for quota in chat_feat["quotas"]] == ["day", "month"]
    assert [quota["quota_limit"] for quota in chat_feat["quotas"]] == [2, 10]
    assert data[1]["is_active"] is True

    app.dependency_overrides.clear()


def test_get_plans_catalog_forbidden_for_non_user_roles():
    _cleanup_db()
    app.dependency_overrides[require_authenticated_user] = _override_auth(role="support")

    response = client.get("/v1/entitlements/plans")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"

    app.dependency_overrides.clear()


def test_get_plans_catalog_keeps_paid_plans_visible_without_billing_rows():
    _cleanup_db()

    with open_app_test_db_session() as db_session:
        for code, name in (
            ("natal_chart_short", "Short Chart"),
            ("natal_chart_long", "Long Chart"),
            ("astrologer_chat", "Chat"),
            ("thematic_consultation", "Thematic"),
            ("horoscope_daily", "Horoscope Daily"),
        ):
            db_session.add(FeatureCatalogModel(feature_code=code, feature_name=name))

        db_session.add_all(
            [
                PlanCatalogModel(
                    plan_code="free", plan_name="Free Plan", audience=Audience.B2C, is_active=True
                ),
                PlanCatalogModel(
                    plan_code="basic", plan_name="Basic Plan", audience=Audience.B2C, is_active=True
                ),
                PlanCatalogModel(
                    plan_code="premium",
                    plan_name="Premium Plan",
                    audience=Audience.B2C,
                    is_active=True,
                ),
            ]
        )
        db_session.commit()

    app.dependency_overrides[require_authenticated_user] = _override_auth()

    response = client.get("/v1/entitlements/plans")

    assert response.status_code == 200
    data = response.json()["data"]
    assert [plan["plan_code"] for plan in data] == ["free", "basic", "premium"]
    assert data[1]["monthly_price_cents"] == 900
    assert data[2]["monthly_price_cents"] == 2900

    app.dependency_overrides.clear()
