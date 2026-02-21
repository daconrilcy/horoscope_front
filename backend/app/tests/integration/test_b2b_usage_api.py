from datetime import UTC, date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.audit_service import AuditServiceError
from app.services.auth_service import AuthService
from app.services.enterprise_credentials_service import EnterpriseCredentialsService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            AuditEventModel,
            EnterpriseDailyUsageModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_enterprise_api_key(email: str) -> tuple[str, int, int]:
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
        return created.api_key, account.id, created.credential_id


def _seed_usage(*, account_id: int, credential_id: int, usage_date: date, used_count: int) -> None:
    with SessionLocal() as db:
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=account_id,
                credential_id=credential_id,
                usage_date=usage_date,
                used_count=used_count,
            )
        )
        db.commit()


def test_b2b_usage_summary_requires_api_key() -> None:
    _cleanup_tables()
    response = client.get("/v1/b2b/usage/summary")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"


def test_b2b_usage_summary_returns_data_for_valid_api_key() -> None:
    _cleanup_tables()
    api_key, account_id, credential_id = _create_enterprise_api_key("b2b-usage-summary@example.com")
    today = datetime.now(UTC).date()
    _seed_usage(
        account_id=account_id,
        credential_id=credential_id,
        usage_date=today,
        used_count=3,
    )

    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-summary"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"] == "rid-b2b-usage-summary"
    assert payload["data"]["account_id"] == account_id
    assert payload["data"]["credential_id"] == credential_id
    assert payload["data"]["daily_consumed"] == 3


def test_b2b_usage_summary_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    api_key, _, _ = _create_enterprise_api_key("b2b-usage-429@example.com")

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "4"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.b2b_usage.check_rate_limit", _always_rate_limited)
    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-429"},
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limit_exceeded"
    assert response.json()["error"]["request_id"] == "rid-b2b-usage-429"


def test_b2b_usage_summary_writes_success_audit_event() -> None:
    _cleanup_tables()
    api_key, account_id, credential_id = _create_enterprise_api_key("b2b-usage-audit@example.com")
    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-audit"},
    )
    assert response.status_code == 200

    with SessionLocal() as db:
        event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-b2b-usage-audit")
            .where(AuditEventModel.action == "b2b_usage_summary_read")
            .where(AuditEventModel.status == "success")
            .limit(1)
        )
        assert event is not None
        assert event.target_type == "enterprise_usage"
        assert event.target_id == str(credential_id)
        assert int(event.details["account_id"]) == account_id


def test_b2b_usage_summary_returns_503_when_audit_unavailable(monkeypatch: object) -> None:
    _cleanup_tables()
    api_key, _, _ = _create_enterprise_api_key("b2b-usage-audit-down@example.com")

    def _raise_audit_error(*args: object, **kwargs: object) -> None:
        raise AuditServiceError(
            code="audit_unavailable",
            message="audit unavailable",
            details={},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.b2b_usage.AuditService.record_event",
        _raise_audit_error,
    )
    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-audit-down"},
    )
    assert response.status_code == 503
    payload = response.json()["error"]
    assert payload["code"] == "audit_unavailable"
    assert payload["request_id"] == "rid-b2b-usage-audit-down"
