from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_editorial_config import EnterpriseEditorialConfigModel
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
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.main import app
from app.services.auth_service import AuthService
from app.services.b2b.api_entitlement_gate import B2BApiEntitlementGate
from app.services.b2b.astrology_service import B2BAstrologyServiceError
from app.services.b2b.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)
from app.services.reference_data_service import ReferenceDataService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def _mock_b2b_snapshot(
    account_id: int,
    plan_code: str,
    granted: bool = True,
    reason_code: str = "granted",
    access_mode: AccessMode | None = AccessMode.QUOTA,
    quota_limit: int | None = None,
    used: int = 0,
    period_unit: PeriodUnit | None = None,
    reset_mode: ResetMode | None = None,
) -> EffectiveEntitlementsSnapshot:
    usage_states = []
    feature_code = B2BApiEntitlementGate.FEATURE_CODE
    if access_mode == AccessMode.QUOTA and quota_limit is not None:
        usage_states = [
            UsageState(
                feature_code=feature_code,
                quota_key=feature_code,
                quota_limit=quota_limit,
                used=used,
                remaining=max(0, quota_limit - used),
                exhausted=used >= quota_limit,
                period_unit=period_unit.value if period_unit else None,
                period_value=1,
                reset_mode=reset_mode.value if reset_mode else None,
                window_start=None,
                window_end=None,
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
        period_value=1,
        reset_mode=reset_mode.value if reset_mode else None,
        usage_states=usage_states,
    )
    return EffectiveEntitlementsSnapshot(
        subject_type="b2b_account",
        subject_id=account_id,
        plan_code=plan_code,
        billing_status="active",
        entitlements={feature_code: access},
    )


def _dynamic_b2b_snapshot(
    db: Session, *, enterprise_account_id: int
) -> EffectiveEntitlementsSnapshot:
    from app.services.b2b.canonical_plan_resolver import resolve_b2b_canonical_plan

    feature_code = B2BApiEntitlementGate.FEATURE_CODE
    canonical_plan = resolve_b2b_canonical_plan(db, enterprise_account_id)
    if not canonical_plan:
        return _mock_b2b_snapshot(
            account_id=enterprise_account_id,
            plan_code="none",
            granted=False,
            reason_code="b2b_no_canonical_plan",
        )

    binding_stmt = (
        select(PlanFeatureBindingModel)
        .join(FeatureCatalogModel, PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id)
        .where(
            PlanFeatureBindingModel.plan_id == canonical_plan.id,
            FeatureCatalogModel.feature_code == feature_code,
        )
    )
    binding = db.scalar(binding_stmt)
    if not binding:
        return _mock_b2b_snapshot(
            account_id=enterprise_account_id,
            plan_code=canonical_plan.plan_code,
            granted=False,
            reason_code="b2b_no_binding",
        )

    granted = binding.is_enabled and binding.access_mode != AccessMode.DISABLED
    reason_code = "granted" if granted else "binding_disabled"

    quota = db.scalar(
        select(PlanFeatureQuotaModel).where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
        )
    )

    from app.infra.db.models.enterprise_feature_usage_counters import (
        EnterpriseFeatureUsageCounterModel,
    )

    counter = db.scalar(
        select(EnterpriseFeatureUsageCounterModel).where(
            EnterpriseFeatureUsageCounterModel.enterprise_account_id == enterprise_account_id,
            EnterpriseFeatureUsageCounterModel.feature_code == feature_code,
        )
    )
    used = counter.used_count if counter else 0

    if granted and binding.access_mode == AccessMode.QUOTA and quota:
        if used >= quota.quota_limit:
            granted = False
            reason_code = "quota_exhausted"

    return _mock_b2b_snapshot(
        account_id=enterprise_account_id,
        plan_code=canonical_plan.plan_code,
        granted=granted,
        reason_code=reason_code,
        access_mode=binding.access_mode,
        quota_limit=quota.quota_limit if quota else None,
        used=used,
        period_unit=quota.period_unit if quota else None,
        reset_mode=quota.reset_mode if quota else None,
    )


