from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.product_entitlements import (
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    SourceOrigin,
)
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    # Use drop/create to ensure fresh state and avoid foreign key issues
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _register_user(db, *, email: str, role: str):
    return AuthService.register(
        db,
        email=email,
        password="strong-pass-123",
        role=role,
    )


def _setup_repair_data(db) -> tuple[str, int, int]:
    ops_auth = _register_user(db, email="ops@example.com", role="ops")

    feature = FeatureCatalogModel(
        feature_code="b2b_api_access",
        feature_name="B2B API",
        is_metered=True,
    )
    db.add(feature)
    db.flush()

    # 1. Account with NO canonical plan (units > 0)
    admin1 = _register_user(db, email="admin1@example.com", role="enterprise_admin")
    acc1 = EnterpriseAccountModel(
        admin_user_id=admin1.user.id, company_name="No Plan Co", status="active"
    )
    db.add(acc1)
    db.flush()
    plan1 = EnterpriseBillingPlanModel(
        code="p1", display_name="P1", included_monthly_units=100, monthly_fixed_cents=0
    )
    db.add(plan1)
    db.flush()
    db.add(EnterpriseAccountBillingPlanModel(enterprise_account_id=acc1.id, plan_id=plan1.id))

    # 2. Account WITH canonical plan but NO binding (units > 0)
    admin2 = _register_user(db, email="admin2@example.com", role="enterprise_admin")
    acc2 = EnterpriseAccountModel(
        admin_user_id=admin2.user.id, company_name="No Binding Co", status="active"
    )
    db.add(acc2)
    db.flush()
    plan2 = EnterpriseBillingPlanModel(
        code="p2", display_name="P2", included_monthly_units=200, monthly_fixed_cents=0
    )
    db.add(plan2)
    db.flush()
    db.add(EnterpriseAccountBillingPlanModel(enterprise_account_id=acc2.id, plan_id=plan2.id))
    db.add(
        PlanCatalogModel(
            plan_code="p2",
            plan_name="P2",
            audience=Audience.B2B,
            source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
            source_id=plan2.id,
            is_active=True,
        )
    )

    # 3. Account needing manual review (units = 0)
    admin3 = _register_user(db, email="admin3@example.com", role="enterprise_admin")
    acc3 = EnterpriseAccountModel(
        admin_user_id=admin3.user.id, company_name="Zero Units Co", status="active"
    )
    db.add(acc3)
    db.flush()
    plan3 = EnterpriseBillingPlanModel(
        code="p3", display_name="P3", included_monthly_units=0, monthly_fixed_cents=0
    )
    db.add(plan3)
    db.flush()
    db.add(EnterpriseAccountBillingPlanModel(enterprise_account_id=acc3.id, plan_id=plan3.id))
    cat3 = PlanCatalogModel(
        plan_code="p3",
        plan_name="P3",
        audience=Audience.B2B,
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        source_id=plan3.id,
        is_active=True,
    )
    db.add(cat3)
    db.flush()

    db.commit()
    return ops_auth.tokens.access_token, acc3.id, cat3.id


def test_repair_run_dry_run_success() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        ops_token, _, _ = _setup_repair_data(db)

    response = client.post(
        "/v1/ops/b2b/entitlements/repair/run?dry_run=true",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dry_run"] is True
    assert data["plans_created"] == 1  # acc1
    assert data["bindings_created"] == 2  # acc1 and acc2
    assert len(data["remaining_blockers"]) == 1  # acc3 (zero units)
    assert data["remaining_blockers"][0]["recommended_action"] == "classify_zero_units"

    # Verify NO data in DB
    with SessionLocal() as db:
        assert db.scalar(select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "p1")) is None


def test_repair_run_and_classify_zero_units_e2e() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        ops_token, acc3_id, cat3_id = _setup_repair_data(db)

    # 1. Run repair
    response = client.post(
        "/v1/ops/b2b/entitlements/repair/run",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["plans_created"] == 1
    assert data["bindings_created"] == 2
    assert len(data["remaining_blockers"]) == 1

    # 2. Audit should show 1 blocker (acc3)
    response = client.get(
        "/v1/ops/b2b/entitlements/audit?blocker_only=true",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["total_count"] == 1
    assert response.json()["data"]["items"][0]["company_name"] == "Zero Units Co"

    # 3. Classify acc3
    response = client.post(
        "/v1/ops/b2b/entitlements/repair/classify-zero-units",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={"canonical_plan_id": cat3_id, "access_mode": "disabled", "quota_limit": None},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "created"

    response = client.get(
        "/v1/ops/b2b/entitlements/audit?blocker_only=true",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["total_count"] == 0


def test_set_admin_user_success() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        ops_token, _, _ = _setup_repair_data(db)

        # Create account without admin
        acc = EnterpriseAccountModel(company_name="No Admin Co", status="active")
        db.add(acc)
        db.flush()
        acc_id = acc.id

        # Create user to become admin
        user = _register_user(db, email="new_admin@example.com", role="enterprise_admin")
        user_id = user.user.id
        db.commit()

    response = client.post(
        "/v1/ops/b2b/entitlements/repair/set-admin-user",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={"account_id": acc_id, "user_id": user_id},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    with SessionLocal() as db:
        acc = db.get(EnterpriseAccountModel, acc_id)
        assert acc.admin_user_id == user_id


def test_repair_run_works_even_if_admin_user_id_is_null() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        ops_auth = _register_user(db, email="ops@example.com", role="ops")
        ops_token = ops_auth.tokens.access_token

        feature = FeatureCatalogModel(
            feature_code="b2b_api_access",
            feature_name="B2B API",
            is_metered=True,
        )
        db.add(feature)
        db.flush()

        # Compte SANS admin_user_id mais avec usage > 0 (via ent plan)
        acc = EnterpriseAccountModel(
            company_name="No Admin Co", status="active", admin_user_id=None
        )
        db.add(acc)
        db.flush()
        plan = EnterpriseBillingPlanModel(
            code="p-noadmin",
            display_name="P No Admin",
            included_monthly_units=150,
            monthly_fixed_cents=0,
        )
        db.add(plan)
        db.flush()
        db.add(EnterpriseAccountBillingPlanModel(enterprise_account_id=acc.id, plan_id=plan.id))
        db.commit()

    # AC 15: run_auto_repair ne doit plus considérer admin_user_id_missing comme un blocker
    response = client.post(
        "/v1/ops/b2b/entitlements/repair/run",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["plans_created"] == 1
    assert data["bindings_created"] == 1
    # Aucun blocker car le plan a > 0 units
    assert len(data["remaining_blockers"]) == 0

    # Vérification audit
    response = client.get(
        "/v1/ops/b2b/entitlements/audit",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["resolution_source"] == "canonical_quota"
    assert item["quota_limit"] == 150
    assert item["admin_user_id_present"] is False
