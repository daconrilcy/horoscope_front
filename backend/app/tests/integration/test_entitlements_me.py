from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.models import FeatureUsageCounterModel, UserModel
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
from app.infra.db.session import get_db_session
from app.main import app
from app.services.billing_service import BillingPlanData, BillingService, SubscriptionStatusData

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


FEATURE_CODES = {
    "astrologer_chat",
    "thematic_consultation",
    "natal_chart_long",
    "natal_chart_short",
}


def _subscription(plan_code: str) -> SubscriptionStatusData:
    return SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code=plan_code,
            display_name=plan_code.title(),
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=0,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=datetime.now(timezone.utc),
    )


def _add_binding(
    db: Session,
    *,
    plan_id: int,
    feature_id: int,
    access_mode: AccessMode,
    variant_code: str | None = None,
    quota_key: str | None = None,
    quota_limit: int | None = None,
    period_unit: PeriodUnit | None = None,
    period_value: int | None = None,
    reset_mode: ResetMode | None = None,
) -> None:
    binding = PlanFeatureBindingModel(
        plan_id=plan_id,
        feature_id=feature_id,
        access_mode=access_mode,
        variant_code=variant_code,
    )
    db.add(binding)
    db.flush()

    if access_mode != AccessMode.QUOTA:
        return

    assert quota_key is not None
    assert quota_limit is not None
    assert period_unit is not None
    assert period_value is not None
    assert reset_mode is not None
    db.add(
        PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key=quota_key,
            quota_limit=quota_limit,
            period_unit=period_unit,
            period_value=period_value,
            reset_mode=reset_mode,
        )
    )


