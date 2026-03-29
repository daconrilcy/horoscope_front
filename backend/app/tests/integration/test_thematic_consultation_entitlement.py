from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

import app.infra.db.models  # noqa: F401
from app.api.v1.schemas.consultation import (
    ConsultationGenerateData,
    ConsultationSection,
    ConsultationStatus,
    PrecisionLevel,
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
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine, get_db_session
from app.main import app
from app.services.billing_service import BillingPlanData, BillingService, SubscriptionStatusData
from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService
from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)
from app.services.thematic_consultation_entitlement_gate import ConsultationQuotaExceededError

UTC = timezone.utc
FEATURE_CODE = "thematic_consultation"
CLIENT = TestClient(app)


def _mock_resolver_snapshot(
    user_id: int,
    plan_code: str,
    granted: bool = True,
    reason_code: str = "granted",
    access_mode: AccessMode = AccessMode.QUOTA,
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
                quota_key="consultations",
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
        variant_code=None,
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


def _get_user_id(email: str) -> int:
    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email=email).one()
        return user.id


def _dynamic_snapshot(db: Session, *, app_user_id: int) -> EffectiveEntitlementsSnapshot:
    # Simuler ce que le vrai resolver ferait mais en se basant sur ce qu'on a seedé
    from sqlalchemy import select

    from app.infra.db.models.product_entitlements import (
        FeatureUsageCounterModel,
        PlanCatalogModel,
        PlanFeatureBindingModel,
        PlanFeatureQuotaModel,
    )

    # On cherche le binding seedé (on suppose un seul plan pour le test)
    # On fait un join manuel car la relation n'est peut-être pas chargée
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
        quota_limit=quota.quota_limit if quota else None,
        used=used,
        period_unit=quota.period_unit if quota else None,
        reset_mode=quota.reset_mode if quota else None,
        window_end=window_end,
    )


def _reset_database() -> None:
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserBirthProfileModel))
        db.execute(delete(UserModel))
        db.commit()


def _auth_headers(email: str) -> dict[str, str]:
    register = CLIENT.post(
        "/v1/auth/register",
        json={"email": email, "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _seed_thematic_binding(
    *,
    plan_code: str,
    access_mode: AccessMode,
    is_enabled: bool = True,
    quota_limit: int | None = None,
    period_unit: PeriodUnit | None = None,
    period_value: int = 1,
    reset_mode: ResetMode | None = None,
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
            feature_name="Thematic Consultation",
            is_metered=True,
        )
        db.add_all([plan, feature])
        db.flush()

        binding = PlanFeatureBindingModel(
            plan_id=plan.id,
            feature_id=feature.id,
            is_enabled=is_enabled,
            access_mode=access_mode,
            source_origin=SourceOrigin.MANUAL,
        )
        db.add(binding)
        db.flush()

        if access_mode == AccessMode.QUOTA:
            assert quota_limit is not None
            assert period_unit is not None
            assert reset_mode is not None
            db.add(
                PlanFeatureQuotaModel(
                    plan_feature_binding_id=binding.id,
                    quota_key="consultations",
                    quota_limit=quota_limit,
                    period_unit=period_unit,
                    period_value=period_value,
                    reset_mode=reset_mode,
                    source_origin=SourceOrigin.MANUAL,
                )
            )

        db.commit()


def _subscription_status(
    *,
    plan_code: str | None,
    status: str = "active",
    daily_message_limit: int = 0,
) -> SubscriptionStatusData:
    plan = None
    if plan_code is not None:
        plan = BillingPlanData(
            code=plan_code,
            display_name=plan_code.title(),
            monthly_price_cents=500,
            currency="EUR",
            daily_message_limit=daily_message_limit,
            is_active=True,
        )
    return SubscriptionStatusData(
        status=status,
        plan=plan,
        failure_reason=None,
        updated_at=None,
    )


def _generate_payload() -> ConsultationGenerateData:
    return ConsultationGenerateData(
        consultation_id="consult_test",
        consultation_type="career",
        status=ConsultationStatus.nominal,
        precision_level=PrecisionLevel.high,
        fallback_mode=None,
        safeguard_issue=None,
        route_key="career_full",
        summary="Synthese",
        sections=[
            ConsultationSection(
                id="analysis",
                title="Lecture astrologique",
                content="Contenu",
                blocks=[],
            )
        ],
        chat_prefill="Prefill",
        metadata={"request_id": "test"},
    )


def _post_generate(headers: dict[str, str], question: str = "Quelle direction prendre ?"):
    return CLIENT.post(
        "/v1/consultations/generate",
        json={"consultation_type": "career", "question": question},
        headers=headers,
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()
    BillingService.reset_subscription_status_cache()


def test_generate_canonical_quota_ok() -> None:
    _reset_database()
    headers = _auth_headers("quota-ok@example.com")
    _seed_thematic_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        quota_limit=1,
        period_unit=PeriodUnit.WEEK,
        reset_mode=ResetMode.CALENDAR,
    )

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
        patch(
            "app.services.consultation_generation_service.ConsultationGenerationService.generate",
            return_value=_generate_payload(),
        ),
    ):
        response = _post_generate(headers)

    assert response.status_code == 200
    data = response.json()
    assert data["quota_info"]["remaining"] == 0
    assert data["quota_info"]["limit"] == 1

    with SessionLocal() as db:
        counters = db.query(FeatureUsageCounterModel).all()
        assert len(counters) == 1
        assert counters[0].feature_code == FEATURE_CODE
        assert counters[0].used_count == 1


