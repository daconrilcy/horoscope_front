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
from app.infra.db.session import SessionLocal, engine
from app.main import app

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
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_get_plans_catalog_unauthenticated():
    _cleanup_db()
    response = client.get("/v1/entitlements/plans")
    assert response.status_code == 401


def test_get_plans_catalog_success():
    _cleanup_db()

    # 1. Setup Data
    with SessionLocal() as db_session:
        # Features
        f1 = FeatureCatalogModel(feature_code="natal_chart_short", feature_name="Short Chart")
        f2 = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
        # We need all 4 canonical features for exhaustivity check
        f3 = FeatureCatalogModel(feature_code="natal_chart_long", feature_name="Long Chart")
        f4 = FeatureCatalogModel(feature_code="thematic_consultation", feature_name="Thematic")
        db_session.add_all([f1, f2, f3, f4])
        db_session.commit()

        # Plans
        p_free = PlanCatalogModel(
            plan_code="free", plan_name="Free Plan", audience=Audience.B2C, is_active=True
        )
        p_basic = PlanCatalogModel(
            plan_code="basic", plan_name="Basic Plan", audience=Audience.B2C, is_active=True
        )
        db_session.add_all([p_free, p_basic])
        db_session.commit()

        # Billing Plans (Prices)
        bp_basic = BillingPlanModel(
            code="basic",
            display_name="Basic",
            monthly_price_cents=900,
            currency="EUR",
            daily_message_limit=5,
            is_active=True,
        )
        db_session.add(bp_basic)
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
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db_session.add(q1)
        db_session.commit()

    # Overrides
    app.dependency_overrides[require_authenticated_user] = _override_auth()

    # 2. Call API
    response = client.get("/v1/entitlements/plans")

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()["data"]

    # Plans order: free, basic
    assert len(data) == 2
    assert data[0]["plan_code"] == "free"
    assert data[0]["monthly_price_cents"] == 0
    assert data[1]["plan_code"] == "basic"
    assert data[1]["monthly_price_cents"] == 900

    # Features exhaustivity (AC1)
    # Even though plan free only has 1 binding, it should return all 4 features
    assert len(data[0]["features"]) == 4
    codes_free = [f["feature_code"] for f in data[0]["features"]]
    assert codes_free == [
        "natal_chart_short",
        "natal_chart_long",
        "astrologer_chat",
        "thematic_consultation",
    ]
    assert data[0]["features"][0]["is_enabled"] is True
    assert data[0]["features"][1]["is_enabled"] is False  # natal_chart_long not in plan

    assert len(data[1]["features"]) == 4
    assert data[1]["features"][2]["feature_code"] == "astrologer_chat"
    assert data[1]["features"][2]["is_enabled"] is True
    assert data[1]["features"][2]["access_mode"] == "quota"
    assert len(data[1]["features"][2]["quotas"]) == 1
    assert data[1]["features"][2]["quotas"][0]["quota_limit"] == 10

    app.dependency_overrides.clear()
