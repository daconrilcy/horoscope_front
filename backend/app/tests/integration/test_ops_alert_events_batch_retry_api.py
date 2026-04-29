from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import select

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
    seed_ops_alert_audit,
    seed_ops_alert_event,
)

client = TestClient(app)


def test_post_retry_batch_dry_run_no_persistence() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-dry@example.com", "ops")
    with SessionLocal() as db:
        first_audit = seed_ops_alert_audit(db)
        second_audit = seed_ops_alert_audit(db)
        first = seed_ops_alert_event(db, audit_id=first_audit.id, delivery_status="failed")
        second = seed_ops_alert_event(db, audit_id=second_audit.id, delivery_status="failed")
        first_id = first.id
        second_id = second.id
        db.commit()

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["candidate_count"] == 2
    assert payload["retried_count"] == 2
    assert payload["sent_count"] == 0
    assert payload["failed_count"] == 0
    assert payload["skipped_count"] == 0
    assert payload["dry_run"] is True
    assert payload["alert_event_ids"] == [first_id, second_id]

    with SessionLocal() as db:
        assert db.query(CanonicalEntitlementMutationAlertDeliveryAttemptModel).count() == 0


def test_post_retry_batch_real_retries_multiple_failed() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-real@example.com", "ops")
    with SessionLocal() as db:
        first_audit = seed_ops_alert_audit(db)
        second_audit = seed_ops_alert_audit(db)
        first = seed_ops_alert_event(db, audit_id=first_audit.id, delivery_status="failed")
        second = seed_ops_alert_event(db, audit_id=second_audit.id, delivery_status="failed")
        first_id = first.id
        second_id = second.id
        db.commit()

    with patch(
        "app.services.canonical_entitlement.alert.batch_retry."
        "CanonicalEntitlementAlertDeliveryRuntime._deliver_webhook",
        return_value=(True, None),
    ):
        response = client.post(
            "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
            json={"limit": 10},
            headers={
                "Authorization": f"Bearer {ops_token}",
                "X-Request-Id": "rid-batch-real",
            },
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["candidate_count"] == 2
    assert payload["retried_count"] == 2
    assert payload["sent_count"] == 2
    assert payload["failed_count"] == 0
    assert payload["skipped_count"] == 0
    assert payload["dry_run"] is False
    assert payload["alert_event_ids"] == [first_id, second_id]

    with SessionLocal() as db:
        attempts = (
            db.execute(
                select(CanonicalEntitlementMutationAlertDeliveryAttemptModel).order_by(
                    CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id.asc(),
                    CanonicalEntitlementMutationAlertDeliveryAttemptModel.attempt_number.asc(),
                )
            )
            .scalars()
            .all()
        )
        events = (
            db.execute(
                select(CanonicalEntitlementMutationAlertEventModel).order_by(
                    CanonicalEntitlementMutationAlertEventModel.id.asc()
                )
            )
            .scalars()
            .all()
        )
        assert len(attempts) == 2
        assert [attempt.request_id for attempt in attempts] == ["rid-batch-real", "rid-batch-real"]
        assert [event.id for event in events] == [first_id, second_id]
        assert [event.delivery_status for event in events] == ["sent", "sent"]


def test_post_retry_batch_with_filter_by_feature_code() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-feature@example.com", "ops")
    with SessionLocal() as db:
        matching_audit = seed_ops_alert_audit(db)
        other_audit = seed_ops_alert_audit(db)
        matching = seed_ops_alert_event(db, audit_id=matching_audit.id, delivery_status="failed")
        matching.feature_code_snapshot = "feature-a"
        other = seed_ops_alert_event(db, audit_id=other_audit.id, delivery_status="failed")
        other.feature_code_snapshot = "feature-b"
        matching_id = matching.id
        db.commit()

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True, "feature_code": "feature-a"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["candidate_count"] == 1
    assert payload["alert_event_ids"] == [matching_id]


def test_post_retry_batch_with_filter_by_alert_kind() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-kind@example.com", "ops")
    with SessionLocal() as db:
        matching_audit = seed_ops_alert_audit(db)
        other_audit = seed_ops_alert_audit(db)
        matching = seed_ops_alert_event(db, audit_id=matching_audit.id, delivery_status="failed")
        matching.alert_kind = "sla_overdue"
        other = seed_ops_alert_event(db, audit_id=other_audit.id, delivery_status="failed")
        other.alert_kind = "sla_due_soon"
        matching_id = matching.id
        db.commit()

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True, "alert_kind": "sla_overdue"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["candidate_count"] == 1
    assert payload["alert_event_ids"] == [matching_id]


def test_post_retry_batch_with_filter_by_request_id_alias() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-request-id@example.com", "ops")
    with SessionLocal() as db:
        matching_audit = seed_ops_alert_audit(db)
        other_audit = seed_ops_alert_audit(db)
        matching = seed_ops_alert_event(db, audit_id=matching_audit.id, delivery_status="failed")
        matching.request_id = "req-match"
        other = seed_ops_alert_event(db, audit_id=other_audit.id, delivery_status="failed")
        other.request_id = "req-other"
        matching_id = matching.id
        db.commit()

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True, "request_id": "req-match"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["candidate_count"] == 1
    assert payload["alert_event_ids"] == [matching_id]


def test_post_retry_batch_respects_limit() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-limit@example.com", "ops")
    with SessionLocal() as db:
        first_audit = seed_ops_alert_audit(db)
        second_audit = seed_ops_alert_audit(db)
        third_audit = seed_ops_alert_audit(db)
        first = seed_ops_alert_event(db, audit_id=first_audit.id, delivery_status="failed")
        first.created_at = datetime(2026, 3, 29, 8, 0, tzinfo=timezone.utc)
        second = seed_ops_alert_event(db, audit_id=second_audit.id, delivery_status="failed")
        second.created_at = datetime(2026, 3, 29, 9, 0, tzinfo=timezone.utc)
        third = seed_ops_alert_event(db, audit_id=third_audit.id, delivery_status="failed")
        third.created_at = datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc)
        first_id = first.id
        second_id = second.id
        db.commit()

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 2, "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["candidate_count"] == 2
    assert payload["alert_event_ids"] == [first_id, second_id]


