from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.privacy import UserPrivacyRequestModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.privacy_service import PrivacyServiceError

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            UserPrivacyRequestModel,
            ChatMessageModel,
            ChatConversationModel,
            ChartResultModel,
            UserDailyQuotaUsageModel,
            PaymentAttemptModel,
            SubscriptionPlanChangeModel,
            UserSubscriptionModel,
            BillingPlanModel,
            UserBirthProfileModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _register_and_get_access_token() -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": "privacy-api-user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def test_privacy_export_requires_token() -> None:
    _cleanup_tables()
    response = client.post("/v1/privacy/export")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_privacy_export_request_and_status_success() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    export_response = client.post("/v1/privacy/export", headers=headers)
    assert export_response.status_code == 200
    payload = export_response.json()["data"]
    assert payload["request_kind"] == "export"
    assert payload["status"] == "completed"
    assert payload["result_data"]["user"]["email"] == "privacy-api-user@example.com"

    status_response = client.get("/v1/privacy/export", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["data"]["request_kind"] == "export"


def test_privacy_export_status_returns_404_when_no_request() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get("/v1/privacy/export", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "privacy_not_found"


def test_privacy_delete_request_requires_confirmation() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/privacy/delete",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"confirmation": "NO"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "privacy_request_invalid"


def test_privacy_delete_anonymizes_account_and_removes_profile() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        owner = db.scalar(
            select(UserModel).where(UserModel.email == "privacy-api-user@example.com").limit(1)
        )
        assert owner is not None
        db.add(
            UserBirthProfileModel(
                user_id=owner.id,
                birth_date=date(1990, 1, 1),
                birth_time="10:30:00",
                birth_place="Paris",
                birth_timezone="Europe/Paris",
            )
        )
        db.commit()

    delete_response = client.post(
        "/v1/privacy/delete",
        headers=headers,
        json={"confirmation": "DELETE"},
    )
    assert delete_response.status_code == 200
    payload = delete_response.json()["data"]
    assert payload["request_kind"] == "delete"
    assert payload["status"] == "completed"

    status_response = client.get("/v1/privacy/delete", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["data"]["request_kind"] == "delete"

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email.like("deleted-user-%")).limit(1))
        assert user is not None
        assert user.email.startswith("deleted-user-")
        profile = db.scalar(
            select(UserBirthProfileModel).where(UserBirthProfileModel.user_id == user.id).limit(1)
        )
        assert profile is None


def test_privacy_endpoints_forbidden_for_non_user_role() -> None:
    _cleanup_tables()
    support_token = _register_user_with_role_and_token("privacy-support@example.com", "support")
    headers = {"Authorization": f"Bearer {support_token}"}
    response = client.post("/v1/privacy/export", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_privacy_export_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "X-Request-Id": "rid-privacy-429"}

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "9"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.privacy.check_rate_limit", _always_rate_limited)

    response = client.post("/v1/privacy/export", headers=headers)
    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-privacy-429"
    assert payload["details"]["retry_after"] == "9"


def test_privacy_export_uses_user_plan_rate_limit_key(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    seen_keys: list[str] = []

    def _capture_rate_limit(*, key: str, limit: int, window_seconds: int) -> None:
        seen_keys.append(key)

    monkeypatch.setattr("app.api.v1.routers.privacy.check_rate_limit", _capture_rate_limit)

    response = client.post("/v1/privacy/export", headers=headers)
    assert response.status_code == 200
    assert any(key.startswith("privacy:user_plan:") for key in seen_keys)


def test_privacy_export_is_idempotent_for_repeated_posts() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    first = client.post("/v1/privacy/export", headers=headers)
    second = client.post("/v1/privacy/export", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["request_id"] == second.json()["data"]["request_id"]


def test_privacy_export_returns_503_when_audit_write_fails(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    def _raise_audit_error(*args: object, **kwargs: object) -> None:
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr("app.api.v1.routers.privacy.AuditService.record_event", _raise_audit_error)

    response = client.post("/v1/privacy/export", headers=headers)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "audit_unavailable"


def test_privacy_export_returns_503_when_service_error_and_audit_write_fails(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    def _raise_privacy_error(*args: object, **kwargs: object) -> None:
        raise PrivacyServiceError(
            code="privacy_request_conflict",
            message="an export request is already in progress",
            details={"request_kind": "export"},
        )

    def _raise_audit_error(*args: object, **kwargs: object) -> None:
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(
        "app.api.v1.routers.privacy.PrivacyService.request_export",
        _raise_privacy_error,
    )
    monkeypatch.setattr("app.api.v1.routers.privacy.AuditService.record_event", _raise_audit_error)

    response = client.post("/v1/privacy/export", headers=headers)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "audit_unavailable"


def test_privacy_delete_returns_503_when_validation_error_and_audit_write_fails(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    def _raise_audit_error(*args: object, **kwargs: object) -> None:
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr("app.api.v1.routers.privacy.AuditService.record_event", _raise_audit_error)

    response = client.post("/v1/privacy/delete", headers=headers, json={})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "audit_unavailable"


def test_privacy_delete_invalid_confirmation_writes_failed_audit(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    seen_statuses: list[str] = []
    seen_error_codes: list[str | None] = []

    def _capture_record_event(*args: object, **kwargs: object) -> None:
        payload = kwargs["payload"]
        seen_statuses.append(payload.status)
        details = payload.details if isinstance(payload.details, dict) else {}
        error_code = details.get("error_code")
        seen_error_codes.append(error_code if isinstance(error_code, str) else None)

    monkeypatch.setattr(
        "app.api.v1.routers.privacy.AuditService.record_event",
        _capture_record_event,
    )

    response = client.post(
        "/v1/privacy/delete",
        headers=headers,
        json={"confirmation": "NO"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "privacy_request_invalid"
    assert seen_statuses == ["failed"]
    assert seen_error_codes == ["privacy_request_invalid"]
