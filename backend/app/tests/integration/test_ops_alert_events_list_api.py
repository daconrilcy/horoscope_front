from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.core.rate_limit import RateLimitError
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
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


def test_get_alerts_list_empty() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-list-empty@example.com", "ops")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["items"] == []
    assert payload["total_count"] == 0
    assert payload["page"] == 1
    assert payload["page_size"] == 20


def test_get_alerts_list_returns_items_with_derived_fields() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-list-items@example.com", "ops")
    with SessionLocal() as db:
        first_audit = seed_ops_alert_audit(db)
        second_audit = seed_ops_alert_audit(db)
        older = seed_ops_alert_event(db, audit_id=first_audit.id, delivery_status="failed")
        older.created_at = datetime(2026, 3, 29, 8, 0, tzinfo=timezone.utc)
        newer = seed_ops_alert_event(db, audit_id=second_audit.id, delivery_status="sent")
        newer.created_at = datetime(2026, 3, 29, 9, 0, tzinfo=timezone.utc)
        seed_ops_alert_attempt(
            db, alert_event_id=older.id, attempt_number=1, delivery_status="failed"
        )
        seed_ops_alert_attempt(
            db, alert_event_id=older.id, attempt_number=3, delivery_status="sent"
        )
        seed_ops_alert_attempt(
            db, alert_event_id=older.id, attempt_number=2, delivery_status="failed"
        )
        db.commit()
        newer_id = newer.id
        older_id = older.id

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert [item["id"] for item in items] == [newer_id, older_id]
    assert items[0]["attempt_count"] == 0
    assert items[0]["last_attempt_number"] is None
    assert items[0]["last_attempt_status"] is None
    assert items[0]["retryable"] is False
    assert items[1]["attempt_count"] == 3
    assert items[1]["last_attempt_number"] == 3
    assert items[1]["last_attempt_status"] == "sent"
    assert items[1]["retryable"] is True


def test_get_alerts_list_filter_by_delivery_status_failed() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-list-filter-status@example.com", "ops")
    with SessionLocal() as db:
        audit_one = seed_ops_alert_audit(db)
        audit_two = seed_ops_alert_audit(db)
        failed_event = seed_ops_alert_event(db, audit_id=audit_one.id, delivery_status="failed")
        seed_ops_alert_event(db, audit_id=audit_two.id, delivery_status="sent")
        db.commit()
        failed_event_id = failed_event.id

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts?delivery_status=failed",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 1
    assert [item["id"] for item in payload["items"]] == [failed_event_id]


def test_get_alerts_list_filter_by_audit_id() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-list-filter-audit@example.com", "ops")
    with SessionLocal() as db:
        matching_audit = seed_ops_alert_audit(db)
        other_audit = seed_ops_alert_audit(db)
        matching_event = seed_ops_alert_event(db, audit_id=matching_audit.id)
        seed_ops_alert_event(db, audit_id=other_audit.id)
        db.commit()
        matching_audit_id = matching_audit.id
        matching_event_id = matching_event.id

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/alerts?audit_id={matching_audit_id}",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 1
    assert [item["id"] for item in payload["items"]] == [matching_event_id]


def test_get_alerts_list_filter_by_feature_code() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-list-filter-feature@example.com", "ops")
    with SessionLocal() as db:
        audit_one = seed_ops_alert_audit(db)
        audit_two = seed_ops_alert_audit(db)
        matching_event = seed_ops_alert_event(db, audit_id=audit_one.id)
        other_event = seed_ops_alert_event(db, audit_id=audit_two.id)
        matching_event.feature_code_snapshot = "feature-a"
        other_event.feature_code_snapshot = "feature-b"
        db.commit()
        matching_event_id = matching_event.id

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts?feature_code=feature-a",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 1
    assert [item["id"] for item in payload["items"]] == [matching_event_id]


def test_get_alerts_list_pagination() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-list-pagination@example.com", "ops")
    with SessionLocal() as db:
        for index in range(3):
            audit = seed_ops_alert_audit(db)
            event = seed_ops_alert_event(db, audit_id=audit.id)
            event.created_at = datetime(2026, 3, 29, 10 + index, 0, tzinfo=timezone.utc)
        db.commit()
        expected_page_two_id = (
            db.query(CanonicalEntitlementMutationAlertEventModel)
            .order_by(
                CanonicalEntitlementMutationAlertEventModel.created_at.desc(),
                CanonicalEntitlementMutationAlertEventModel.id.desc(),
            )
            .offset(1)
            .limit(1)
            .one()
            .id
        )

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts?page=2&page_size=1",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 3
    assert payload["page"] == 2
    assert payload["page_size"] == 1
    assert [item["id"] for item in payload["items"]] == [expected_page_two_id]


def test_get_alerts_list_pagination_out_of_range_keeps_total_count() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token(
        "ops-list-pagination-oob@example.com",
        "ops",
    )
    with SessionLocal() as db:
        for _ in range(2):
            audit = seed_ops_alert_audit(db)
            seed_ops_alert_event(db, audit_id=audit.id)
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts?page=3&page_size=1",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["items"] == []
    assert payload["total_count"] == 2
    assert payload["page"] == 3
    assert payload["page_size"] == 1


def test_get_alerts_list_requires_ops_role() -> None:
    cleanup_ops_alert_tables()
    user_token = register_user_and_issue_token_with_role_claim(
        "ops-list-forbidden@example.com",
        "user",
        "user",
    )

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_get_alerts_list_returns_429_when_rate_limited(monkeypatch: object) -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-list-429@example.com", "ops")

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
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-list-429",
        },
    )

    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-list-429"


def test_get_alerts_summary_empty() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-summary-empty@example.com", "ops")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts/summary",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "total_count": 0,
        "failed_count": 0,
        "sent_count": 0,
        "retryable_count": 0,
        "webhook_failed_count": 0,
        "log_sent_count": 0,
        "suppressed_count": 0,
        "resolved_count": 0,
    }


def test_get_alerts_summary_counts_correctly() -> None:
    cleanup_ops_alert_tables()
    ops_token = register_user_with_role_and_token("ops-summary-counts@example.com", "ops")
    with SessionLocal() as db:
        audit_one = seed_ops_alert_audit(db)
        audit_two = seed_ops_alert_audit(db)
        audit_three = seed_ops_alert_audit(db)
        failed_webhook = seed_ops_alert_event(db, audit_id=audit_one.id, delivery_status="failed")
        sent_log = seed_ops_alert_event(db, audit_id=audit_two.id, delivery_status="sent")
        sent_other = seed_ops_alert_event(db, audit_id=audit_three.id, delivery_status="sent")
        failed_webhook.feature_code_snapshot = "feature-a"
        sent_log.feature_code_snapshot = "feature-a"
        sent_other.feature_code_snapshot = "feature-b"
        sent_log.delivery_channel = "log"
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts/summary?feature_code=feature-a",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "total_count": 2,
        "failed_count": 1,
        "sent_count": 1,
        "retryable_count": 1,
        "webhook_failed_count": 1,
        "log_sent_count": 1,
        "suppressed_count": 0,
        "resolved_count": 0,
    }


def test_get_alerts_summary_requires_ops_role() -> None:
    cleanup_ops_alert_tables()
    user_token = register_user_and_issue_token_with_role_claim(
        "ops-summary-forbidden@example.com",
        "user",
        "user",
    )

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts/summary",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"
