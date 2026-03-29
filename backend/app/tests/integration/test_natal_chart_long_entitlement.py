from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

import app.infra.db.models  # noqa: F401
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.schemas.natal_interpretation import (
    InterpretationMeta,
    NatalInterpretationData,
    NatalInterpretationResponse,
)
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
    SourceOrigin,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine, get_db_session
from app.llm_orchestration.schemas import AstroResponseV3
from app.main import app
from app.services.billing_service import BillingPlanData, BillingService, SubscriptionStatusData
from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService
from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)
from app.services.natal_chart_long_entitlement_gate import (
    NatalChartLongAccessDeniedError,
    NatalChartLongEntitlementResult,
    NatalChartLongQuotaExceededError,
)

client = TestClient(app)

COMPLETE_PAYLOAD = {"use_case_level": "complete", "locale": "fr-FR"}
SHORT_PAYLOAD = {"use_case_level": "short", "locale": "fr-FR"}
FEATURE_CODE = "natal_chart_long"


def _mock_resolver_snapshot(
    user_id: int,
    plan_code: str,
    granted: bool = True,
    reason_code: str = "granted",
    access_mode: AccessMode = AccessMode.QUOTA,
    variant_code: str | None = None,
    quota_limit: int | None = None,
    used: int = 0,
    period_unit: PeriodUnit | None = None,
    period_value: int = 1,
    reset_mode: ResetMode | None = None,
    window_end: datetime | None = None,
) -> EffectiveEntitlementsSnapshot:
    usage_states = []
    if access_mode == AccessMode.QUOTA and quota_limit is not None:
        usage_states = [
            UsageState(
                feature_code=FEATURE_CODE,
                quota_key="interpretations",
                quota_limit=quota_limit,
                used=used,
                remaining=max(0, quota_limit - used),
                exhausted=used >= quota_limit,
                period_unit=period_unit.value if period_unit else None,
                period_value=period_value,
                reset_mode=reset_mode.value if reset_mode else None,
                window_start=None,
                window_end=window_end,
            )
        ]

    access = EffectiveFeatureAccess(
        granted=granted,
        reason_code=reason_code,
        access_mode=access_mode.value if access_mode else None,
        variant_code=variant_code,
        quota_limit=quota_limit,
        quota_used=used,
        quota_remaining=max(0, quota_limit - used) if quota_limit is not None else None,
        period_unit=period_unit.value if period_unit else None,
        period_value=period_value,
        reset_mode=reset_mode.value if reset_mode else None,
        usage_states=usage_states,
    )
    return EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=user_id,
        plan_code=plan_code,
        billing_status="active",
        entitlements={FEATURE_CODE: access},
    )


def _dynamic_snapshot(db: Session, *, app_user_id: int) -> EffectiveEntitlementsSnapshot:
    from app.infra.db.models.product_entitlements import (
        FeatureUsageCounterModel,
        PlanCatalogModel,
        PlanFeatureBindingModel,
        PlanFeatureQuotaModel,
    )
    from sqlalchemy import select

    binding_stmt = (
        select(PlanFeatureBindingModel, PlanCatalogModel)
        .join(PlanCatalogModel, PlanFeatureBindingModel.plan_id == PlanCatalogModel.id)
        .limit(1)
    )
    row = db.execute(binding_stmt).first()
    if not row:
        return _mock_resolver_snapshot(
            user_id=app_user_id, plan_code="none", granted=False, reason_code="feature_not_in_plan"
        )

    binding, plan = row
    quota = db.scalar(
        select(PlanFeatureQuotaModel).where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
        )
    )

    counter = db.scalar(
        select(FeatureUsageCounterModel).where(
            FeatureUsageCounterModel.user_id == app_user_id,
            FeatureUsageCounterModel.feature_code == FEATURE_CODE,
        )
    )
    used = counter.used_count if counter else 0
    window_end = counter.window_end if counter else None
    if window_end and window_end.tzinfo is None:
        window_end = window_end.replace(tzinfo=timezone.utc)

    granted = binding.is_enabled and binding.access_mode != AccessMode.DISABLED
    reason_code = "granted" if granted else "binding_disabled"

    if granted and binding.access_mode == AccessMode.QUOTA and quota:
        if used >= quota.quota_limit:
            granted = False
            reason_code = "quota_exhausted"

    return _mock_resolver_snapshot(
        user_id=app_user_id,
        plan_code=plan.plan_code,
        granted=granted,
        reason_code=reason_code,
        access_mode=binding.access_mode,
        variant_code=binding.variant_code,
        quota_limit=quota.quota_limit if quota else None,
        used=used,
        period_unit=quota.period_unit if quota else None,
        reset_mode=quota.reset_mode if quota else None,
        window_end=window_end,
    )