def test_post_retry_batch_requires_ops_role() -> None:
    cleanup_ops_alert_tables()
    user_token = register_user_and_issue_token_with_role_claim(
        "ops-batch-forbidden@example.com",
        "user",
        "user",
    )

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_post_retry_batch_returns_429_when_rate_limited(monkeypatch: object) -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-429@example.com", "ops")

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
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10},
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-batch-429",
        },
    )

    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-batch-429"


def test_post_retry_batch_returns_422_when_limit_missing() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-422-missing@example.com", "ops")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"dry_run": False},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 422


def test_post_retry_batch_returns_422_when_limit_exceeds_100() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-422-max@example.com", "ops")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 101},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 422


def test_post_retry_batch_empty_when_no_failed() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-empty@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        seed_ops_alert_event(db, audit_id=audit.id, delivery_status="sent")
        db.commit()

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "candidate_count": 0,
        "retried_count": 0,
        "sent_count": 0,
        "failed_count": 0,
        "skipped_count": 0,
        "dry_run": True,
        "alert_event_ids": [],
    }


def test_post_retry_batch_does_not_affect_sent_events() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-batch-sent@example.com", "ops")
    with SessionLocal() as db:
        audit = seed_ops_alert_audit(db)
        failed = seed_ops_alert_event(db, audit_id=audit.id, delivery_status="failed")
        sent = seed_ops_alert_event(db, audit_id=audit.id, delivery_status="sent")
        failed_id = failed.id
        sent_id = sent.id
        db.commit()

    with patch(
        "app.services.canonical_entitlement.alert.batch_retry."
        "CanonicalEntitlementAlertDeliveryRuntime._deliver_webhook",
        return_value=(True, None),
    ):
        response = client.post(
            "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
            json={"limit": 10},
            headers={"Authorization": f"Bearer {ops_token}"},
        )

    assert response.status_code == 200
    assert response.json()["data"]["alert_event_ids"] == [failed_id]

    with SessionLocal() as db:
        refreshed_failed = db.get(CanonicalEntitlementMutationAlertEventModel, failed_id)
        refreshed_sent = db.get(CanonicalEntitlementMutationAlertEventModel, sent_id)
        attempts = (
            db.execute(
                select(CanonicalEntitlementMutationAlertDeliveryAttemptModel).where(
                    CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id
                    == failed_id
                )
            )
            .scalars()
            .all()
        )
        assert refreshed_failed is not None
        assert refreshed_sent is not None
        assert refreshed_failed.delivery_status == "sent"
        assert refreshed_sent.delivery_status == "sent"
        assert len(attempts) == 1