@pytest.fixture(autouse=True)
def patch_b2b_resolver():
    from unittest.mock import patch

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2b_account_snapshot",
        side_effect=_dynamic_b2b_snapshot,
    ):
        yield


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        for model in (
            AuditEventModel,
            EnterpriseEditorialConfigModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountBillingPlanModel,
            EnterpriseBillingPlanModel,
            EnterpriseAccountModel,
            FeatureUsageCounterModel,
            PlanFeatureQuotaModel,
            PlanFeatureBindingModel,
            FeatureCatalogModel,
            PlanCatalogModel,
            ReferenceVersionModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _setup_b2b_canonical(
    db,
    email="b2b-canonical@example.com",
    access_mode=AccessMode.QUOTA,
    *,
    is_enabled: bool = True,
):
    # Create user and account
    try:
        auth = AuthService.register(
            db,
            email=email,
            password="strong-pass-123",
            role="enterprise_admin",
        )
    except Exception:
        # If user already exists, find him
        from app.infra.db.models.user import UserModel

        user = db.scalar(select(UserModel).where(UserModel.email == email))
        from dataclasses import dataclass

        @dataclass
        class AuthResult:
            user: UserModel

        auth = AuthResult(user=user)

    account = EnterpriseAccountModel(
        admin_user_id=auth.user.id, company_name="Canonical Co", status="active"
    )
    db.add(account)
    db.flush()

    cred = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)

    ent_plan = EnterpriseBillingPlanModel(
        code=f"plan-{email}", display_name="Plan", monthly_fixed_cents=0
    )
    db.add(ent_plan)
    db.flush()

    acc_plan = EnterpriseAccountBillingPlanModel(
        enterprise_account_id=account.id,
        plan_id=ent_plan.id,
    )
    db.add(acc_plan)

    plan_catalog = PlanCatalogModel(
        plan_code=f"cat-{email}",
        plan_name="Cat",
        audience=Audience.B2B,
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        source_id=ent_plan.id,
        is_active=True,
    )
    db.add(plan_catalog)
    db.flush()

    feature = db.scalar(
        select(FeatureCatalogModel).where(
            FeatureCatalogModel.feature_code == B2BApiEntitlementGate.FEATURE_CODE
        )
    )
    if not feature:
        feature = FeatureCatalogModel(
            feature_code=B2BApiEntitlementGate.FEATURE_CODE,
            feature_name="B2B API",
            is_metered=True,
        )
        db.add(feature)
        db.flush()

    binding = PlanFeatureBindingModel(
        plan_id=plan_catalog.id,
        feature_id=feature.id,
        access_mode=access_mode,
        is_enabled=is_enabled,
    )
    db.add(binding)
    db.flush()

    if access_mode == AccessMode.QUOTA:
        quota = PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="calls",
            quota_limit=10,
            period_unit=PeriodUnit.MONTH,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db.add(quota)

    db.commit()
    return cred.api_key, account.id


def test_b2b_astrology_canonical_quota_success():
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)
        api_key, _ = _setup_b2b_canonical(db, "success@b2b.com", AccessMode.QUOTA)

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-canon-1"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["quota_info"]["source"] == "canonical"
    assert payload["quota_info"]["limit"] == 10
    assert payload["quota_info"]["remaining"] == 9


def test_b2b_astrology_canonical_quota_exhausted():
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)
        api_key, _ = _setup_b2b_canonical(db, "exhausted@b2b.com", AccessMode.QUOTA)

    # On consomme les 10
    for i in range(10):
        resp = client.get(
            "/v1/b2b/astrology/weekly-by-sign",
            headers={"X-API-Key": api_key, "X-Request-Id": f"rid-consume-{i}"},
        )
        assert resp.status_code == 200

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-exhausted"},
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "b2b_api_quota_exceeded"


def test_b2b_astrology_canonical_disabled():
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)
        api_key, _ = _setup_b2b_canonical(db, "disabled@b2b.com", AccessMode.DISABLED)

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-disabled"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "b2b_api_access_denied"
    assert response.json()["error"]["details"]["reason"] == "disabled_by_plan"
    assert response.json()["error"]["details"]["reason_code"] == "binding_disabled"


def test_b2b_astrology_disabled_binding_not_enabled_skips_settings_fallback():
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)
        api_key, account_id = _setup_b2b_canonical(
            db,
            "disabled-not-enabled@b2b.com",
            AccessMode.QUOTA,
            is_enabled=False,
        )

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-disabled-not-enabled"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "b2b_api_access_denied"
    assert response.json()["error"]["details"]["reason"] == "disabled_by_plan"
    assert response.json()["error"]["details"]["reason_code"] == "binding_disabled"


def test_b2b_astrology_fallback_settings():
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)
        # On setup un compte SANS plan canonique
        auth = AuthService.register(
            db,
            email="fallback@b2b.com",
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id, company_name="Fallback Co", status="active"
        )
        db.add(account)
        db.flush()
        cred = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        api_key = cred.api_key

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-fallback"},
    )
    assert response.status_code == 403
    payload = response.json()["error"]
    assert payload["code"] == "b2b_no_canonical_plan"


def test_b2b_astrology_canonical_quota_decrements_and_exposes_month_window():
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)
        api_key, _ = _setup_b2b_canonical(db, "decrement@b2b.com", AccessMode.QUOTA)

    first = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-decrement-1"},
    )
    second = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-decrement-2"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["quota_info"]["remaining"] == 9
    assert second.json()["quota_info"]["remaining"] == 8
    assert second.json()["quota_info"]["window_end"].endswith("T00:00:00Z")


def test_b2b_astrology_rolls_back_canonical_usage_when_downstream_fails(monkeypatch):
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)
        api_key, account_id = _setup_b2b_canonical(db, "rollback@b2b.com", AccessMode.QUOTA)
        account = db.get(EnterpriseAccountModel, account_id)
        admin_user_id = account.admin_user_id

    def _raise_downstream(*args, **kwargs):
        raise B2BAstrologyServiceError(
            code="weekly_generation_failed",
            message="downstream failure",
            details={},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.b2b.astrology.B2BAstrologyService.get_weekly_by_sign",
        _raise_downstream,
    )

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-rollback"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "weekly_generation_failed"

    with open_app_test_db_session() as db:
        counters = db.scalars(
            select(FeatureUsageCounterModel).where(
                FeatureUsageCounterModel.user_id == admin_user_id,
                FeatureUsageCounterModel.feature_code == B2BApiEntitlementGate.FEATURE_CODE,
            )
        ).all()
        assert sum(counter.used_count for counter in counters) == 0


def test_b2b_astrology_canonical_unlimited():
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)
        api_key, _ = _setup_b2b_canonical(db, "unlimited@b2b.com", AccessMode.UNLIMITED)

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-unlimited"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["quota_info"]["source"] == "canonical"
