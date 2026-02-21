from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingCycleModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.enterprise_credentials_service import EnterpriseCredentialsService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            AuditEventModel,
            EnterpriseAccountBillingPlanModel,
            EnterpriseBillingCycleModel,
            EnterpriseBillingPlanModel,
            EnterpriseDailyUsageModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_enterprise_context(email: str) -> tuple[int, int]:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=email,
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id,
            company_name="Acme Media",
            status="active",
        )
        db.add(account)
        db.flush()
        credential = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return account.id, credential.credential_id


def _create_ops_token(email: str = "ops-reconciliation@example.com") -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="ops")
        db.commit()
        return auth.tokens.access_token


def test_reconciliation_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/b2b/reconciliation/issues")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_reconciliation_forbidden_for_non_ops_role() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="support-reconciliation@example.com",
            password="strong-pass-123",
            role="support",
        )
        db.commit()
        token = auth.tokens.access_token
    response = client.get(
        "/v1/ops/b2b/reconciliation/issues",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_reconciliation_list_detail_and_action_flow() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context("reconciliation-flow@example.com")
    ops_token = _create_ops_token()
    with SessionLocal() as db:
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=account_id,
                credential_id=credential_id,
                usage_date=date(2026, 2, 10),
                used_count=9,
            )
        )
        db.commit()

    list_response = client.get(
        "/v1/ops/b2b/reconciliation/issues",
        params={"account_id": account_id, "severity": "major"},
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-reconciliation-list",
        },
    )
    assert list_response.status_code == 200
    listed = list_response.json()["data"]
    assert listed["total"] == 1
    issue_id = listed["items"][0]["issue_id"]

    detail_response = client.get(
        f"/v1/ops/b2b/reconciliation/issues/{issue_id}",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-reconciliation-detail",
        },
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["issue"]["issue_id"] == issue_id
    assert len(detail_response.json()["data"]["issue"]["recommended_actions"]) == 4

    action_response = client.post(
        f"/v1/ops/b2b/reconciliation/issues/{issue_id}/actions",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-reconciliation-action",
        },
        json={"action": "mark_investigated", "note": "analyste assigne"},
    )
    assert action_response.status_code == 200
    assert action_response.json()["data"]["action"] == "mark_investigated"

    with SessionLocal() as db:
        action_audit = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-reconciliation-action")
            .where(AuditEventModel.action == "b2b_reconciliation_action")
            .limit(1)
        )
        assert action_audit is not None
        assert action_audit.status == "success"


def test_reconciliation_invalid_issue_id_returns_422() -> None:
    _cleanup_tables()
    ops_token = _create_ops_token("ops-reconciliation-invalid@example.com")
    response = client.get(
        "/v1/ops/b2b/reconciliation/issues/not-valid",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-reconciliation-invalid",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_issue_id"