def test_generate_canonical_quota_consumes_before_generation() -> None:
    _reset_database()
    headers = _auth_headers("quota-order@example.com")
    _seed_thematic_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        quota_limit=1,
        period_unit=PeriodUnit.WEEK,
        reset_mode=ResetMode.CALENDAR,
    )

    async def assert_counter_visible(
        db, user_id: int, request, request_id: str
    ) -> ConsultationGenerateData:
        counter = (
            db.query(FeatureUsageCounterModel)
            .filter_by(
                user_id=user_id,
                feature_code=FEATURE_CODE,
                quota_key="consultations",
            )
            .one()
        )
        assert counter.used_count == 1
        assert request_id != ""
        return _generate_payload()

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
        patch(
            "app.services.consultation_generation_service.ConsultationGenerationService.generate",
            side_effect=assert_counter_visible,
        ),
    ):
        response = _post_generate(headers)

    assert response.status_code == 200


def test_generate_canonical_unlimited_ok() -> None:
    _reset_database()
    headers = _auth_headers("unlimited@example.com")
    _seed_thematic_binding(
        plan_code="premium",
        access_mode=AccessMode.UNLIMITED,
    )

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
        patch(
            "app.services.consultation_generation_service.ConsultationGenerationService.generate",
            return_value=_generate_payload(),
        ),
    ):
        response = _post_generate(headers)

    assert response.status_code == 200
    data = response.json()
    assert data["quota_info"]["remaining"] is None
    assert data["quota_info"]["limit"] is None
    assert data["quota_info"]["window_end"] is None

    with SessionLocal() as db:
        assert db.query(FeatureUsageCounterModel).count() == 0


def test_generate_no_plan_rejected() -> None:
    _reset_database()
    headers = _auth_headers("no-plan@example.com")

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        side_effect=_dynamic_snapshot,
    ):
        response = _post_generate(headers)

    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "consultation_access_denied"
    assert data["error"]["details"]["reason"] == "no_plan"
    assert data["error"]["details"]["reason_code"] == "feature_not_in_plan"


