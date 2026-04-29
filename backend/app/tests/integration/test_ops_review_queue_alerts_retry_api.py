from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.rate_limit import RateLimitError
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.session import SessionLocal
from app.main import app
from app.tests.integration.ops_alert_helpers import (
    cleanup_ops_alert_tables,
    register_user_and_issue_token_with_role_claim,
    register_user_with_role_and_token,
    seed_ops_alert_attempt,
    seed_ops_alert_audit,
    seed_ops_alert_event,
)

client = TestClient(app)


def test_get_attempts_empty_for_alert_without_attempts() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-alerts@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        event = seed_ops_alert_event(db, audit_id=audit.id)
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
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-attempts@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        event = seed_ops_alert_event(db, audit_id=audit.id)
        seed_ops_alert_attempt(
            db, alert_event_id=event.id, attempt_number=1, delivery_status="failed"
        )
        seed_ops_alert_attempt(
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
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-retry@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        event = seed_ops_alert_event(db, audit_id=audit.id)
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
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-retry-dry@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        event = seed_ops_alert_event(db, audit_id=audit.id)
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
    cleanup_ops_alert_tables()
    user_token = register_user_and_issue_token_with_role_claim(
        "non-ops-retry@example.com",
        "user",
        "user",
    )
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        event = seed_ops_alert_event(db, audit_id=audit.id)
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
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-404@example.com", "ops")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/9999/retry",
        json={"dry_run": False},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "alert_event_not_found"


def test_post_retry_returns_409_for_non_failed_alert() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-409@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        event = seed_ops_alert_event(db, audit_id=audit.id, delivery_status="sent")
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
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-attempts-404@example.com", "ops")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts/9999/attempts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "alert_event_not_found"


def test_get_attempts_returns_429_when_rate_limited(monkeypatch: object) -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-attempts-429@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        event = seed_ops_alert_event(db, audit_id=audit.id)
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
        "app.services.canonical_entitlement.audit.api_mutation_audits.check_rate_limit",
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
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-retry-429@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        event = seed_ops_alert_event(db, audit_id=audit.id)
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
        "app.services.canonical_entitlement.audit.api_mutation_audits.check_rate_limit",
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
