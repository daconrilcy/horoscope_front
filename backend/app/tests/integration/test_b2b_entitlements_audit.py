from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_feature_usage_counters import (
    EnterpriseFeatureUsageCounterModel,
)
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
from app.main import app
from app.services.auth_service import AuthService
from app.services.b2b.api_entitlement_gate import B2BApiEntitlementGate
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def _cleanup_tables() -> None:
    app_test_engine().dispose()
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    app_test_engine().dispose()
    with open_app_test_db_session() as db:
        from app.infra.db.models.user import UserModel

        for model in (
            EnterpriseFeatureUsageCounterModel,
            FeatureUsageCounterModel,
            PlanFeatureQuotaModel,
            PlanFeatureBindingModel,
            FeatureCatalogModel,
            PlanCatalogModel,
            EnterpriseAccountBillingPlanModel,
            EnterpriseBillingPlanModel,
            EnterpriseAccountModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()
    app_test_engine().dispose()


def _register_user(db, *, email: str, role: str):
    return AuthService.register(
        db,
        email=email,
        password="strong-pass-123",
        role=role,
    )


def _create_account_with_plan(
    db,
    *,
    email: str,
    company_name: str,
    plan_code: str,
    canonical_plan_code: str,
    feature: FeatureCatalogModel,
    with_binding: bool,
    admin_user_id: int | None = None,
) -> int:
    if admin_user_id is None:
        admin_auth = _register_user(db, email=email, role="enterprise_admin")
        admin_user_id = admin_auth.user.id

    account = EnterpriseAccountModel(
        admin_user_id=admin_user_id,
        company_name=company_name,
        status="active",
    )
    db.add(account)
    db.flush()

    enterprise_plan = EnterpriseBillingPlanModel(
        code=plan_code,
        display_name=plan_code,
        monthly_fixed_cents=0,
        included_monthly_units=100,
    )
    db.add(enterprise_plan)
    db.flush()

    db.add(
        EnterpriseAccountBillingPlanModel(
            enterprise_account_id=account.id,
            plan_id=enterprise_plan.id,
        )
    )

    canonical_plan = PlanCatalogModel(
        plan_code=canonical_plan_code,
        plan_name=canonical_plan_code,
        audience=Audience.B2B,
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        source_id=enterprise_plan.id,
        is_active=True,
    )
    db.add(canonical_plan)
    db.flush()

    if not with_binding:
        return account.id

    binding = PlanFeatureBindingModel(
        plan_id=canonical_plan.id,
        feature_id=feature.id,
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
    )
    db.add(binding)
    db.flush()

    db.add(
        PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="calls",
            quota_limit=100,
            period_unit=PeriodUnit.MONTH,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
    )
    return account.id


def _setup_audit_data(db) -> tuple[str, str]:
    ops_auth = _register_user(db, email="ops@example.com", role="ops")
    user_auth = _register_user(db, email="user@example.com", role="user")

    feature = FeatureCatalogModel(
        feature_code=B2BApiEntitlementGate.FEATURE_CODE,
        feature_name="B2B API",
        is_metered=True,
    )
    db.add(feature)
    db.flush()

    _create_account_with_plan(
        db,
        email="admin1@example.com",
        company_name="Canonical Co",
        plan_code="plan1",
        canonical_plan_code="cat1",
        feature=feature,
        with_binding=True,
    )
    _create_account_with_plan(
        db,
        email="admin2@example.com",
        company_name="Fallback Co",
        plan_code="plan2",
        canonical_plan_code="cat2",
        feature=feature,
        with_binding=False,
    )

    db.commit()
    return ops_auth.tokens.access_token, user_auth.tokens.access_token


def test_get_b2b_entitlements_audit_success() -> None:
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ops_token, _ = _setup_audit_data(db)

    response = client.get(
        "/v1/ops/b2b/entitlements/audit",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 2
    assert len(payload["items"]) == 2

    canonical_item = next(
        item for item in payload["items"] if item["company_name"] == "Canonical Co"
    )
    assert canonical_item["resolution_source"] == "canonical_quota"
    assert canonical_item["quota_limit"] == 100

    fallback_item = next(item for item in payload["items"] if item["company_name"] == "Fallback Co")
    assert fallback_item["resolution_source"] == "settings_fallback"
    assert fallback_item["reason"] == "no_binding"


def test_get_b2b_entitlements_audit_filters() -> None:
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ops_token, _ = _setup_audit_data(db)

    response = client.get(
        "/v1/ops/b2b/entitlements/audit?resolution_source=settings_fallback",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 1
    assert payload["items"][0]["company_name"] == "Fallback Co"


def test_get_b2b_entitlements_audit_blocker_only_excludes_canonical_disabled() -> None:
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ops_token, _ = _setup_audit_data(db)
        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "b2b_api_access")
        )
        disabled_admin = _register_user(
            db, email="admin-disabled@example.com", role="enterprise_admin"
        )
        disabled_account = EnterpriseAccountModel(
            admin_user_id=disabled_admin.user.id,
            company_name="Disabled Co",
            status="active",
        )
        db.add(disabled_account)
        db.flush()

        disabled_plan = EnterpriseBillingPlanModel(
            code="plan-disabled",
            display_name="Disabled",
            monthly_fixed_cents=0,
            included_monthly_units=0,
        )
        db.add(disabled_plan)
        db.flush()

        db.add(
            EnterpriseAccountBillingPlanModel(
                enterprise_account_id=disabled_account.id,
                plan_id=disabled_plan.id,
            )
        )
        disabled_canonical_plan = PlanCatalogModel(
            plan_code="cat-disabled",
            plan_name="cat-disabled",
            audience=Audience.B2B,
            source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
            source_id=disabled_plan.id,
            is_active=True,
        )
        db.add(disabled_canonical_plan)
        db.flush()
        db.add(
            PlanFeatureBindingModel(
                plan_id=disabled_canonical_plan.id,
                feature_id=feature.id,
                access_mode=AccessMode.DISABLED,
                is_enabled=False,
            )
        )
        db.commit()

    response = client.get(
        "/v1/ops/b2b/entitlements/audit?blocker_only=true",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 1
    assert payload["items"][0]["company_name"] == "Fallback Co"


def test_get_b2b_entitlements_audit_forbidden() -> None:
    _cleanup_tables()
    with open_app_test_db_session() as db:
        _, user_token = _setup_audit_data(db)

    response = client.get(
        "/v1/ops/b2b/entitlements/audit",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_get_b2b_entitlements_audit_invalid_filter() -> None:
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ops_token, _ = _setup_audit_data(db)

    response = client.get(
        "/v1/ops/b2b/entitlements/audit?resolution_source=INVALID",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_resolution_source"


def test_get_b2b_entitlements_audit_no_side_effects() -> None:
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ops_token, _ = _setup_audit_data(db)

    with open_app_test_db_session() as db:
        from sqlalchemy import func

        count_before = db.scalar(select(func.count(EnterpriseFeatureUsageCounterModel.id)))

    response = client.get(
        "/v1/ops/b2b/entitlements/audit",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200

    with open_app_test_db_session() as db:
        count_after = db.scalar(select(func.count(EnterpriseFeatureUsageCounterModel.id)))

    assert count_before == count_after


def test_audit_works_even_if_admin_user_id_is_null() -> None:
    _cleanup_tables()
    with open_app_test_db_session() as db:
        ops_auth = _register_user(db, email="ops@example.com", role="ops")
        feature = FeatureCatalogModel(
            feature_code=B2BApiEntitlementGate.FEATURE_CODE,
            feature_name="B2B API",
            is_metered=True,
        )
        db.add(feature)
        db.flush()

        # Compte SANS admin_user_id mais avec plan valide
        _create_account_with_plan(
            db,
            email="ignored@example.com",
            company_name="No Admin Co",
            plan_code="p-noadmin",
            canonical_plan_code="c-noadmin",
            feature=feature,
            with_binding=True,
            admin_user_id=None,
        )
        # On supprime l'admin_user_id juste après la création (qui l'a créé via email)
        account = db.scalar(
            select(EnterpriseAccountModel).where(
                EnterpriseAccountModel.company_name == "No Admin Co"
            )
        )
        account.admin_user_id = None
        db.commit()
        ops_token = ops_auth.tokens.access_token

    response = client.get(
        "/v1/ops/b2b/entitlements/audit",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    item = next(i for i in payload["items"] if i["company_name"] == "No Admin Co")

    # AC 14: Ne doit plus être en settings_fallback / admin_user_id_missing
    assert item["resolution_source"] == "canonical_quota"
    assert item["admin_user_id_present"] is False