def test_generate_quota_exhausted_rejected() -> None:
    _reset_database()
    headers = _auth_headers("quota-exhausted@example.com")
    _seed_thematic_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        quota_limit=1,
        period_unit=PeriodUnit.WEEK,
        reset_mode=ResetMode.CALENDAR,
    )

    fixed_now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=UTC)
    frozen_datetime = MagicMock(wraps=datetime)
    frozen_datetime.now.return_value = fixed_now

    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email="quota-exhausted@example.com").one()
        db.add(
            FeatureUsageCounterModel(
                user_id=user.id,
                feature_code=FEATURE_CODE,
                quota_key="consultations",
                period_unit=PeriodUnit.WEEK,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                window_start=datetime(2026, 3, 23, 0, 0, 0, tzinfo=UTC),
                window_end=datetime(2026, 3, 30, 0, 0, 0, tzinfo=UTC),
                used_count=1,
            )
        )
        db.commit()

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
        patch("app.services.entitlement_service.datetime", frozen_datetime),
    ):
        response = _post_generate(headers)

    assert response.status_code == 429
    data = response.json()
    assert data["error"]["code"] == "consultation_quota_exceeded"
    assert data["error"]["details"]["window_end"] == "2026-03-30T00:00:00+00:00"


def test_generate_disabled_binding_returns_disabled_by_plan() -> None:
    _reset_database()
    headers = _auth_headers("disabled@example.com")
    _seed_thematic_binding(
        plan_code="free",
        access_mode=AccessMode.DISABLED,
        is_enabled=False,
    )
    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
    ):
        response = _post_generate(headers)

    assert response.status_code == 403
    assert response.json()["error"]["details"]["reason"] == "disabled_by_plan"
    assert response.json()["error"]["details"]["reason_code"] == "binding_disabled"


def test_generate_no_canonical_binding_returns_no_binding() -> None:
    _reset_database()
    headers = _auth_headers("no-binding@example.com")

    with SessionLocal() as db:
        db.add(
            PlanCatalogModel(
                plan_code="basic",
                plan_name="Basic",
                audience=Audience.B2C,
                source_type="manual",
            )
        )
        db.add(
            FeatureCatalogModel(
                feature_code=FEATURE_CODE,
                feature_name="Thematic Consultation",
                is_metered=True,
            )
        )
        db.commit()
    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
    ):
        response = _post_generate(headers)

    assert response.status_code == 403
    assert response.json()["error"]["details"]["reason"] == "no_plan"
    assert response.json()["error"]["details"]["reason_code"] == "feature_not_in_plan"


def test_generate_rolls_back_partial_canonical_consumption() -> None:
    _reset_database()
    headers = _auth_headers("rollback-partial@example.com")

    db_session = SessionLocal()
    app.dependency_overrides[get_db_session] = lambda: db_session

    user = db_session.query(UserModel).filter_by(email="rollback-partial@example.com").one()

    def _partial_consume_then_fail(*_args, **_kwargs):
        db_session.add(
            FeatureUsageCounterModel(
                user_id=user.id,
                feature_code=FEATURE_CODE,
                quota_key="consultations",
                period_unit=PeriodUnit.WEEK,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                window_start=datetime(2026, 3, 23, 0, 0, 0, tzinfo=UTC),
                window_end=datetime(2026, 3, 30, 0, 0, 0, tzinfo=UTC),
                used_count=1,
            )
        )
        db_session.flush()
        raise ConsultationQuotaExceededError(
            quota_key="consultations",
            used=1,
            limit=1,
            window_end=datetime(2026, 3, 30, 0, 0, 0, tzinfo=UTC),
        )

    with (
        patch(
            "app.api.v1.routers.consultations.ThematicConsultationEntitlementGate.check_and_consume",
            side_effect=_partial_consume_then_fail,
        ),
        patch.object(db_session, "rollback", wraps=db_session.rollback) as mock_rollback,
    ):
        response = _post_generate(headers)

    persisted_counter = (
        db_session.query(FeatureUsageCounterModel)
        .filter_by(user_id=user.id, feature_code=FEATURE_CODE)
        .one_or_none()
    )

    app.dependency_overrides.pop(get_db_session, None)
    db_session.close()

    assert response.status_code == 429
    mock_rollback.assert_called_once()
    assert persisted_counter is None