def seed_canonical_plans(db: Session) -> None:
    plans = {
        code: PlanCatalogModel(
            plan_code=code,
            plan_name=f"{code.title()} Plan",
            audience=Audience.B2C,
        )
        for code in ("trial", "basic", "premium")
    }
    db.add_all(plans.values())
    db.flush()

    features = {
        "natal_chart_short": FeatureCatalogModel(
            feature_code="natal_chart_short",
            feature_name="Natal Chart Short",
            is_metered=False,
        ),
        "natal_chart_long": FeatureCatalogModel(
            feature_code="natal_chart_long",
            feature_name="Natal Chart Long",
            is_metered=True,
        ),
        "astrologer_chat": FeatureCatalogModel(
            feature_code="astrologer_chat",
            feature_name="Astrologer Chat",
            is_metered=True,
        ),
        "thematic_consultation": FeatureCatalogModel(
            feature_code="thematic_consultation",
            feature_name="Thematic Consultation",
            is_metered=True,
        ),
    }
    db.add_all(features.values())
    db.flush()

    trial_id = plans["trial"].id
    _add_binding(
        db,
        plan_id=trial_id,
        feature_id=features["astrologer_chat"].id,
        access_mode=AccessMode.DISABLED,
    )
    _add_binding(
        db,
        plan_id=trial_id,
        feature_id=features["thematic_consultation"].id,
        access_mode=AccessMode.QUOTA,
        quota_key="consultations",
        quota_limit=1,
        period_unit=PeriodUnit.WEEK,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    _add_binding(
        db,
        plan_id=trial_id,
        feature_id=features["natal_chart_long"].id,
        access_mode=AccessMode.QUOTA,
        variant_code="single_astrologer",
        quota_key="interpretations",
        quota_limit=1,
        period_unit=PeriodUnit.LIFETIME,
        period_value=1,
        reset_mode=ResetMode.LIFETIME,
    )
    _add_binding(
        db,
        plan_id=trial_id,
        feature_id=features["natal_chart_short"].id,
        access_mode=AccessMode.UNLIMITED,
    )

    basic_id = plans["basic"].id
    _add_binding(
        db,
        plan_id=basic_id,
        feature_id=features["astrologer_chat"].id,
        access_mode=AccessMode.QUOTA,
        quota_key="messages",
        quota_limit=5,
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    _add_binding(
        db,
        plan_id=basic_id,
        feature_id=features["thematic_consultation"].id,
        access_mode=AccessMode.QUOTA,
        quota_key="consultations",
        quota_limit=3,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    _add_binding(
        db,
        plan_id=basic_id,
        feature_id=features["natal_chart_long"].id,
        access_mode=AccessMode.QUOTA,
        variant_code="single_astrologer",
        quota_key="interpretations",
        quota_limit=1,
        period_unit=PeriodUnit.LIFETIME,
        period_value=1,
        reset_mode=ResetMode.LIFETIME,
    )
    _add_binding(
        db,
        plan_id=basic_id,
        feature_id=features["natal_chart_short"].id,
        access_mode=AccessMode.UNLIMITED,
    )

    premium_id = plans["premium"].id
    _add_binding(
        db,
        plan_id=premium_id,
        feature_id=features["astrologer_chat"].id,
        access_mode=AccessMode.QUOTA,
        quota_key="messages",
        quota_limit=2000,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    _add_binding(
        db,
        plan_id=premium_id,
        feature_id=features["thematic_consultation"].id,
        access_mode=AccessMode.UNLIMITED,
    )
    _add_binding(
        db,
        plan_id=premium_id,
        feature_id=features["natal_chart_long"].id,
        access_mode=AccessMode.QUOTA,
        variant_code="multi_astrologer",
        quota_key="interpretations",
        quota_limit=5,
        period_unit=PeriodUnit.LIFETIME,
        period_value=1,
        reset_mode=ResetMode.LIFETIME,
    )
    _add_binding(
        db,
        plan_id=premium_id,
        feature_id=features["natal_chart_short"].id,
        access_mode=AccessMode.UNLIMITED,
    )

    db.commit()


def _create_user(db_session: Session, email: str) -> UserModel:
    user = UserModel(
        email=email,
        password_hash="fake_hash",
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _call_endpoint_for_plan(db_session: Session, user_id: int, plan_code: str):
    with pytest.MonkeyPatch().context() as monkeypatch:
        monkeypatch.setattr(
            BillingService,
            "get_subscription_status",
            lambda *args, **kwargs: _subscription(plan_code),
        )
        app.dependency_overrides[require_authenticated_user] = _override_auth(user_id=user_id)
        app.dependency_overrides[get_db_session] = lambda: db_session
        response = client.get("/v1/entitlements/me")
    app.dependency_overrides.clear()
    return response


def test_trial_user_entitlements(db_session: Session):
    """
    Vérifie les entitlements d'un utilisateur trial d'après le seed canonique :
    - astrologer_chat: disabled
    - natal_chart_long: quota 1/lifetime
    - thematic_consultation: quota 1/week
    - natal_chart_short: unlimited
    """
    seed_canonical_plans(db_session)
    user = _create_user(db_session, "trial@example.com")

    response = _call_endpoint_for_plan(db_session, user.id, "trial")
    assert response.status_code == 200

    payload = response.json()
    features = payload["data"]["features"]
    assert {feature["feature_code"] for feature in features} == FEATURE_CODES
    assert payload["meta"]["request_id"]

    thematic = next(f for f in features if f["feature_code"] == "thematic_consultation")
    assert thematic["access_mode"] == "quota"
    assert thematic["final_access"] is True
    assert thematic["usage_states"][0]["quota_limit"] == 1
    assert thematic["usage_states"][0]["period_unit"] == "week"
    assert thematic["usage_states"][0]["reset_mode"] == "calendar"
    assert thematic["usage_states"][0]["window_end"] is not None

    ncl = next(f for f in features if f["feature_code"] == "natal_chart_long")
    assert ncl["access_mode"] == "quota"
    assert ncl["variant_code"] == "single_astrologer"
    assert ncl["usage_states"][0]["quota_limit"] == 1
    assert ncl["usage_states"][0]["reset_mode"] == "lifetime"
    assert ncl["usage_states"][0]["window_end"] is None

    chat = next(f for f in features if f["feature_code"] == "astrologer_chat")
    assert chat["final_access"] is False
    assert chat["reason"] == "disabled_by_plan"

    short = next(f for f in features if f["feature_code"] == "natal_chart_short")
    assert short["access_mode"] == "unlimited"
    assert short["final_access"] is True


def test_basic_user_entitlements(db_session: Session):
    seed_canonical_plans(db_session)
    user = _create_user(db_session, "basic@example.com")

    response = _call_endpoint_for_plan(db_session, user.id, "basic")
    assert response.status_code == 200

    features = response.json()["data"]["features"]
    assert {feature["feature_code"] for feature in features} == FEATURE_CODES

    chat = next(f for f in features if f["feature_code"] == "astrologer_chat")
    assert chat["access_mode"] == "quota"
    assert chat["final_access"] is True
    assert chat["usage_states"][0]["quota_limit"] == 5
    assert chat["usage_states"][0]["period_unit"] == "day"
    assert chat["usage_states"][0]["reset_mode"] == "calendar"
    assert chat["usage_states"][0]["remaining"] == 5
    assert chat["usage_states"][0]["window_end"] is not None

    ncl = next(f for f in features if f["feature_code"] == "natal_chart_long")
    assert ncl["variant_code"] == "single_astrologer"
    assert ncl["usage_states"][0]["quota_limit"] == 1
    assert ncl["usage_states"][0]["window_end"] is None


def test_premium_user_entitlements(db_session: Session):
    seed_canonical_plans(db_session)
    user = _create_user(db_session, "premium@example.com")

    response = _call_endpoint_for_plan(db_session, user.id, "premium")
    assert response.status_code == 200

    features = response.json()["data"]["features"]
    assert {feature["feature_code"] for feature in features} == FEATURE_CODES

    chat = next(f for f in features if f["feature_code"] == "astrologer_chat")
    assert chat["access_mode"] == "quota"
    assert chat["final_access"] is True
    assert chat["usage_states"][0]["quota_limit"] == 2000
    assert chat["usage_states"][0]["period_unit"] == "month"
    assert chat["usage_states"][0]["reset_mode"] == "calendar"
    assert chat["usage_states"][0]["window_end"] is not None

    ncl = next(f for f in features if f["feature_code"] == "natal_chart_long")
    assert ncl["variant_code"] == "multi_astrologer"
    assert ncl["usage_states"][0]["quota_limit"] == 5
    assert ncl["usage_states"][0]["window_end"] is None


def test_no_quota_consumed(db_session: Session):
    """Vérifie que l'appel à l'endpoint ne consomme aucun quota."""
    seed_canonical_plans(db_session)
    user = _create_user(db_session, "consume_test@example.com")

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

    response = _call_endpoint_for_plan(db_session, user.id, "trial")
    assert response.status_code == 200
    db_session.refresh(counter)
    assert counter.used_count == 0

    response = _call_endpoint_for_plan(db_session, user.id, "trial")
    assert response.status_code == 200
    db_session.refresh(counter)
    assert counter.used_count == 0


def test_basic_user_chat_usage_states_populated(db_session: Session):
    """AC: 11 - user basic avec consommation -> usage_states[0].remaining reflète la réalité."""
    seed_canonical_plans(db_session)
    user = _create_user(db_session, "basic_consume@example.com")

    # Créer un compteur avec 2 messages consommés
    window_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    db_session.add(FeatureUsageCounterModel(
        user_id=user.id,
        feature_code="astrologer_chat",
        quota_key="messages",
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        window_start=window_start,
        window_end=window_start + timedelta(days=1),
        used_count=2,
    ))
    db_session.commit()

    response = _call_endpoint_for_plan(db_session, user.id, "basic")
    assert response.status_code == 200
    chat = next(f for f in response.json()["data"]["features"] if f["feature_code"] == "astrologer_chat")
    assert chat["usage_states"][0]["used"] == 2
    assert chat["usage_states"][0]["remaining"] == 3
    assert chat["usage_states"][0]["window_end"] is not None


def test_no_legacy_fallback_reason_in_response(db_session: Session):
    """AC: 11 - Vérifier qu'aucun plan connu ne retourne reason=legacy_fallback."""
    seed_canonical_plans(db_session)
    user = _create_user(db_session, "audit@example.com")

    for plan in ("trial", "basic", "premium"):
        response = _call_endpoint_for_plan(db_session, user.id, plan)
        assert response.status_code == 200
        features = response.json()["data"]["features"]
        for f in features:
            assert f["reason"] != "legacy_fallback", f"Plan {plan} feature {f['feature_code']} returned legacy_fallback"
