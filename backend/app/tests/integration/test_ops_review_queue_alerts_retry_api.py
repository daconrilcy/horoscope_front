from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.rate_limit import RateLimitError
from app.core.security import create_access_token
from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling_event import (
    CanonicalEntitlementMutationAlertHandlingEventModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserModel))
        db.execute(delete(CanonicalEntitlementMutationAlertDeliveryAttemptModel))
        db.execute(delete(CanonicalEntitlementMutationAlertHandlingEventModel))
        db.execute(delete(CanonicalEntitlementMutationAlertHandlingModel))
        db.execute(delete(CanonicalEntitlementMutationAlertEventModel))
        db.execute(delete(CanonicalEntitlementMutationAuditModel))
        db.commit()


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _register_user_and_issue_token_with_role_claim(email: str, role: str, claim_role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return create_access_token(subject=str(auth.user.id), role=claim_role)


def _seed_audit(db) -> CanonicalEntitlementMutationAuditModel:
    audit = CanonicalEntitlementMutationAuditModel(
        operation="upsert_plan_feature_configuration",
        plan_id=1,
        plan_code_snapshot="premium",
        feature_code="test_feature",
        actor_type="user",
        actor_identifier="user@test.com",
        source_origin="manual",
        before_payload={"is_enabled": True},
        after_payload={"is_enabled": False},
    )
    db.add(audit)
    db.flush()
    return audit


def _seed_alert_event(
    db,
    *,
    audit_id: int,
    delivery_status: str = "failed",
) -> CanonicalEntitlementMutationAlertEventModel:
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"audit:{audit_id}:review:pending_review:sla:overdue:{delivery_status}",
        alert_kind="sla_overdue",
        risk_level_snapshot="high",
        effective_review_status_snapshot="pending_review",
        feature_code_snapshot="test_feature",
        plan_id_snapshot=1,
        plan_code_snapshot="premium",
        actor_type_snapshot="user",
        actor_identifier_snapshot="user@test.com",
        sla_target_seconds_snapshot=14_400,
        age_seconds_snapshot=99_999,
        delivery_channel="webhook",
        delivery_status=delivery_status,
        delivery_error=None if delivery_status == "sent" else "Connection refused",
        payload={"alert_kind": "sla_overdue", "audit_id": audit_id},
    )
    db.add(event)
    db.flush()
    return event


def _seed_attempt(
    db,
    *,
    alert_event_id: int,
    attempt_number: int,
    delivery_status: str,
    request_id: str | None = None,
) -> CanonicalEntitlementMutationAlertDeliveryAttemptModel:
    attempt = CanonicalEntitlementMutationAlertDeliveryAttemptModel(
        alert_event_id=alert_event_id,
        attempt_number=attempt_number,
        delivery_channel="webhook",
        delivery_status=delivery_status,
        delivery_error=None if delivery_status == "sent" else "Timeout",
        request_id=request_id,
        payload={"alert_event_id": alert_event_id, "attempt_number": attempt_number},
    )
    db.add(attempt)
    db.flush()
    return attempt


def test_get_attempts_empty_for_alert_without_attempts() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-alerts@example.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id)
        db.commit()
        alert_event_id = event.id

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/attempts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["items"] == []
    assert payload["total_count"] == 0


def test_get_attempts_returns_attempt_history() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-attempts@example.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id)
        _seed_attempt(db, alert_event_id=event.id, attempt_number=1, delivery_status="failed")
        _seed_attempt(
            db,
            alert_event_id=event.id,
            attempt_number=2,
            delivery_status="sent",
            request_id="req-2",
        )
        db.commit()
        alert_event_id = event.id

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/attempts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert [item["attempt_number"] for item in items] == [1, 2]
    assert items[1]["delivery_status"] == "sent"
    assert items[1]["request_id"] == "req-2"


def test_post_retry_creates_new_attempt() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-retry@example.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id)
        db.commit()
        alert_event_id = event.id

    with patch(
        "app.services.canonical_entitlement.alert.retry."
        "CanonicalEntitlementAlertDeliveryRuntime._deliver_webhook",
        return_value=(True, None),
    ):
        response = client.post(
            f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/retry",
            json={"dry_run": False},
            headers={
                "Authorization": f"Bearer {ops_token}",
                "X-Request-Id": "rid-retry",
            },
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["alert_event_id"] == alert_event_id
    assert payload["attempted"] is True
    assert payload["delivery_status"] == "sent"
    assert payload["attempt_number"] == 1
    assert payload["request_id"] == "rid-retry"

    with SessionLocal() as db:
        attempts = (
            db.query(CanonicalEntitlementMutationAlertDeliveryAttemptModel)
            .filter(
                CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id
                == alert_event_id
            )
            .all()
        )
        event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
        assert len(attempts) == 1
        assert attempts[0].request_id == "rid-retry"
        assert event is not None
        assert event.delivery_status == "sent"


def test_post_retry_dry_run_creates_no_attempt() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-retry-dry@example.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id)
        db.commit()
        alert_event_id = event.id

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/retry",
        json={"dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["attempted"] is True
    assert payload["delivery_status"] == "failed"
    assert payload["attempt_number"] is None

    with SessionLocal() as db:
        assert (
            db.query(CanonicalEntitlementMutationAlertDeliveryAttemptModel)
            .filter(
                CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id
                == alert_event_id
            )
            .count()
            == 0
        )


def test_post_retry_requires_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_and_issue_token_with_role_claim(
        "non-ops-retry@example.com",
        "user",
        "user",
    )
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id)
        db.commit()
        alert_event_id = event.id

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/retry",
        json={"dry_run": False},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_post_retry_returns_404_for_unknown_alert() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-404@example.com", "ops")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/9999/retry",
        json={"dry_run": False},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "alert_event_not_found"


def test_post_retry_returns_409_for_non_failed_alert() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-409@example.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id, delivery_status="sent")
        db.commit()
        alert_event_id = event.id

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/retry",
        json={"dry_run": False},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "alert_event_not_retryable"


def test_get_attempts_returns_404_for_unknown_alert() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-attempts-404@example.com", "ops")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts/9999/attempts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "alert_event_not_found"


def test_get_attempts_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-attempts-429@example.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id)
        db.commit()
        alert_event_id = event.id

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "7"},
            status_code=429,
        )

    monkeypatch.setattr(
        "app.api.v1.router_logic.ops.entitlement_mutation_audits.check_rate_limit",
        _always_rate_limited,
    )

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/attempts",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-attempts-429",
        },
    )

    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-attempts-429"


def test_post_retry_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-retry-429@example.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id)
        db.commit()
        alert_event_id = event.id

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "7"},
            status_code=429,
        )

    monkeypatch.setattr(
        "app.api.v1.router_logic.ops.entitlement_mutation_audits.check_rate_limit",
        _always_rate_limited,
    )

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/retry",
        json={"dry_run": False},
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-retry-429",
        },
    )

    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-retry-429"
