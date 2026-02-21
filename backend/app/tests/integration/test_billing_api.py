from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService

client = TestClient(app)


def _cleanup_tables() -> None:
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(SubscriptionPlanChangeModel))
        db.execute(delete(PaymentAttemptModel))
        db.execute(delete(UserDailyQuotaUsageModel))
        db.execute(delete(UserSubscriptionModel))
        db.execute(delete(BillingPlanModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_and_get_access_token() -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": "billing-api-user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def test_billing_subscription_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/billing/subscription")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"
    assert response.json()["error"]["request_id"] != "n/a"


def test_billing_checkout_forbidden_for_non_user_role() -> None:
    _cleanup_tables()
    support_access_token = _register_user_with_role_and_token(
        "billing-support@example.com",
        "support",
    )
    response = client.post(
        "/v1/billing/checkout",
        headers={"Authorization": f"Bearer {support_access_token}"},
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "billing-role-forbidden-1",
        },
    )
    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "insufficient_role"
    assert payload["error"]["details"]["required_role"] == "user"


def test_billing_checkout_success_and_subscription_visibility() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    checkout = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "api-checkout-ok-1",
        },
    )
    assert checkout.status_code == 200
    assert checkout.json()["data"]["subscription"]["status"] == "active"
    assert checkout.json()["data"]["payment_status"] == "succeeded"

    status = client.get("/v1/billing/subscription", headers=headers)
    assert status.status_code == 200
    assert status.json()["data"]["status"] == "active"
    assert status.json()["data"]["plan"]["code"] == "basic-entry"


def test_billing_checkout_failure_then_retry_success() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    failed_checkout = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_fail",
            "idempotency_key": "api-checkout-fail-1",
        },
    )
    assert failed_checkout.status_code == 200
    assert failed_checkout.json()["data"]["subscription"]["status"] == "inactive"
    assert failed_checkout.json()["data"]["subscription"]["failure_reason"] is not None
    assert failed_checkout.json()["data"]["payment_status"] == "failed"

    retry = client.post(
        "/v1/billing/retry",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "api-checkout-retry-1",
        },
    )
    assert retry.status_code == 200
    assert retry.json()["data"]["subscription"]["status"] == "active"
    assert retry.json()["data"]["payment_status"] == "succeeded"


def test_billing_checkout_is_idempotent_for_same_key() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    first = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "api-checkout-idempotent-1",
        },
    )
    second = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_fail",
            "idempotency_key": "api-checkout-idempotent-1",
        },
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["payment_attempt_id"] == second.json()["data"]["payment_attempt_id"]
    assert second.json()["data"]["subscription"]["status"] == "active"


def test_billing_checkout_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "X-Request-Id": "rid-billing-429"}

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "7"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.billing.check_rate_limit", _always_rate_limited)

    response = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "billing-rate-limit-1",
        },
    )
    assert response.status_code == 429
    payload = response.json()
    assert payload["error"]["code"] == "rate_limit_exceeded"
    assert payload["error"]["request_id"] == "rid-billing-429"
    assert payload["error"]["details"]["retry_after"] == "7"


def test_billing_checkout_returns_503_when_audit_write_fails(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    def _raise_audit_error(*args: object, **kwargs: object) -> None:
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr("app.api.v1.routers.billing.AuditService.record_event", _raise_audit_error)

    response = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "billing-audit-fail-1",
        },
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "audit_unavailable"

    status = client.get("/v1/billing/subscription", headers=headers)
    assert status.status_code == 200
    assert status.json()["data"]["status"] == "inactive"
    assert status.json()["data"]["plan"] is None


def test_billing_quota_status_returns_usage_snapshot() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    checkout = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "api-checkout-quota-1",
        },
    )
    assert checkout.status_code == 200

    quota = client.get("/v1/billing/quota", headers=headers)
    assert quota.status_code == 200
    payload = quota.json()["data"]
    assert payload["limit"] == 5
    assert payload["consumed"] == 0
    assert payload["remaining"] == 5
    assert payload["blocked"] is False
    assert "reset_at" in payload