def test_generate_access_denied_rolls_back() -> None:
    _reset_database()
    headers = _auth_headers("rollback-403@example.com")
    db_session = SessionLocal()
    app.dependency_overrides[get_db_session] = lambda: db_session

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
        patch.object(db_session, "rollback") as mock_rollback,
    ):
        response = _post_generate(headers)

    app.dependency_overrides.pop(get_db_session, None)
    db_session.close()

    assert response.status_code == 403
    mock_rollback.assert_called_once()


def test_generate_quota_exceeded_rolls_back() -> None:
    _reset_database()
    headers = _auth_headers("rollback-429@example.com")
    _seed_thematic_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        quota_limit=1,
        period_unit=PeriodUnit.WEEK,
        reset_mode=ResetMode.CALENDAR,
    )

    db_session = SessionLocal()
    app.dependency_overrides[get_db_session] = lambda: db_session
    fixed_now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=UTC)
    frozen_datetime = MagicMock(wraps=datetime)
    frozen_datetime.now.return_value = fixed_now

    user = db_session.query(UserModel).filter_by(email="rollback-429@example.com").one()
    db_session.add(
        FeatureUsageCounterModel(
            user_id=user.id,
            feature_code=FEATURE_CODE,
            quota_key="consultations",
            period_unit=PeriodUnit.WEEK,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
            window_start=datetime(2026, 3, 23, 0, 0, 0, tzinfo=UTC),
            window_end=datetime(2026, 3, 30, 0, 0, 0, tzinfo=UTC),
            used_count=1,
        )
    )
    db_session.commit()

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
        patch("app.services.entitlement_service.datetime", frozen_datetime),
        patch.object(db_session, "rollback") as mock_rollback,
    ):
        response = _post_generate(headers)

    app.dependency_overrides.pop(get_db_session, None)
    db_session.close()

    assert response.status_code == 429
    mock_rollback.assert_called_once()


def test_premium_quota_2_per_day() -> None:
    _reset_database()
    headers = _auth_headers("premium-day@example.com")
    _seed_thematic_binding(
        plan_code="premium",
        access_mode=AccessMode.QUOTA,
        quota_limit=2,
        period_unit=PeriodUnit.DAY,
        reset_mode=ResetMode.CALENDAR,
    )

    fixed_now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=UTC)
    frozen_datetime = MagicMock(wraps=datetime)
    frozen_datetime.now.return_value = fixed_now

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
        patch("app.services.entitlement_service.datetime", frozen_datetime),
        patch("app.services.quota_usage_service.datetime", frozen_datetime),
        patch(
            "app.services.consultation_generation_service.ConsultationGenerationService.generate",
            return_value=_generate_payload(),
        ),
    ):
        first = _post_generate(headers, "Q1")
        second = _post_generate(headers, "Q2")
        third = _post_generate(headers, "Q3")

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json()["error"]["details"]["limit"] == 2


def test_basic_quota_1_per_week() -> None:
    _reset_database()
    headers = _auth_headers("basic-week@example.com")
    _seed_thematic_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        quota_limit=1,
        period_unit=PeriodUnit.WEEK,
        reset_mode=ResetMode.CALENDAR,
    )

    fixed_now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=UTC)
    frozen_datetime = MagicMock(wraps=datetime)
    frozen_datetime.now.return_value = fixed_now

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            side_effect=_dynamic_snapshot,
        ),
        patch("app.services.entitlement_service.datetime", frozen_datetime),
        patch("app.services.quota_usage_service.datetime", frozen_datetime),
        patch(
            "app.services.consultation_generation_service.ConsultationGenerationService.generate",
            return_value=_generate_payload(),
        ),
    ):
        first = _post_generate(headers, "Semaine 1")
        second = _post_generate(headers, "Semaine 2")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["error"]["details"]["limit"] == 1
