from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import joinedload, sessionmaker

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
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
from app.infra.db.models.user import UserModel
from app.main import app
from app.tests.helpers.db_session import (
    open_app_test_db_session,
    reset_app_test_db_session_factory,
    use_app_test_db_session_factory,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test-admin-entitlements.db').as_posix()}"
    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    use_app_test_db_session_factory(test_session_local)
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        reset_app_test_db_session_factory()
        test_engine.dispose()


@pytest.fixture
def admin_token():
    with open_app_test_db_session() as db:
        from app.core.security import hash_password

        admin = UserModel(
            email="admin-ent@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard",
        )
        db.add(admin)
        db.commit()

    response = client.post(
        "/v1/auth/login", json={"email": "admin-ent@example.com", "password": "admin123"}
    )
    return response.json()["data"]["tokens"]["access_token"]


def test_get_entitlement_matrix_success(admin_token):
    with open_app_test_db_session() as db:
        # 1. Setup Plan
        plan = PlanCatalogModel(plan_code="free", plan_name="Free Plan", audience=Audience.B2C)
        db.add(plan)

        # 2. Setup Feature
        feat = FeatureCatalogModel(feature_code="chat", feature_name="Chat Feature")
        db.add(feat)
        db.flush()

        # 3. Setup Binding
        binding = PlanFeatureBindingModel(
            plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
        )
        db.add(binding)
        db.flush()

        # 4. Setup Quota
        quota = PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="daily",
            quota_limit=5,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db.add(quota)
        db.commit()

        plan_id = plan.id
        feat_id = feat.id

    response = client.get(
        "/v1/admin/entitlements/matrix", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data["plans"]) >= 1
    assert len(data["features"]) >= 1

    cell_key = f"{plan_id}:{feat_id}"
    assert cell_key in data["cells"]
    cell = data["cells"][cell_key]
    assert cell["access_mode"] == "quota"
    assert cell["quota_limit"] == 5
    assert cell["is_incoherent"] is False


def test_get_entitlement_matrix_incoherent(admin_token):
    with open_app_test_db_session() as db:
        plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
        db.add(plan)
        feat = FeatureCatalogModel(feature_code="natal", feature_name="Natal")
        db.add(feat)
        db.flush()

        # Binding with QUOTA but NO actual quota records
        binding = PlanFeatureBindingModel(
            plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
        )
        db.add(binding)
        db.commit()
        plan_id = plan.id
        feat_id = feat.id

    response = client.get(
        "/v1/admin/entitlements/matrix", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    cell_key = f"{plan_id}:{feat_id}"
    assert response.json()["cells"][cell_key]["is_incoherent"] is True


def test_update_entitlement_success(admin_token):
    with open_app_test_db_session() as db:
        plan = PlanCatalogModel(plan_code="edit-plan", plan_name="Edit Plan", audience=Audience.B2C)
        db.add(plan)
        feat = FeatureCatalogModel(feature_code="edit-feat", feature_name="Edit Feat")
        db.add(feat)
        db.flush()
        binding = PlanFeatureBindingModel(
            plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.DISABLED, is_enabled=False
        )
        db.add(binding)
        db.flush()
        quota = PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="daily",
            quota_limit=1,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db.add(quota)
        db.commit()
        plan_id = plan.id
        feat_id = feat.id

    response = client.patch(
        f"/v1/admin/entitlements/{plan_id}/{feat_id}",
        json={"access_mode": "quota", "quota_limit": 10, "is_enabled": True},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    with open_app_test_db_session() as db:
        # Re-fetch binding
        b = db.scalar(
            select(PlanFeatureBindingModel)
            .where(
                PlanFeatureBindingModel.plan_id == plan_id,
                PlanFeatureBindingModel.feature_id == feat_id,
            )
            .options(joinedload(PlanFeatureBindingModel.quotas))
        )
        assert b.access_mode == AccessMode.QUOTA
        assert b.is_enabled is True
        assert b.quotas[0].quota_limit == 10

        # Check audit
        audit = db.scalar(
            select(AuditEventModel).where(AuditEventModel.action == "entitlement_quota_updated")
        )
        assert audit is not None
