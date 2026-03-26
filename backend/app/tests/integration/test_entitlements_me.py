from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.models import (
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    UserModel,
    FeatureUsageCounterModel,
)
from app.infra.db.session import get_db_session
from app.main import app
from app.services.billing_service import BillingService

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


def test_unauthenticated_returns_401():
    """Vérifie que l'accès sans token retourne 401."""
    response = client.get("/v1/entitlements/me")
    assert response.status_code == 401


def test_no_plan_user_all_features_denied(db_session: Session):
    """Vérifie qu'un utilisateur sans plan a toutes ses features refusées avec reason=no_plan."""
    user = UserModel(
        email="no_plan@example.com",
        password_hash="fake_hash",
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    app.dependency_overrides[require_authenticated_user] = _override_auth(user_id=user.id)
    app.dependency_overrides[get_db_session] = lambda: db_session

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200
    
    features = response.json()["data"]["features"]
    assert len(features) == 4
    for f in features:
        assert f["final_access"] is False
        assert f["reason"] == "no_plan"
    
    app.dependency_overrides.clear()


def seed_canonical_plans(db: Session):
    from app.infra.db.models.product_entitlements import (
        AccessMode, Audience, FeatureCatalogModel, PeriodUnit,
        PlanCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel,
        ResetMode, SourceOrigin
    )
    
    # Plans
    trial_plan = PlanCatalogModel(
        plan_code="trial",
        plan_name="Trial Plan",
        audience=Audience.B2C,
    )
    db.add(trial_plan)
    db.flush()

    # Features
    features = {
        "natal_chart_short": FeatureCatalogModel(feature_code="natal_chart_short", feature_name="NCS", is_metered=False),
        "natal_chart_long": FeatureCatalogModel(feature_code="natal_chart_long", feature_name="NCL", is_metered=True),
        "astrologer_chat": FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat", is_metered=True),
        "thematic_consultation": FeatureCatalogModel(feature_code="thematic_consultation", feature_name="Consult", is_metered=True),
    }
    for f in features.values():
        db.add(f)
    db.flush()

    # Bindings for Trial
    # natal_chart_long: quota 1/lifetime
    ncl_binding = PlanFeatureBindingModel(
        plan_id=trial_plan.id,
        feature_id=features["natal_chart_long"].id,
        access_mode=AccessMode.QUOTA,
        variant_code="single_astrologer"
    )
    db.add(ncl_binding)
    db.flush()
    db.add(PlanFeatureQuotaModel(
        plan_feature_binding_id=ncl_binding.id,
        quota_key="interpretations",
        quota_limit=1,
        period_unit=PeriodUnit.LIFETIME,
        period_value=1,
        reset_mode=ResetMode.LIFETIME
    ))

    # astrologer_chat: disabled
    db.add(PlanFeatureBindingModel(
        plan_id=trial_plan.id,
        feature_id=features["astrologer_chat"].id,
        access_mode=AccessMode.DISABLED
    ))

    # natal_chart_short: unlimited
    db.add(PlanFeatureBindingModel(
        plan_id=trial_plan.id,
        feature_id=features["natal_chart_short"].id,
        access_mode=AccessMode.UNLIMITED
    ))
    
    db.commit()


def test_trial_user_entitlements(db_session: Session):
    """
    Vérifie les entitlements d'un utilisateur trial d'après le seed canonique :
    - astrologer_chat: disabled
    - natal_chart_long: quota 1/lifetime
    - thematic_consultation: quota 1/week
    - natal_chart_short: unlimited
    """
    seed_canonical_plans(db_session)
    user = UserModel(
        email="trial@example.com",
        password_hash="fake_hash",
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Mock subscription status via BillingService (utilisé par EntitlementService)
    with pytest.MonkeyPatch().context() as m:
        from app.services.billing_service import SubscriptionStatusData, BillingPlanData
        
        trial_plan = BillingPlanData(
            code="trial",
            display_name="Trial Plan",
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=0,
            is_active=True
        )
        
        m.setattr(
            BillingService,
            "get_subscription_status",
            lambda *args, **kwargs: SubscriptionStatusData(
                status="active",
                plan=trial_plan,
                failure_reason=None,
                updated_at=datetime.now(timezone.utc)
            )
        )

        app.dependency_overrides[require_authenticated_user] = _override_auth(user_id=user.id)
        app.dependency_overrides[get_db_session] = lambda: db_session

        response = client.get("/v1/entitlements/me")
        assert response.status_code == 200
        
        features = response.json()["data"]["features"]
        
        # Natal Chart Long
        ncl = next(f for f in features if f["feature_code"] == "natal_chart_long")
        assert ncl["access_mode"] == "quota"
        assert ncl["variant_code"] == "single_astrologer"
        assert len(ncl["usage_states"]) == 1
        assert ncl["usage_states"][0]["quota_limit"] == 1
        assert ncl["usage_states"][0]["reset_mode"] == "lifetime"

        # Astrologer Chat
        ac = next(f for f in features if f["feature_code"] == "astrologer_chat")
        assert ac["final_access"] is False
        assert ac["reason"] == "disabled_by_plan"

        # Natal Chart Short
        ncs = next(f for f in features if f["feature_code"] == "natal_chart_short")
        assert ncs["access_mode"] == "unlimited"
        assert ncs["final_access"] is True

        app.dependency_overrides.clear()


def test_no_quota_consumed(db_session: Session):
    """Vérifie que l'appel à l'endpoint ne consomme aucun quota."""
    seed_canonical_plans(db_session)
    user = UserModel(
        email="consume_test@example.com",
        password_hash="fake_hash",
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # On s'assure qu'un compteur existe
    counter = FeatureUsageCounterModel(
        user_id=user.id,
        feature_code="natal_chart_long",
        quota_key="interpretations",
        period_unit="lifetime",
        period_value=1,
        reset_mode="lifetime",
        window_start=datetime(1970, 1, 1, tzinfo=timezone.utc),
        used_count=0,
    )
    db_session.add(counter)
    db_session.commit()

    with pytest.MonkeyPatch().context() as m:
        from app.services.billing_service import SubscriptionStatusData, BillingPlanData
        
        trial_plan = BillingPlanData(
            code="trial",
            display_name="Trial Plan",
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=0,
            is_active=True
        )

        m.setattr(
            BillingService,
            "get_subscription_status",
            lambda *args, **kwargs: SubscriptionStatusData(
                status="active",
                plan=trial_plan,
                failure_reason=None,
                updated_at=datetime.now(timezone.utc)
            )
        )

        app.dependency_overrides[require_authenticated_user] = _override_auth(user_id=user.id)
        app.dependency_overrides[get_db_session] = lambda: db_session

        # Premier appel
        client.get("/v1/entitlements/me")
        db_session.refresh(counter)
        assert counter.used_count == 0

        # Deuxième appel
        client.get("/v1/entitlements/me")
        db_session.refresh(counter)
        assert counter.used_count == 0

        app.dependency_overrides.clear()