def _override_auth() -> AuthenticatedUser:
    return AuthenticatedUser(
        id=42,
        role="user",
        email="test-user@example.com",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _make_usage_state(used=1, limit=1, remaining=0):
    return UsageState(
        feature_code="natal_chart_long",
        quota_key="interpretations",
        quota_limit=limit,
        used=used,
        remaining=remaining,
        exhausted=used >= limit,
        period_unit="lifetime",
        period_value=1,
        reset_mode="lifetime",
        window_start=None,
        window_end=None,  # lifetime → pas de window_end
    )


def _make_valid_interpretation_response(level="complete"):
    return NatalInterpretationResponse(
        data=NatalInterpretationData(
            chart_id="test_chart",
            use_case="natal_interpretation",
            interpretation=AstroResponseV3(
                title="Test Title",
                summary="A" * 901,
                sections=[
                    {"key": "inner_life", "heading": f"Heading {i}", "content": "B" * 281}
                    for i in range(5)
                ],
                highlights=["H1", "H2", "H3", "H4", "H5"],
                advice=["A1", "A2", "A3", "A4", "A5"],
                evidence=[],
            ),
            meta=InterpretationMeta(
                level=level, use_case="natal_interpretation", validation_status="valid"
            ),
        ),
        disclaimers=[],
    )


def _reset_database() -> None:
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserModel))
        db.commit()


def _auth_headers(email: str) -> dict[str, str]:
    register = client.post(
        "/v1/auth/register",
        json={"email": email, "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _subscription_status(
    plan_code: str | None, *, status: str = "active"
) -> SubscriptionStatusData:
    plan = None
    if plan_code is not None:
        plan = BillingPlanData(
            code=plan_code,
            display_name=plan_code.title(),
            monthly_price_cents=500,
            currency="EUR",
            daily_message_limit=0,
            is_active=True,
        )
    return SubscriptionStatusData(
        status=status,
        plan=plan,
        failure_reason=None,
        updated_at=None,
    )


def _seed_natal_chart_long_binding(
    *,
    plan_code: str,
    access_mode: AccessMode,
    variant_code: str,
    quota_limit: int | None = None,
) -> None:
    with SessionLocal() as db:
        plan = PlanCatalogModel(
            plan_code=plan_code,
            plan_name=plan_code.title(),
            audience=Audience.B2C,
            source_type="manual",
        )
        feature = FeatureCatalogModel(
            feature_code=FEATURE_CODE,
            feature_name="Natal Chart Long",
            is_metered=True,
        )
        db.add_all([plan, feature])
        db.flush()

        binding = PlanFeatureBindingModel(
            plan_id=plan.id,
            feature_id=feature.id,
            is_enabled=True,
            access_mode=access_mode,
            variant_code=variant_code,
            source_origin=SourceOrigin.MANUAL,
        )
        db.add(binding)
        db.flush()

        if access_mode == AccessMode.QUOTA:
            assert quota_limit is not None
            db.add(
                PlanFeatureQuotaModel(
                    plan_feature_binding_id=binding.id,
                    quota_key="interpretations",
                    quota_limit=quota_limit,
                    period_unit=PeriodUnit.LIFETIME,
                    period_value=1,
                    reset_mode=ResetMode.LIFETIME,
                    source_origin=SourceOrigin.MANUAL,
                )
            )

        db.commit()


def _get_user_id(email: str) -> int:
    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == email))
        assert user is not None
        return user.id


def _get_counter(user_id: int) -> FeatureUsageCounterModel | None:
    with SessionLocal() as db:
        return db.scalar(
            select(FeatureUsageCounterModel).where(
                FeatureUsageCounterModel.user_id == user_id,
                FeatureUsageCounterModel.feature_code == FEATURE_CODE,
            )
        )


def _patch_interpretation_dependencies(side_effect=None):
    return (
        patch(
            "app.services.user_natal_chart_service.UserNatalChartService.get_latest_for_user",
            return_value=MagicMock(chart_id="test_chart", result={}),
        ),
        patch(
            "app.services.user_birth_profile_service.UserBirthProfileService.get_for_user",
            return_value=MagicMock(),
        ),
        patch(
            "app.services.natal_interpretation_service_v2.NatalInterpretationServiceV2.interpret",
            new=AsyncMock(
                side_effect=side_effect,
                return_value=None
                if side_effect
                else _make_valid_interpretation_response(level="complete"),
            ),
        ),
    )


