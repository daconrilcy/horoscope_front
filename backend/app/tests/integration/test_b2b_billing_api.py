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


def _create_enterprise_api_key(email: str) -> tuple[str, int]:
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
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return created.api_key, account.id


def _seed_usage_from_api_key(api_key: str, *, usage_date: date, used_count: int) -> None:
    with SessionLocal() as db:
        authenticated = EnterpriseCredentialsService.authenticate_api_key(db, api_key=api_key)
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=authenticated.account_id,
                credential_id=authenticated.credential_id,
                usage_date=usage_date,
                used_count=used_count,
            )
        )
        db.commit()


def _create_ops_access_token(email: str = "ops-b2b-billing@example.com") -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="ops")
        db.commit()
        return auth.tokens.access_token


def test_b2b_billing_close_cycle_and_read_latest() -> None:
    _cleanup_tables()
    api_key, account_id = _create_enterprise_api_key("b2b-billing-close@example.com")
    _seed_usage_from_api_key(api_key, usage_date=date(2026, 2, 12), used_count=7)
    ops_token = _create_ops_access_token()

    close = client.post(
        "/v1/b2b/billing/cycles/close",
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-b2b-billing-close"},
        json={
            "account_id": account_id,
            "period_start": "2026-02-01",
            "period_end": "2026-02-28",
        },
    )
    assert close.status_code == 200
    close_payload = close.json()
    assert close_payload["meta"]["request_id"] == "rid-b2b-billing-close"
    assert (
        close_payload["data"]["total_amount_cents"] >= close_payload["data"]["fixed_amount_cents"]
    )

    latest = client.get(
        "/v1/b2b/billing/cycles/latest",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-billing-latest"},
    )
    assert latest.status_code == 200
    latest_payload = latest.json()
    assert latest_payload["meta"]["request_id"] == "rid-b2b-billing-latest"
    assert latest_payload["data"]["period_start"] == "2026-02-01"
    assert latest_payload["data"]["period_end"] == "2026-02-28"

    listing = client.get(
        "/v1/b2b/billing/cycles",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-billing-list"},
    )
    assert listing.status_code == 200
    assert listing.json()["data"]["total"] == 1


def test_b2b_billing_close_cycle_is_idempotent() -> None:
    _cleanup_tables()
    api_key, account_id = _create_enterprise_api_key("b2b-billing-idempotent@example.com")
    _seed_usage_from_api_key(api_key, usage_date=date(2026, 2, 2), used_count=3)
    ops_token = _create_ops_access_token("ops-b2b-billing-idempotent@example.com")

    body = {
        "account_id": account_id,
        "period_start": "2026-02-01",
        "period_end": "2026-02-28",
    }
    first = client.post(
        "/v1/b2b/billing/cycles/close", headers={"Authorization": f"Bearer {ops_token}"}, json=body
    )
    second = client.post(
        "/v1/b2b/billing/cycles/close", headers={"Authorization": f"Bearer {ops_token}"}, json=body
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["cycle_id"] == second.json()["data"]["cycle_id"]


def test_b2b_billing_close_cycle_forbidden_for_non_ops() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        user = AuthService.register(
            db,
            email="support-b2b-billing@example.com",
            password="strong-pass-123",
            role="support",
        )
        db.commit()
        token = user.tokens.access_token
    response = client.post(
        "/v1/b2b/billing/cycles/close",
        headers={"Authorization": f"Bearer {token}", "X-Request-Id": "rid-b2b-billing-forbidden"},
        json={"account_id": 1, "period_start": "2026-02-01", "period_end": "2026-02-28"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"
    assert response.json()["error"]["request_id"] == "rid-b2b-billing-forbidden"


def test_b2b_billing_latest_requires_api_key() -> None:
    _cleanup_tables()
    response = client.get("/v1/b2b/billing/cycles/latest")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"


def test_b2b_billing_list_returns_422_for_invalid_pagination() -> None:
    _cleanup_tables()
    api_key, _ = _create_enterprise_api_key("b2b-billing-pagination@example.com")
    response = client.get(
        "/v1/b2b/billing/cycles?limit=0&offset=0",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-billing-pagination"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_billing_pagination"


def test_b2b_billing_latest_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    api_key, _ = _create_enterprise_api_key("b2b-billing-429@example.com")

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "2"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.b2b_billing.check_rate_limit", _always_rate_limited)

    response = client.get(
        "/v1/b2b/billing/cycles/latest",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-billing-429"},
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limit_exceeded"
    assert response.json()["error"]["request_id"] == "rid-b2b-billing-429"


def test_b2b_billing_ops_can_consult_latest_cycle() -> None:
    _cleanup_tables()
    api_key, account_id = _create_enterprise_api_key("b2b-billing-ops-read@example.com")
    _seed_usage_from_api_key(api_key, usage_date=date(2026, 2, 20), used_count=4)
    ops_token = _create_ops_access_token("ops-b2b-billing-ops-read@example.com")
    close = client.post(
        "/v1/b2b/billing/cycles/close",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-b2b-billing-ops-close",
        },
        json={"account_id": account_id, "period_start": "2026-02-01", "period_end": "2026-02-28"},
    )
    assert close.status_code == 200

    latest = client.get(
        f"/v1/b2b/billing/ops/cycles/latest?account_id={account_id}",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-b2b-billing-ops-latest",
        },
    )
    assert latest.status_code == 200
    assert latest.json()["meta"]["request_id"] == "rid-b2b-billing-ops-latest"


def test_b2b_billing_read_endpoints_write_audit_events() -> None:
    _cleanup_tables()
    api_key, account_id = _create_enterprise_api_key("b2b-billing-audit-read@example.com")
    _seed_usage_from_api_key(api_key, usage_date=date(2026, 2, 18), used_count=1)
    ops_token = _create_ops_access_token("ops-b2b-billing-audit-read@example.com")
    close = client.post(
        "/v1/b2b/billing/cycles/close",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-b2b-billing-audit-close",
        },
        json={"account_id": account_id, "period_start": "2026-02-01", "period_end": "2026-02-28"},
    )
    assert close.status_code == 200

    latest = client.get(
        "/v1/b2b/billing/cycles/latest",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-billing-audit-latest"},
    )
    listing = client.get(
        "/v1/b2b/billing/cycles",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-billing-audit-list"},
    )
    assert latest.status_code == 200
    assert listing.status_code == 200

    with SessionLocal() as db:
        latest_audit = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-b2b-billing-audit-latest")
            .where(AuditEventModel.action == "b2b_billing_cycle_read_latest")
            .limit(1)
        )
        list_audit = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-b2b-billing-audit-list")
            .where(AuditEventModel.action == "b2b_billing_cycle_read_list")
            .limit(1)
        )
        assert latest_audit is not None
        assert latest_audit.status == "success"
        assert list_audit is not None
        assert list_audit.status == "success"
