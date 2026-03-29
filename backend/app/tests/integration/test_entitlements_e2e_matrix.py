from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.base import Base
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.main import app
from app.services.billing_service import BillingPlanData, BillingService, SubscriptionStatusData
from app.services.quota_window_resolver import QuotaWindowResolver

CLIENT = TestClient(app)
FEATURE_CODES = (
    "natal_chart_short",
    "natal_chart_long",
    "astrologer_chat",
    "thematic_consultation",
)
NORMALIZED_DENIAL_REASONS = {
    "binding_disabled",
    "feature_not_in_plan",
    "billing_inactive",
    "quota_exhausted",
}


@dataclass(frozen=True)
class ExpectedQuota:
    quota_key: str
    quota_limit: int
    period_unit: str
    period_value: int
    reset_mode: str


@dataclass(frozen=True)
class ExpectedFeature:
    granted: bool
    reason_code: str
    access_mode: str | None
    quota_limit: int | None
    variant_code: str | None
    quota: ExpectedQuota | None = None


EXPECTED_MATRIX: dict[str, dict[str, ExpectedFeature]] = {
    "none": {
        feature_code: ExpectedFeature(
            granted=False,
            reason_code="feature_not_in_plan",
            access_mode=None,
            quota_limit=None,
            variant_code=None,
        )
        for feature_code in FEATURE_CODES
    },
    "free": {
        "natal_chart_short": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="unlimited",
            quota_limit=None,
            variant_code=None,
        ),
        "natal_chart_long": ExpectedFeature(
            granted=False,
            reason_code="binding_disabled",
            access_mode="disabled",
            quota_limit=None,
            variant_code=None,
        ),
        "astrologer_chat": ExpectedFeature(
            granted=False,
            reason_code="binding_disabled",
            access_mode="disabled",
            quota_limit=None,
            variant_code=None,
        ),
        "thematic_consultation": ExpectedFeature(
            granted=False,
            reason_code="binding_disabled",
            access_mode="disabled",
            quota_limit=None,
            variant_code=None,
        ),
    },
    "trial": {
        "natal_chart_short": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="unlimited",
            quota_limit=None,
            variant_code=None,
        ),
        "natal_chart_long": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="quota",
            quota_limit=1,
            variant_code="single_astrologer",
            quota=ExpectedQuota(
                quota_key="interpretations",
                quota_limit=1,
                period_unit="lifetime",
                period_value=1,
                reset_mode="lifetime",
            ),
        ),
        "astrologer_chat": ExpectedFeature(
            granted=False,
            reason_code="binding_disabled",
            access_mode="disabled",
            quota_limit=None,
            variant_code=None,
        ),
        "thematic_consultation": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="quota",
            quota_limit=1,
            variant_code=None,
            quota=ExpectedQuota(
                quota_key="consultations",
                quota_limit=1,
                period_unit="week",
                period_value=1,
                reset_mode="calendar",
            ),
        ),
    },
    "basic": {
        "natal_chart_short": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="unlimited",
            quota_limit=None,
            variant_code=None,
        ),
        "natal_chart_long": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="quota",
            quota_limit=1,
            variant_code="single_astrologer",
            quota=ExpectedQuota(
                quota_key="interpretations",
                quota_limit=1,
                period_unit="lifetime",
                period_value=1,
                reset_mode="lifetime",
            ),
        ),
        "astrologer_chat": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="quota",
            quota_limit=5,
            variant_code=None,
            quota=ExpectedQuota(
                quota_key="messages",
                quota_limit=5,
                period_unit="day",
                period_value=1,
                reset_mode="calendar",
            ),
        ),
        "thematic_consultation": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="quota",
            quota_limit=1,
            variant_code=None,
            quota=ExpectedQuota(
                quota_key="consultations",
                quota_limit=1,
                period_unit="week",
                period_value=1,
                reset_mode="calendar",
            ),
        ),
    },
    "premium": {
        "natal_chart_short": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="unlimited",
            quota_limit=None,
            variant_code=None,
        ),
        "natal_chart_long": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="quota",
            quota_limit=5,
            variant_code="multi_astrologer",
            quota=ExpectedQuota(
                quota_key="interpretations",
                quota_limit=5,
                period_unit="lifetime",
                period_value=1,
                reset_mode="lifetime",
            ),
        ),
        "astrologer_chat": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="quota",
            quota_limit=2000,
            variant_code=None,
            quota=ExpectedQuota(
                quota_key="messages",
                quota_limit=2000,
                period_unit="month",
                period_value=1,
                reset_mode="calendar",
            ),
        ),
        "thematic_consultation": ExpectedFeature(
            granted=True,
            reason_code="granted",
            access_mode="quota",
            quota_limit=2,
            variant_code=None,
            quota=ExpectedQuota(
                quota_key="consultations",
                quota_limit=2,
                period_unit="day",
                period_value=1,
                reset_mode="calendar",
            ),
        ),
    },
}


