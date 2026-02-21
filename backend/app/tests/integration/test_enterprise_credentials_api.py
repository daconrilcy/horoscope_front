from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(AuditEventModel))
        db.execute(delete(EnterpriseApiCredentialModel))
        db.execute(delete(EnterpriseAccountModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_user_with_role(email: str, role: str) -> tuple[int, str]:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.user.id, auth.tokens.access_token


def _attach_enterprise_account(admin_user_id: int, status: str = "active") -> None:
    with SessionLocal() as db:
        db.add(
            EnterpriseAccountModel(
                admin_user_id=admin_user_id,
                company_name="Acme Media",
                status=status,
            )
        )
        db.commit()


def test_enterprise_credentials_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/b2b/credentials")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_enterprise_credentials_forbidden_for_non_enterprise_admin() -> None:
    _cleanup_tables()
    _, token = _register_user_with_role("b2b-user@example.com", "user")
    response = client.get("/v1/b2b/credentials", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_generate_and_rotate_enterprise_credentials_with_audit() -> None:
    _cleanup_tables()
    admin_user_id, token = _register_user_with_role(
        "b2b-admin@example.com",
        "enterprise_admin",
    )
    _attach_enterprise_account(admin_user_id)

    generate = client.post(
        "/v1/b2b/credentials/generate",
        headers={"Authorization": f"Bearer {token}", "X-Request-Id": "rid-b2b-create"},
    )
    assert generate.status_code == 200
    created = generate.json()["data"]
    assert created["api_key"].startswith("b2b_")
    assert created["status"] == "active"

    rotate = client.post(
        "/v1/b2b/credentials/rotate",
        headers={"Authorization": f"Bearer {token}", "X-Request-Id": "rid-b2b-rotate"},
    )
    assert rotate.status_code == 200
    rotated = rotate.json()["data"]
    assert rotated["api_key"].startswith("b2b_")
    assert rotated["credential_id"] != created["credential_id"]

    listing = client.get(
        "/v1/b2b/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listing.status_code == 200
    payload = listing.json()["data"]
    assert payload["has_active_credential"] is True
    assert len(payload["credentials"]) == 2

    with SessionLocal() as db:
        create_audit = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-b2b-create")
            .where(AuditEventModel.action == "b2b_api_key_create")
            .limit(1)
        )
        rotate_audit = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-b2b-rotate")
            .where(AuditEventModel.action == "b2b_api_key_rotate")
            .limit(1)
        )
        assert create_audit is not None
        assert create_audit.status == "success"
        assert rotate_audit is not None
        assert rotate_audit.status == "success"


def test_generate_requires_active_enterprise_account() -> None:
    _cleanup_tables()
    admin_user_id, token = _register_user_with_role(
        "b2b-admin-inactive@example.com",
        "enterprise_admin",
    )
    _attach_enterprise_account(admin_user_id, status="inactive")
    response = client.post(
        "/v1/b2b/credentials/generate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "enterprise_account_inactive"


def test_enterprise_credentials_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    admin_user_id, token = _register_user_with_role(
        "b2b-admin-429@example.com",
        "enterprise_admin",
    )
    _attach_enterprise_account(admin_user_id)
    headers = {"Authorization": f"Bearer {token}", "X-Request-Id": "rid-b2b-429"}

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "5"},
            status_code=429,
        )

    monkeypatch.setattr(
        "app.api.v1.routers.enterprise_credentials.check_rate_limit",
        _always_rate_limited,
    )

    response = client.get("/v1/b2b/credentials", headers=headers)
    assert response.status_code == 429
    assert response.json()["error"]["request_id"] == "rid-b2b-429"


def test_generate_returns_503_when_audit_unavailable(monkeypatch: object) -> None:
    _cleanup_tables()
    admin_user_id, token = _register_user_with_role(
        "b2b-admin-audit-fail@example.com",
        "enterprise_admin",
    )
    _attach_enterprise_account(admin_user_id)

    from app.services.audit_service import AuditServiceError

    def _audit_unavailable(*args: object, **kwargs: object) -> None:
        raise AuditServiceError(
            code="audit_unavailable",
            message="audit unavailable",
            details={},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.enterprise_credentials._record_audit_event",
        _audit_unavailable,
    )

    response = client.post(
        "/v1/b2b/credentials/generate",
        headers={"Authorization": f"Bearer {token}", "X-Request-Id": "rid-b2b-audit-fail"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "audit_unavailable"

    with SessionLocal() as db:
        credentials = db.scalars(select(EnterpriseApiCredentialModel)).all()
        assert credentials == []