def test_billing_quota_status_forbidden_for_non_user_role() -> None:
    _cleanup_tables()
    support_access_token = _register_user_with_role_and_token(
        "billing-quota-support@example.com",
        "support",
    )
    response = client.get(
        "/v1/billing/quota",
        headers={"Authorization": f"Bearer {support_access_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_billing_plan_change_updates_subscription_and_quota_limit() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    checkout = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "api-checkout-plan-change-1",
        },
    )
    assert checkout.status_code == 200

    quota_before = client.get("/v1/billing/quota", headers=headers)
    assert quota_before.status_code == 200
    assert quota_before.json()["data"]["limit"] == 5

    change = client.post(
        "/v1/billing/plan-change",
        headers=headers,
        json={
            "target_plan_code": "premium-unlimited",
            "idempotency_key": "api-plan-change-1",
        },
    )
    assert change.status_code == 200
    payload = change.json()["data"]
    assert payload["subscription"]["status"] == "active"
    assert payload["subscription"]["plan"]["code"] == "premium-unlimited"
    assert payload["previous_plan_code"] == "basic-entry"
    assert payload["target_plan_code"] == "premium-unlimited"
    assert payload["plan_change_status"] == "succeeded"

    status = client.get("/v1/billing/subscription", headers=headers)
    assert status.status_code == 200
    assert status.json()["data"]["plan"]["code"] == "premium-unlimited"

    quota_after = client.get("/v1/billing/quota", headers=headers)
    assert quota_after.status_code == 200
    assert quota_after.json()["data"]["limit"] == 1000


def test_billing_plan_change_rejects_invalid_target_plan() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    checkout = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "api-checkout-plan-change-invalid-1",
        },
    )
    assert checkout.status_code == 200

    change = client.post(
        "/v1/billing/plan-change",
        headers=headers,
        json={
            "target_plan_code": "unknown-plan",
            "idempotency_key": "api-plan-change-invalid-1",
        },
    )
    assert change.status_code == 422
    assert change.json()["error"]["code"] == "invalid_target_plan"


def test_billing_plan_change_forbidden_for_non_user_role() -> None:
    _cleanup_tables()
    support_access_token = _register_user_with_role_and_token(
        "billing-plan-change-support@example.com",
        "support",
    )
    response = client.post(
        "/v1/billing/plan-change",
        headers={"Authorization": f"Bearer {support_access_token}"},
        json={
            "target_plan_code": "premium-unlimited",
            "idempotency_key": "api-plan-change-role-forbidden-1",
        },
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_billing_plan_change_is_idempotent_for_same_key() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    checkout = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "api-checkout-plan-change-idempotent-1",
        },
    )
    assert checkout.status_code == 200

    first = client.post(
        "/v1/billing/plan-change",
        headers=headers,
        json={
            "target_plan_code": "premium-unlimited",
            "idempotency_key": "api-plan-change-idempotent-1",
        },
    )
    second = client.post(
        "/v1/billing/plan-change",
        headers=headers,
        json={
            "target_plan_code": "basic-entry",
            "idempotency_key": "api-plan-change-idempotent-1",
        },
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["plan_change_id"] == second.json()["data"]["plan_change_id"]
    assert second.json()["data"]["target_plan_code"] == "premium-unlimited"


def test_billing_plan_change_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "X-Request-Id": "rid-plan-change-429"}

    checkout = client.post(
        "/v1/billing/checkout",
        headers=headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "api-checkout-plan-change-429-1",
        },
    )
    assert checkout.status_code == 200

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "8"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.billing.check_rate_limit", _always_rate_limited)

    response = client.post(
        "/v1/billing/plan-change",
        headers=headers,
        json={
            "target_plan_code": "premium-unlimited",
            "idempotency_key": "api-plan-change-429-1",
        },
    )
    assert response.status_code == 429
    payload = response.json()
    assert payload["error"]["code"] == "rate_limit_exceeded"
    assert payload["error"]["request_id"] == "rid-plan-change-429"
    assert payload["error"]["details"]["retry_after"] == "8"