def _override_auth(user_id: int, role: str = "user"):
    def _override() -> AuthenticatedUser:
        return AuthenticatedUser(
            id=user_id,
            role=role,
            email=f"test_{user_id}@example.com",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    return _override


def _subscription(plan_code: str, status: str = "active") -> SubscriptionStatusData:
    plan = None
    if plan_code != "none":
        plan = BillingPlanData(
            code=plan_code,
            display_name=plan_code.title(),
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=0,
            is_active=True,
        )

    return SubscriptionStatusData(
        status=status,
        plan=plan,
        failure_reason=None,
        updated_at=datetime.now(timezone.utc),
    )


def _add_binding(
    db: Session,
    *,
    plan_id: int,
    feature_id: int,
    access_mode: AccessMode,
    is_enabled: bool = True,
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
        is_enabled=is_enabled,
        variant_code=variant_code,
    )
    db.add(binding)
    db.flush()

    if access_mode != AccessMode.QUOTA or not is_enabled:
        return

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


def _seed_canonical_matrix(db: Session) -> None:
    plans = {
        code: PlanCatalogModel(
            plan_code=code,
            plan_name=f"{code.title()} Plan",
            audience=Audience.B2C,
        )
        for code in ("free", "trial", "basic", "premium")
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

    for plan_code, expected_features in EXPECTED_MATRIX.items():
        if plan_code == "none":
            continue

        plan_id = plans[plan_code].id
        for feature_code, expected in expected_features.items():
            feature_id = features[feature_code].id
            quota = expected.quota
            _add_binding(
                db,
                plan_id=plan_id,
                feature_id=feature_id,
                access_mode=AccessMode(expected.access_mode)
                if expected.access_mode is not None
                else AccessMode.DISABLED,
                is_enabled=expected.reason_code != "binding_disabled",
                variant_code=expected.variant_code,
                quota_key=quota.quota_key if quota else None,
                quota_limit=quota.quota_limit if quota else None,
                period_unit=PeriodUnit(quota.period_unit) if quota else None,
                period_value=quota.period_value if quota else None,
                reset_mode=ResetMode(quota.reset_mode) if quota else None,
            )

    db.commit()


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    _seed_canonical_matrix(db)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def _create_user(db: Session) -> UserModel:
    user = UserModel(
        email=f"user_{datetime.now().timestamp()}@example.com",
        password_hash="hash",
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_usage_counter(
    db: Session,
    *,
    user_id: int,
    feature_code: str,
    quota: ExpectedQuota,
    used_count: int,
) -> None:
    window = QuotaWindowResolver.compute_window(
        quota.period_unit,
        quota.period_value,
        quota.reset_mode,
        datetime.now(timezone.utc),
    )
    db.add(
        FeatureUsageCounterModel(
            user_id=user_id,
            feature_code=feature_code,
            quota_key=quota.quota_key,
            period_unit=PeriodUnit(quota.period_unit),
            period_value=quota.period_value,
            reset_mode=ResetMode(quota.reset_mode),
            window_start=window.window_start,
            window_end=window.window_end,
            used_count=used_count,
        )
    )
    db.commit()


def _client_get_entitlements(
    *,
    user_id: int,
    db: Session,
    plan_code: str,
    billing_status: str = "active",
):
    app.dependency_overrides[require_authenticated_user] = _override_auth(user_id=user_id)
    app.dependency_overrides[get_db_session] = lambda: db
    with pytest.MonkeyPatch().context() as monkeypatch:
        monkeypatch.setattr(
            BillingService,
            "get_subscription_status_readonly",
            lambda *args, **kwargs: _subscription(plan_code, billing_status),
        )
        response = CLIENT.get("/v1/entitlements/me")
    app.dependency_overrides.clear()
    return response


def _get_feature(response, feature_code: str) -> dict[str, Any]:
    features = response.json()["data"]["features"]
    return next(feature for feature in features if feature["feature_code"] == feature_code)


def _assert_feature_matches_expected(
    feature_payload: dict[str, Any],
    expected: ExpectedFeature,
) -> None:
    assert feature_payload["granted"] is expected.granted
    assert feature_payload["reason_code"] == expected.reason_code
    assert feature_payload["access_mode"] == expected.access_mode
    assert feature_payload["quota_limit"] == expected.quota_limit
    assert feature_payload["variant_code"] == expected.variant_code

    if expected.quota is None:
        assert feature_payload["quota_remaining"] is None
        assert feature_payload["usage_states"] == []
        return

    usage_state = feature_payload["usage_states"][0]
    assert usage_state["quota_key"] == expected.quota.quota_key
    assert usage_state["quota_limit"] == expected.quota.quota_limit
    assert usage_state["period_unit"] == expected.quota.period_unit
    assert usage_state["period_value"] == expected.quota.period_value
    assert usage_state["reset_mode"] == expected.quota.reset_mode
    assert feature_payload["quota_remaining"] == usage_state["remaining"]

    if expected.granted:
        assert feature_payload["quota_remaining"] == expected.quota.quota_limit


def _assert_plan_snapshot(
    response,
    *,
    expected_plan_code: str,
    expected_billing_status: str,
    expected_features: dict[str, ExpectedFeature],
) -> None:
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["plan_code"] == expected_plan_code
    assert payload["billing_status"] == expected_billing_status
    assert {feature["feature_code"] for feature in payload["features"]} == set(FEATURE_CODES)

    for feature_code, expected in expected_features.items():
        _assert_feature_matches_expected(_get_feature(response, feature_code), expected)


class TestNoSubscription:
    def test_all_features_are_not_in_plan(self, db_session: Session) -> None:
        user = _create_user(db_session)
        response = _client_get_entitlements(
            user_id=user.id,
            db=db_session,
            plan_code="none",
            billing_status="none",
        )

        _assert_plan_snapshot(
            response,
            expected_plan_code="none",
            expected_billing_status="none",
            expected_features=EXPECTED_MATRIX["none"],
        )


class TestFreePlan:
    def test_free_plan_matrix(self, db_session: Session) -> None:
        user = _create_user(db_session)
        response = _client_get_entitlements(user_id=user.id, db=db_session, plan_code="free")

        _assert_plan_snapshot(
            response,
            expected_plan_code="free",
            expected_billing_status="active",
            expected_features=EXPECTED_MATRIX["free"],
        )


class TestTrialPlan:
    def test_trial_plan_matrix(self, db_session: Session) -> None:
        user = _create_user(db_session)
        response = _client_get_entitlements(
            user_id=user.id,
            db=db_session,
            plan_code="trial",
            billing_status="trialing",
        )

        _assert_plan_snapshot(
            response,
            expected_plan_code="trial",
            expected_billing_status="trialing",
            expected_features=EXPECTED_MATRIX["trial"],
        )


class TestBasicPlan:
    def test_basic_plan_matrix(self, db_session: Session) -> None:
        user = _create_user(db_session)
        response = _client_get_entitlements(user_id=user.id, db=db_session, plan_code="basic")

        _assert_plan_snapshot(
            response,
            expected_plan_code="basic",
            expected_billing_status="active",
            expected_features=EXPECTED_MATRIX["basic"],
        )


class TestPremiumPlan:
    def test_premium_plan_matrix(self, db_session: Session) -> None:
        user = _create_user(db_session)
        response = _client_get_entitlements(user_id=user.id, db=db_session, plan_code="premium")

        _assert_plan_snapshot(
            response,
            expected_plan_code="premium",
            expected_billing_status="active",
            expected_features=EXPECTED_MATRIX["premium"],
        )


class TestBillingInactiveScenario:
    def test_enabled_features_are_denied_when_billing_is_inactive(
        self,
        db_session: Session,
    ) -> None:
        user = _create_user(db_session)
        response = _client_get_entitlements(
            user_id=user.id,
            db=db_session,
            plan_code="premium",
            billing_status="past_due",
        )

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["plan_code"] == "premium"
        assert payload["billing_status"] == "past_due"

        for feature_code in FEATURE_CODES:
            feature = _get_feature(response, feature_code)
            if EXPECTED_MATRIX["premium"][feature_code].access_mode == "disabled":
                continue
            assert feature["granted"] is False
            assert feature["reason_code"] == "billing_inactive"


class TestFrontendContract:
    @pytest.mark.parametrize(
        ("plan_code", "billing_status"),
        [
            ("none", "none"),
            ("free", "active"),
            ("trial", "trialing"),
            ("basic", "active"),
            ("premium", "active"),
        ],
    )
    def test_snapshot_is_sufficient_for_frontend(
        self,
        db_session: Session,
        plan_code: str,
        billing_status: str,
    ) -> None:
        user = _create_user(db_session)
        response = _client_get_entitlements(
            user_id=user.id,
            db=db_session,
            plan_code=plan_code,
            billing_status=billing_status,
        )

        assert response.status_code == 200
        for feature in response.json()["data"]["features"]:
            if feature["granted"] is False:
                assert feature["reason_code"] in NORMALIZED_DENIAL_REASONS
                continue

            if feature["access_mode"] == "quota":
                assert feature["quota_remaining"] is not None
                assert feature["quota_limit"] is not None
                assert feature["usage_states"]
            elif feature["access_mode"] == "unlimited":
                assert feature["quota_remaining"] is None
                assert feature["quota_limit"] is None
                assert feature["usage_states"] == []

            if feature["variant_code"] is not None:
                assert feature["variant_code"] in {
                    "single_astrologer",
                    "multi_astrologer",
                }

    def test_quota_exhausted_stays_in_normalized_vocabulary(self, db_session: Session) -> None:
        user = _create_user(db_session)
        quota = EXPECTED_MATRIX["basic"]["astrologer_chat"].quota
        assert quota is not None
        _create_usage_counter(
            db_session,
            user_id=user.id,
            feature_code="astrologer_chat",
            quota=quota,
            used_count=quota.quota_limit,
        )

        response = _client_get_entitlements(user_id=user.id, db=db_session, plan_code="basic")
        feature = _get_feature(response, "astrologer_chat")

        assert feature["granted"] is False
        assert feature["reason_code"] == "quota_exhausted"
        assert feature["quota_limit"] == quota.quota_limit
        assert feature["quota_remaining"] == 0
        assert feature["usage_states"][0]["remaining"] == 0
