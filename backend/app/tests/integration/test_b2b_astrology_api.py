from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.config import settings
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_editorial_config import EnterpriseEditorialConfigModel
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.audit_service import AuditServiceError
from app.services.auth_service import AuthService
from app.services.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.reference_data_service import ReferenceDataService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            AuditEventModel,
            EnterpriseEditorialConfigModel,
            EnterpriseDailyUsageModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_enterprise_api_key(email: str) -> str:
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
        return created.api_key


def test_b2b_astrology_requires_api_key_header() -> None:
    _cleanup_tables()
    response = client.get("/v1/b2b/astrology/weekly-by-sign")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"


def test_b2b_astrology_rejects_invalid_api_key() -> None:
    _cleanup_tables()
    _create_enterprise_api_key("b2b-invalid-base@example.com")
    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": "b2b_invalid_unknown_secret", "X-Request-Id": "rid-b2b-invalid"},
    )
    assert response.status_code == 401
    payload = response.json()["error"]
    assert payload["code"] == "invalid_api_key"
    assert payload["request_id"] == "rid-b2b-invalid"


def test_b2b_astrology_rejects_revoked_api_key() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="b2b-revoked@example.com",
            password="strong-pass-123",
            role="enterprise_admin",
        )
        db.add(
            EnterpriseAccountModel(
                admin_user_id=auth.user.id,
                company_name="Acme Media",
                status="active",
            )
        )
        db.flush()
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        EnterpriseCredentialsService.rotate_credential(db, admin_user_id=auth.user.id)
        db.commit()
        revoked_key = created.api_key

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": revoked_key, "X-Request-Id": "rid-b2b-revoked"},
    )
    assert response.status_code == 403
    payload = response.json()["error"]
    assert payload["code"] == "revoked_api_key"
    assert payload["request_id"] == "rid-b2b-revoked"


def test_b2b_astrology_returns_weekly_by_sign_with_valid_api_key() -> None:
    _cleanup_tables()
    api_key = _create_enterprise_api_key("b2b-success@example.com")
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db)

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-success"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"] == "rid-b2b-success"
    assert payload["data"]["api_version"] == "v1"
    assert len(payload["data"]["items"]) > 0


def test_b2b_usage_summary_returns_metrics_for_credential() -> None:
    _cleanup_tables()
    api_key = _create_enterprise_api_key("b2b-usage-summary@example.com")
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db)

    first_call = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-1"},
    )
    assert first_call.status_code == 200

    summary = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-summary"},
    )
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["meta"]["request_id"] == "rid-b2b-usage-summary"
    assert payload["data"]["daily_consumed"] >= 1
    assert payload["data"]["monthly_consumed"] >= 1
    assert payload["data"]["limit_mode"] in {"block", "overage"}


def test_b2b_astrology_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    api_key = _create_enterprise_api_key("b2b-429@example.com")
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db)

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "3"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.b2b_astrology.check_rate_limit", _always_rate_limited)

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-429"},
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limit_exceeded"
    assert response.json()["error"]["request_id"] == "rid-b2b-429"


def test_b2b_astrology_returns_429_when_b2b_quota_exceeded(monkeypatch: object) -> None:
    _cleanup_tables()
    api_key = _create_enterprise_api_key("b2b-quota-exceeded@example.com")
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db)

    monkeypatch.setattr(settings, "b2b_daily_usage_limit", 1)
    monkeypatch.setattr(settings, "b2b_monthly_usage_limit", 10)
    monkeypatch.setattr(settings, "b2b_usage_limit_mode", "block")

    first = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-quota-ok"},
    )
    assert first.status_code == 200

    second = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-quota-block"},
    )
    assert second.status_code == 429
    payload = second.json()["error"]
    assert payload["code"] == "b2b_quota_exceeded"
    assert payload["request_id"] == "rid-b2b-quota-block"


def test_b2b_astrology_rejects_api_key_for_inactive_enterprise_account() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="b2b-inactive-account@example.com",
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
        account.status = "inactive"
        db.commit()
        api_key = created.api_key

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-inactive-account"},
    )
    assert response.status_code == 403
    payload = response.json()["error"]
    assert payload["code"] == "enterprise_account_inactive"
    assert payload["request_id"] == "rid-b2b-inactive-account"


def test_b2b_astrology_keeps_auth_error_when_audit_is_unavailable(monkeypatch: object) -> None:
    _cleanup_tables()
    _create_enterprise_api_key("b2b-audit-down@example.com")

    def _raise_audit_error(*args: object, **kwargs: object) -> None:
        raise AuditServiceError(
            code="audit_unavailable",
            message="audit unavailable",
            details={},
        )

    monkeypatch.setattr(
        "app.api.dependencies.b2b_auth.AuditService.record_event",
        _raise_audit_error,
    )

    response = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={
            "X-API-Key": "b2b_invalid_unknown_secret",
            "X-Request-Id": "rid-b2b-audit-down",
        },
    )
    assert response.status_code == 401
    payload = response.json()["error"]
    assert payload["code"] == "invalid_api_key"
    assert payload["request_id"] == "rid-b2b-audit-down"