@pytest.fixture(autouse=True)
def clear_test_state():
    yield
    app.dependency_overrides.clear()
    BillingService.reset_subscription_status_cache()


@pytest.fixture
def mock_user_and_chart():
    app.dependency_overrides[require_authenticated_user] = _override_auth
    with (
        patch(
            "app.services.user_natal_chart_service.UserNatalChartService.get_latest_for_user"
        ) as mock_chart,
        patch(
            "app.services.user_birth_profile_service.UserBirthProfileService.get_for_user"
        ) as mock_profile,
    ):
        chart_obj = MagicMock()
        chart_obj.chart_id = "test_chart"
        chart_obj.result = {}
        mock_chart.return_value = chart_obj

        profile_obj = MagicMock()
        mock_profile.return_value = profile_obj

        yield mock_chart, mock_profile
    app.dependency_overrides.pop(require_authenticated_user, None)
    app.dependency_overrides.pop(get_db_session, None)


def test_short_level_bypasses_gate(mock_user_and_chart):
    """use_case_level=short → gate non appelé, entitlement_info=None."""
    with (
        patch(
            "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume"
        ) as mock_gate,
        patch(
            "app.services.natal_interpretation_service_v2.NatalInterpretationServiceV2.interpret"
        ) as mock_interpret,
    ):
        mock_interpret.return_value = _make_valid_interpretation_response(level="short")

        response = client.post("/v1/natal/interpretation", json=SHORT_PAYLOAD)

    assert response.status_code == 200
    mock_gate.assert_not_called()
    assert response.json().get("entitlement_info") is None


def test_complete_canonical_quota_ok(mock_user_and_chart):
    usage_state = _make_usage_state(used=1, limit=1, remaining=0)
    result = NatalChartLongEntitlementResult(
        path="canonical_quota", variant_code="single_astrologer", usage_states=[usage_state]
    )

    with (
        patch(
            "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
            return_value=result,
        ),
        patch(
            "app.services.natal_interpretation_service_v2.NatalInterpretationServiceV2.interpret"
        ) as mock_interpret,
    ):
        mock_interpret.return_value = _make_valid_interpretation_response(level="complete")

        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)

    assert response.status_code == 200
    data = response.json()
    assert data["entitlement_info"]["remaining"] == 0
    assert data["entitlement_info"]["limit"] == 1
    assert data["entitlement_info"]["variant_code"] == "single_astrologer"


def test_complete_canonical_unlimited_ok(mock_user_and_chart):
    result = NatalChartLongEntitlementResult(
        path="canonical_unlimited", variant_code="multi_astrologer", usage_states=[]
    )

    with (
        patch(
            "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
            return_value=result,
        ),
        patch(
            "app.services.natal_interpretation_service_v2.NatalInterpretationServiceV2.interpret"
        ) as mock_interpret,
    ):
        mock_interpret.return_value = _make_valid_interpretation_response(level="complete")

        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)

    assert response.status_code == 200
    data = response.json()
    assert data["entitlement_info"]["remaining"] is None
    assert data["entitlement_info"]["variant_code"] == "multi_astrologer"


def test_complete_no_plan_rejected(mock_user_and_chart):
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongAccessDeniedError(
            reason="no_plan", billing_status="none", plan_code=""
        ),
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "natal_chart_long_access_denied"
    assert response.json()["error"]["details"]["reason"] == "no_plan"


def test_complete_quota_exhausted_rejected(mock_user_and_chart):
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongQuotaExceededError(
            quota_key="interpretations", used=1, limit=1, window_end=None
        ),
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "natal_chart_long_quota_exceeded"
    assert response.json()["error"]["details"]["window_end"] is None


def test_complete_disabled_binding_returns_disabled_by_plan(mock_user_and_chart):
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongAccessDeniedError(
            reason="disabled_by_plan", billing_status="active", plan_code="free"
        ),
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)

    assert response.status_code == 403
    assert response.json()["error"]["details"]["reason"] == "disabled_by_plan"


def test_complete_no_canonical_binding_returns_no_binding(mock_user_and_chart):
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongAccessDeniedError(
            reason="canonical_no_binding", billing_status="active", plan_code="basic"
        ),
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)

    assert response.status_code == 403
    assert response.json()["error"]["details"]["reason"] == "canonical_no_binding"


