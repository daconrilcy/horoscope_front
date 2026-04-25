from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.core.rate_limit import RateLimitError
from app.infra.db.models.entitlement_mutation.alert.handling_event import (
    CanonicalEntitlementMutationAlertHandlingEventModel,
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


def _insert_history_event(
    *,
    alert_event_id: int,
    handling_status: str,
    handled_at: datetime,
    handled_by_user_id: int | None = 42,
    ops_comment: str | None = None,
    suppression_key: str | None = None,
    request_id: str | None = None,
) -> None:
    with SessionLocal() as db:
        db.add(
            CanonicalEntitlementMutationAlertHandlingEventModel(
                alert_event_id=alert_event_id,
                handling_status=handling_status,
                handled_by_user_id=handled_by_user_id,
                handled_at=handled_at,
                ops_comment=ops_comment,
                suppression_key=suppression_key,
                request_id=request_id,
            )
        )
        db.commit()


def _history_url(alert_event_id: int, query: str = "") -> str:
    suffix = f"?{query}" if query else ""
    return f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handling-history{suffix}"


def test_get_handling_history_empty_when_no_handlings() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-empty@example.com", "ops")
    alert_event_id = _create_event()

    response = client.get(
        _history_url(alert_event_id),
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-empty"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {"items": [], "total_count": 0, "limit": 50, "offset": 0}
    assert response.json()["meta"]["request_id"] == "rid-empty"


def test_get_handling_history_returns_single_event_after_first_handle() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-single@example.com", "ops")
    alert_event_id = _create_event()

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "suppressed", "ops_comment": "Known noise"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-first-handle"},
    )
    assert response.status_code == 201

    history = client.get(
        _history_url(alert_event_id),
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert history.status_code == 200
    items = history.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["event_type"] == "created"
    assert items[0]["handling_status"] == "suppressed"
    assert items[0]["ops_comment"] == "Known noise"


def test_get_handling_history_returns_multiple_events_on_status_change() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-multi@example.com", "ops")
    alert_event_id = _create_event()

    first = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "suppressed", "ops_comment": "noise"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-supp"},
    )
    second = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "resolved", "ops_comment": "fixed"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-resolved"},
    )
    assert first.status_code == 201
    assert second.status_code == 201

    history = client.get(
        _history_url(alert_event_id),
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    items = history.json()["data"]["items"]
    assert len(items) == 2
    assert [item["event_type"] for item in items] == ["updated", "created"]
    assert [item["handling_status"] for item in items] == ["resolved", "suppressed"]


def test_get_handling_history_no_duplicate_on_identical_re_post() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-noop@example.com", "ops")
    alert_event_id = _create_event()

    for request_id in ["rid-noop-1", "rid-noop-2"]:
        response = client.post(
            f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
            json={
                "handling_status": "suppressed",
                "ops_comment": "same-body",
                "suppression_key": "duplicate",
            },
            headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": request_id},
        )
        assert response.status_code == 201

    history = client.get(
        _history_url(alert_event_id),
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert history.status_code == 200
    assert history.json()["data"]["total_count"] == 1


def test_get_handling_history_stores_request_id() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-rid@example.com", "ops")
    alert_event_id = _create_event()

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "resolved"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-store-me"},
    )
    assert response.status_code == 201

    history = client.get(
        _history_url(alert_event_id),
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert history.json()["data"]["items"][0]["request_id"] == "rid-store-me"


def test_get_handling_history_ordered_by_handled_at_desc() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-order@example.com", "ops")
    alert_event_id = _create_event()
    _insert_history_event(
        alert_event_id=alert_event_id,
        handling_status="suppressed",
        handled_at=datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc),
        request_id="rid-old",
    )
    _insert_history_event(
        alert_event_id=alert_event_id,
        handling_status="resolved",
        handled_at=datetime(2026, 3, 29, 11, 0, tzinfo=timezone.utc),
        request_id="rid-new",
    )

    history = client.get(
        _history_url(alert_event_id),
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    items = history.json()["data"]["items"]
    assert [item["request_id"] for item in items] == ["rid-new", "rid-old"]


def test_get_handling_history_pagination() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-page@example.com", "ops")
    alert_event_id = _create_event()
    _insert_history_event(
        alert_event_id=alert_event_id,
        handling_status="suppressed",
        handled_at=datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc),
        request_id="rid-1",
    )
    _insert_history_event(
        alert_event_id=alert_event_id,
        handling_status="resolved",
        handled_at=datetime(2026, 3, 29, 11, 0, tzinfo=timezone.utc),
        request_id="rid-2",
    )

    history = client.get(
        _history_url(alert_event_id, "limit=1&offset=1"),
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert history.status_code == 200
    payload = history.json()["data"]
    assert payload["total_count"] == 2
    assert payload["limit"] == 1
    assert payload["offset"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["request_id"] == "rid-1"


def test_get_handling_history_returns_404_when_alert_event_not_found() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-404@example.com", "ops")

    response = client.get(
        _history_url(9999),
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-404"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "alert_event_not_found"
    assert response.json()["error"]["request_id"] == "rid-404"


def test_get_handling_history_requires_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_and_issue_token_with_role_claim(
        "ops-history-forbidden@example.com",
        "user",
        "user",
    )
    alert_event_id = _create_event()

    response = client.get(
        _history_url(alert_event_id),
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_get_handling_history_unauthenticated_returns_401() -> None:
    _cleanup_tables()
    alert_event_id = _create_event()

    response = client.get(_history_url(alert_event_id))

    assert response.status_code == 401


def test_get_handling_history_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-429@example.com", "ops")
    alert_event_id = _create_event()

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "7"},
            status_code=429,
        )

    monkeypatch.setattr(
        "app.api.v1.routers.ops_entitlement_mutation_audits.check_rate_limit",
        _always_rate_limited,
    )

    response = client.get(
        _history_url(alert_event_id),
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-429"},
    )

    assert response.status_code == 429
    assert response.json()["error"]["request_id"] == "rid-429"


def test_handle_alert_still_returns_201_after_61_44_changes() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-handle-201@example.com", "ops")
    alert_event_id = _create_event()

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle",
        json={"handling_status": "resolved", "ops_comment": "all good"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 201
    assert response.json()["data"]["handling_status"] == "resolved"


def test_batch_retry_still_excludes_suppressed_after_61_44_changes() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-history-batch@example.com", "ops")
    excluded_id = _create_event()
    included_id = _create_event()

    for event_id in [excluded_id]:
        response = client.post(
            f"/v1/ops/entitlements/mutation-audits/alerts/{event_id}/handle",
            json={"handling_status": "suppressed", "suppression_key": "duplicate"},
            headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-batch-supp"},
        )
        assert response.status_code == 201

    batch = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert batch.status_code == 200
    assert batch.json()["data"]["alert_event_ids"] == [included_id]
