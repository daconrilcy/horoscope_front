from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    PeriodUnit,
    ResetMode,
    SourceOrigin,
    FeatureUsageCounterModel,
)
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.b2b_api_entitlement_gate import B2BApiEntitlementGate

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        # All models involved in B2B/Entitlements
        from app.infra.db.models.user import UserModel
        for model in (
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


def _setup_audit_data(db):
    # 1. User OPS for call
    ops_auth = AuthService.register(db, email="ops@example.com", password="strong-pass-123", role="ops")
    user_auth = AuthService.register(db, email="user@example.com", password="strong-pass-123", role="user")
    
    # 2. Account 1: Canonical Quota
    acc1_admin = AuthService.register(db, email="admin1@example.com", password="strong-pass-123", role="enterprise_admin")
    acc1 = EnterpriseAccountModel(admin_user_id=acc1_admin.user.id, company_name="Canonical Co", status="active")
    db.add(acc1)
    db.flush()
    
    ent_plan = EnterpriseBillingPlanModel(code="plan1", display_name="Plan 1", monthly_fixed_cents=0)
    db.add(ent_plan)
    db.flush()
    db.add(EnterpriseAccountBillingPlanModel(enterprise_account_id=acc1.id, plan_id=ent_plan.id))
    
    plan_cat = PlanCatalogModel(
        plan_code="cat1", plan_name="Cat 1", audience=Audience.B2B, 
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value, source_id=ent_plan.id, is_active=True
    )
    db.add(plan_cat)
    db.flush()
    
    feature = FeatureCatalogModel(feature_code=B2BApiEntitlementGate.FEATURE_CODE, feature_name="B2B", is_metered=True)
    db.add(feature)
    db.flush()
    
    binding = PlanFeatureBindingModel(plan_id=plan_cat.id, feature_id=feature.id, access_mode=AccessMode.QUOTA, is_enabled=True)
    db.add(binding)
    db.flush()
    
    db.add(PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id, quota_key="calls", quota_limit=100, 
        period_unit=PeriodUnit.MONTH, period_value=1, reset_mode=ResetMode.CALENDAR
    ))
    
    # 3. Account 2: Settings Fallback (no plan)
    acc2_admin = AuthService.register(db, email="admin2@example.com", password="strong-pass-123", role="enterprise_admin")
    acc2 = EnterpriseAccountModel(admin_user_id=acc2_admin.user.id, company_name="Fallback Co", status="active")
    db.add(acc2)
    
    db.commit()
    return ops_auth.tokens.access_token, user_auth.tokens.access_token


def test_get_b2b_entitlements_audit_success():
    _cleanup_tables()
    with SessionLocal() as db:
        ops_token, _ = _setup_audit_data(db)
        
    response = client.get(
        "/v1/ops/b2b/entitlements/audit",
        headers={"Authorization": f"Bearer {ops_token}"}
    )
    
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 2
    assert len(payload["items"]) == 2
    
    # Verify Account 1
    item1 = next(i for i in payload["items"] if i["company_name"] == "Canonical Co")
    assert item1["resolution_source"] == "canonical_quota"
    assert item1["quota_limit"] == 100
    
    # Verify Account 2
    item2 = next(i for i in payload["items"] if i["company_name"] == "Fallback Co")
    assert item2["resolution_source"] == "settings_fallback"
    assert item2["reason"] == "no_canonical_plan"


def test_get_b2b_entitlements_audit_filters():
    _cleanup_tables()
    with SessionLocal() as db:
        ops_token, _ = _setup_audit_data(db)
        
    # Filter by resolution_source
    response = client.get(
        "/v1/ops/b2b/entitlements/audit?resolution_source=settings_fallback",
        headers={"Authorization": f"Bearer {ops_token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["total_count"] == 1
    assert response.json()["data"]["items"][0]["company_name"] == "Fallback Co"
    
    # Blocker only
    response = client.get(
        "/v1/ops/b2b/entitlements/audit?blocker_only=true",
        headers={"Authorization": f"Bearer {ops_token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["total_count"] == 1
    assert response.json()["data"]["items"][0]["company_name"] == "Fallback Co"


def test_get_b2b_entitlements_audit_forbidden():
    _cleanup_tables()
    with SessionLocal() as db:
        _, user_token = _setup_audit_data(db)
        
    response = client.get(
        "/v1/ops/b2b/entitlements/audit",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_get_b2b_entitlements_audit_invalid_filter():
    _cleanup_tables()
    with SessionLocal() as db:
        ops_token, _ = _setup_audit_data(db)
        
    response = client.get(
        "/v1/ops/b2b/entitlements/audit?resolution_source=INVALID",
        headers={"Authorization": f"Bearer {ops_token}"}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_resolution_source"


def test_get_b2b_entitlements_audit_no_side_effects():
    _cleanup_tables()
    with SessionLocal() as db:
        ops_token, _ = _setup_audit_data(db)
        
    # Pre-check counters
    with SessionLocal() as db:
        count_before = db.query(FeatureUsageCounterModel).count()
        
    response = client.get(
        "/v1/ops/b2b/entitlements/audit",
        headers={"Authorization": f"Bearer {ops_token}"}
    )
    assert response.status_code == 200
    
    # Post-check counters
    with SessionLocal() as db:
        count_after = db.query(FeatureUsageCounterModel).count()
        
    assert count_before == count_after, "Audit should not create any usage counters"