def test_complete_rolls_back_on_access_denied(mock_user_and_chart, db_session):
    from app.infra.db.session import get_db_session

    app.dependency_overrides[get_db_session] = lambda: db_session

    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongAccessDeniedError(
            reason="no_plan", billing_status="none", plan_code=""
        ),
    ):
        with patch.object(db_session, "rollback") as mock_rollback:
            response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)

    assert response.status_code == 403
    mock_rollback.assert_called()


def test_trial_quota_1_per_lifetime() -> None:
    _reset_database()
    email = "trial-lifetime@example.com"
    headers = _auth_headers(email)
    user_id = _get_user_id(email)
    _seed_natal_chart_long_binding(
        plan_code="trial",
        access_mode=AccessMode.QUOTA,
        variant_code="single_astrologer",
        quota_limit=1,
    )

    chart_patch, profile_patch, interpret_patch = _patch_interpretation_dependencies()
    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),

        chart_patch,
        profile_patch,
        interpret_patch,
    ):
        first = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD, headers=headers)
        second = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD, headers=headers)

    counter = _get_counter(user_id)

    assert first.status_code == 200
    assert first.json()["entitlement_info"]["variant_code"] == "single_astrologer"
    assert first.json()["entitlement_info"]["remaining"] == 0
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "natal_chart_long_quota_exceeded"
    assert second.json()["error"]["details"]["limit"] == 1
    assert second.json()["error"]["details"]["window_end"] is None
    assert counter is not None
    assert counter.used_count == 1


def test_premium_quota_5_per_lifetime() -> None:
    _reset_database()
    email = "premium-lifetime@example.com"
    headers = _auth_headers(email)
    user_id = _get_user_id(email)
    _seed_natal_chart_long_binding(
        plan_code="premium",
        access_mode=AccessMode.QUOTA,
        variant_code="multi_astrologer",
        quota_limit=5,
    )

    chart_patch, profile_patch, interpret_patch = _patch_interpretation_dependencies()
    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),

        chart_patch,
        profile_patch,
        interpret_patch,
    ):
        responses = [
            client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD, headers=headers)
            for _ in range(6)
        ]

    counter = _get_counter(user_id)

    assert all(response.status_code == 200 for response in responses[:5])
    assert responses[4].json()["entitlement_info"]["variant_code"] == "multi_astrologer"
    assert responses[4].json()["entitlement_info"]["remaining"] == 0
    assert responses[5].status_code == 429
    assert responses[5].json()["error"]["details"]["limit"] == 5
    assert responses[5].json()["error"]["details"]["window_end"] is None
    assert counter is not None
    assert counter.used_count == 5


@pytest.mark.parametrize(
    ("plan_code", "variant_code"),
    [("trial", "single_astrologer"), ("premium", "multi_astrologer")],
)
def test_variant_code_in_response(plan_code: str, variant_code: str) -> None:
    _reset_database()
    email = f"{plan_code}-variant@example.com"
    headers = _auth_headers(email)
    _seed_natal_chart_long_binding(
        plan_code=plan_code,
        access_mode=AccessMode.UNLIMITED,
        variant_code=variant_code,
    )

    chart_patch, profile_patch, interpret_patch = _patch_interpretation_dependencies()
    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),

        chart_patch,
        profile_patch,
        interpret_patch,
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD, headers=headers)

    assert response.status_code == 200
    assert response.json()["entitlement_info"]["variant_code"] == variant_code


def test_complete_consumes_before_cached_response() -> None:
    _reset_database()
    email = "cached-response@example.com"
    headers = _auth_headers(email)
    user_id = _get_user_id(email)
    _seed_natal_chart_long_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        variant_code="single_astrologer",
        quota_limit=1,
    )

    async def _assert_counter_before_interpret(**kwargs):
        db = kwargs["db"]
        counter = db.scalar(
            select(FeatureUsageCounterModel).where(
                FeatureUsageCounterModel.user_id == user_id,
                FeatureUsageCounterModel.feature_code == FEATURE_CODE,
            )
        )
        assert counter is not None
        assert counter.used_count == 1
        response = _make_valid_interpretation_response(level="complete")
        response.data.meta.cached = True
        return response

    chart_patch, profile_patch, interpret_patch = _patch_interpretation_dependencies(
        side_effect=_assert_counter_before_interpret
    )
    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),

        chart_patch,
        profile_patch,
        interpret_patch,
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD, headers=headers)

    counter = _get_counter(user_id)

    assert response.status_code == 200
    assert response.json()["data"]["meta"]["cached"] is True
    assert counter is not None
    assert counter.used_count == 1
