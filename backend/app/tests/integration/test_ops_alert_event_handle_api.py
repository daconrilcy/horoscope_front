from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.rate_limit import RateLimitError
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.session import SessionLocal
from app.main import app
from app.tests.integration.test_ops_review_queue_alerts_retry_api import (
    _cleanup_tables,
    _register_user_and_issue_token_with_role_claim,
    _register_user_with_role_and_token,
    _seed_alert_event,
    _seed_audit,
)

client = TestClient(app)


def _create_event(*, delivery_status: str = "failed") -> int:
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id, delivery_status=delivery_status)
        db.commit()
        return event.id


def _insert_handling(
    *,
    alert_event_id: int,
    handling_status: str,
    handled_by_user_id: int | None = 42,
    ops_comment: str | None = None,
    suppression_key: str | None = None,
) -> None:
    with SessionLocal() as db:
        db.add(
            CanonicalEntitlementMutationAlertHandlingModel(
                alert_event_id=alert_event_id,
                handling_status=handling_status,
                handled_by_user_id=handled_by_user_id,
                handled_at=datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc),
                ops_comment=ops_comment,
                suppression_key=suppression_key,
            )
        )
        db.commit()


def test_post_handle_creates_suppressed_handling() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-handle-supp@example.com", "ops")
    alert_event_id = _create_event()

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-handle-supp"},
    )

    assert response.status_code == 201
    payload = response.json()["data"]
    assert payload["alert_event_id"] == alert_event_id
    assert payload["handling_status"] == "suppressed"
    assert payload["handled_by_user_id"] is not None
    assert response.json()["meta"]["request_id"] == "rid-handle-supp"


def test_post_handle_creates_resolved_handling() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-handle-res@example.com", "ops")
    alert_event_id = _create_event()

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "resolved"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 201
    assert response.json()["data"]["handling_status"] == "resolved"


def test_post_handle_updates_existing_handling() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-handle-update@example.com", "ops")
    alert_event_id = _create_event()
    _insert_handling(alert_event_id=alert_event_id, handling_status="suppressed")

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "resolved", "ops_comment": "Solved"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 201
    assert response.json()["data"]["handling_status"] == "resolved"
    assert response.json()["data"]["ops_comment"] == "Solved"

    with SessionLocal() as db:
        rows = db.execute(select(CanonicalEntitlementMutationAlertHandlingModel)).scalars().all()
        assert len(rows) == 1
        assert rows[0].handling_status == "resolved"


def test_post_handle_stores_ops_comment_and_suppression_key() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-handle-comment@example.com", "ops")
    alert_event_id = _create_event()

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={
            "handling_status": "suppressed",
            "ops_comment": "Known provider incident",
            "suppression_key": "provider-incident",
        },
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 201
    payload = response.json()["data"]
    assert payload["ops_comment"] == "Known provider incident"
    assert payload["suppression_key"] == "provider-incident"


def test_post_handle_returns_404_when_alert_event_not_found() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-handle-404@example.com", "ops")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/9999/handle",
        json={"handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-handle-404"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["request_id"] == "rid-handle-404"


def test_post_handle_requires_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_and_issue_token_with_role_claim(
        "ops-handle-forbidden@example.com",
        "user",
        "user",
    )
    alert_event_id = _create_event()

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_post_handle_returns_422_for_invalid_status() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-handle-422@example.com", "ops")
    alert_event_id = _create_event()

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "ignored"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 422


def test_post_handle_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-handle-429@example.com", "ops")
    alert_event_id = _create_event()

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
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-handle-429"},
    )

    assert response.status_code == 429
    assert response.json()["error"]["request_id"] == "rid-handle-429"


def test_list_alert_events_includes_handling_state() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-list-handling@example.com", "ops")
    alert_event_id = _create_event()
    _insert_handling(
        alert_event_id=alert_event_id,
        handling_status="suppressed",
        ops_comment="noise",
        suppression_key="duplicate",
    )

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["handling"]["handling_status"] == "suppressed"
    assert item["handling"]["ops_comment"] == "noise"
    assert item["handling"]["suppression_key"] == "duplicate"


def test_list_alert_events_filter_by_handling_status_suppressed() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-filter-supp@example.com", "ops")
    suppressed_id = _create_event()
    other_id = _create_event()
    _insert_handling(alert_event_id=suppressed_id, handling_status="suppressed")
    _insert_handling(alert_event_id=other_id, handling_status="resolved")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts?handling_status=suppressed",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["data"]["items"]] == [suppressed_id]


def test_list_alert_events_filter_by_handling_status_resolved() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-filter-res@example.com", "ops")
    resolved_id = _create_event()
    other_id = _create_event()
    _insert_handling(alert_event_id=resolved_id, handling_status="resolved")
    _insert_handling(alert_event_id=other_id, handling_status="suppressed")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts?handling_status=resolved",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["data"]["items"]] == [resolved_id]


def test_list_alert_events_filter_by_handling_status_pending_retry() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-filter-pending@example.com", "ops")
    pending_id = _create_event(delivery_status="failed")
    handled_id = _create_event(delivery_status="failed")
    sent_id = _create_event(delivery_status="sent")
    _insert_handling(alert_event_id=handled_id, handling_status="suppressed")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts?handling_status=pending_retry",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["data"]["items"]] == [pending_id]
    assert sent_id not in [item["id"] for item in response.json()["data"]["items"]]


def test_list_alert_events_pending_retry_virtual_for_failed_without_handling() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-pending-virtual@example.com", "ops")
    alert_event_id = _create_event(delivery_status="failed")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["id"] == alert_event_id
    assert item["handling"]["handling_status"] == "pending_retry"


def test_summary_includes_suppressed_and_resolved_counts() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-summary-handling@example.com", "ops")
    suppressed_id = _create_event()
    resolved_id = _create_event()
    _insert_handling(alert_event_id=suppressed_id, handling_status="suppressed")
    _insert_handling(alert_event_id=resolved_id, handling_status="resolved")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts/summary",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["suppressed_count"] == 1
    assert data["resolved_count"] == 1


def test_batch_retry_excludes_suppressed_alerts() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-excl-supp@example.com", "ops")
    excluded_id = _create_event()
    included_id = _create_event()
    _insert_handling(alert_event_id=excluded_id, handling_status="suppressed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["alert_event_ids"] == [included_id]


def test_batch_retry_excludes_resolved_alerts() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-excl-res@example.com", "ops")
    excluded_id = _create_event()
    included_id = _create_event()
    _insert_handling(alert_event_id=excluded_id, handling_status="resolved")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["alert_event_ids"] == [included_id]


def test_batch_retry_includes_pending_retry_alerts() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-pending@example.com", "ops")
    pending_id = _create_event()

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["alert_event_ids"] == [pending_id]


def test_retryable_false_when_suppressed() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-retryable-supp@example.com", "ops")
    alert_event_id = _create_event()
    _insert_handling(alert_event_id=alert_event_id, handling_status="suppressed")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["retryable"] is False


def test_retryable_false_when_resolved() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-retryable-res@example.com", "ops")
    alert_event_id = _create_event()
    _insert_handling(alert_event_id=alert_event_id, handling_status="resolved")

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["retryable"] is False


def test_retryable_true_when_pending_retry() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-retryable-pending@example.com", "ops")
    alert_event_id = _create_event()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/alerts",
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["id"] == alert_event_id
    assert item["retryable"] is True
