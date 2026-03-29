from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.rate_limit import RateLimitError
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling import (
    CanonicalEntitlementMutationAlertEventHandlingModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling_event import (
    CanonicalEntitlementMutationAlertEventHandlingEventModel,
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


def _create_event(
    *,
    delivery_status: str = "failed",
    alert_kind: str = "sla_overdue",
    feature_code: str = "test_feature",
) -> int:
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(
            db,
            audit_id=audit.id,
            delivery_status=delivery_status,
        )
        event.alert_kind = alert_kind
        event.feature_code_snapshot = feature_code
        event.payload = {
            "alert_kind": alert_kind,
            "audit_id": audit.id,
            "feature_code": feature_code,
        }
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
            CanonicalEntitlementMutationAlertEventHandlingModel(
                alert_event_id=alert_event_id,
                handling_status=handling_status,
                handled_by_user_id=handled_by_user_id,
                handled_at=datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc),
                ops_comment=ops_comment,
                suppression_key=suppression_key,
            )
        )
        db.commit()


def _count_handlings() -> int:
    with SessionLocal() as db:
        return len(
            db.execute(select(CanonicalEntitlementMutationAlertEventHandlingModel)).scalars().all()
        )


def _count_handling_events(*, alert_event_id: int | None = None) -> int:
    with SessionLocal() as db:
        query = select(CanonicalEntitlementMutationAlertEventHandlingEventModel)
        if alert_event_id is not None:
            query = query.where(
                CanonicalEntitlementMutationAlertEventHandlingEventModel.alert_event_id
                == alert_event_id
            )
        return len(db.execute(query).scalars().all())


def test_batch_handle_suppresses_failed_alerts() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-supp@example.com", "ops")
    first_id = _create_event(delivery_status="failed")
    second_id = _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-batch-supp"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["candidate_count"] == 2
    assert data["handled_count"] == 2
    assert data["skipped_count"] == 0
    assert data["alert_event_ids"] == [first_id, second_id]

    with SessionLocal() as db:
        rows = (
            db.execute(select(CanonicalEntitlementMutationAlertEventHandlingModel)).scalars().all()
        )
        assert [row.handling_status for row in rows] == ["suppressed", "suppressed"]


def test_batch_handle_resolves_failed_alerts() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-res@example.com", "ops")
    alert_event_id = _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "resolved"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["handled_count"] == 1

    with SessionLocal() as db:
        row = db.execute(
            select(CanonicalEntitlementMutationAlertEventHandlingModel).where(
                CanonicalEntitlementMutationAlertEventHandlingModel.alert_event_id == alert_event_id
            )
        ).scalar_one_or_none()
        assert row is not None
        assert row.handling_status == "resolved"


def test_batch_handle_dry_run_does_not_persist() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-dry@example.com", "ops")
    _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "suppressed", "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["dry_run"] is True
    assert response.json()["data"]["handled_count"] == 1
    assert _count_handlings() == 0


def test_batch_handle_skips_already_handled_same_state() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-skip@example.com", "ops")
    alert_event_id = _create_event(delivery_status="failed")
    _insert_handling(
        alert_event_id=alert_event_id,
        handling_status="suppressed",
        ops_comment="noise",
        suppression_key="duplicate",
    )

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={
            "limit": 10,
            "handling_status": "suppressed",
            "ops_comment": "noise",
            "suppression_key": "duplicate",
        },
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["handled_count"] == 0
    assert response.json()["data"]["skipped_count"] == 1
    assert _count_handling_events(alert_event_id=alert_event_id) == 0


def test_batch_handle_rehandles_when_state_changes() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-rehandle@example.com", "ops")
    alert_event_id = _create_event(delivery_status="failed")
    _insert_handling(alert_event_id=alert_event_id, handling_status="suppressed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "resolved"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-batch-rehandle"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["handled_count"] == 1
    assert _count_handling_events(alert_event_id=alert_event_id) == 1

    with SessionLocal() as db:
        row = db.execute(
            select(CanonicalEntitlementMutationAlertEventHandlingModel).where(
                CanonicalEntitlementMutationAlertEventHandlingModel.alert_event_id == alert_event_id
            )
        ).scalar_one_or_none()
        assert row is not None
        assert row.handling_status == "resolved"


def test_batch_handle_limit_is_respected() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-limit@example.com", "ops")
    first_id = _create_event(delivery_status="failed")
    second_id = _create_event(delivery_status="failed")
    _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 2, "handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["candidate_count"] == 2
    assert response.json()["data"]["alert_event_ids"] == [first_id, second_id]


def test_batch_handle_appends_history_events_for_each_handled() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-history@example.com", "ops")
    _create_event(delivery_status="failed")
    _create_event(delivery_status="sent")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert _count_handling_events() == 2


def test_batch_handle_no_history_event_on_skip() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-no-history@example.com", "ops")
    alert_event_id = _create_event(delivery_status="failed")
    _insert_handling(
        alert_event_id=alert_event_id,
        handling_status="resolved",
        ops_comment="done",
        suppression_key=None,
    )

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "resolved", "ops_comment": "done"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["skipped_count"] == 1
    assert _count_handling_events(alert_event_id=alert_event_id) == 0


def test_batch_handle_requires_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_and_issue_token_with_role_claim(
        "ops-batch-handle-forbidden@example.com",
        "user",
        "user",
    )
    _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_batch_handle_unauthenticated_returns_401() -> None:
    _cleanup_tables()
    _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "suppressed"},
    )

    assert response.status_code == 401


def test_batch_handle_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-429@example.com", "ops")
    _create_event(delivery_status="failed")

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

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-batch-handle-429"},
    )

    assert response.status_code == 429
    assert response.json()["error"]["request_id"] == "rid-batch-handle-429"


def test_batch_handle_filter_by_alert_kind() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-kind@example.com", "ops")
    matching_id = _create_event(alert_kind="sla_overdue")
    _create_event(alert_kind="sla_due_soon")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "suppressed", "alert_kind": "sla_overdue"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["alert_event_ids"] == [matching_id]


def test_batch_handle_filter_by_feature_code() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-feature@example.com", "ops")
    matching_id = _create_event(feature_code="feature-a")
    _create_event(feature_code="feature-b")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "resolved", "feature_code": "feature-a"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["alert_event_ids"] == [matching_id]


def test_batch_handle_response_schema() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-handle-schema@example.com", "ops")
    _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-batch-schema"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert set(payload["data"]) == {
        "candidate_count",
        "handled_count",
        "skipped_count",
        "dry_run",
        "alert_event_ids",
    }
    assert payload["meta"]["request_id"] == "rid-batch-schema"


def test_batch_handle_returns_422_when_limit_missing() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token(
        "ops-batch-handle-missing-limit@example.com", "ops"
    )
    _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"handling_status": "suppressed"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 422


def test_batch_handle_returns_422_for_invalid_handling_status() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token(
        "ops-batch-handle-invalid-status@example.com", "ops"
    )
    _create_event(delivery_status="failed")

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/handle-batch",
        json={"limit": 10, "handling_status": "ignored"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 422


def test_batch_retry_still_excludes_suppressed_after_61_45() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch-retry-regression@example.com", "ops")
    with SessionLocal() as db:
        excluded_audit = _seed_audit(db)
        included_audit = _seed_audit(db)
        excluded_id = _seed_alert_event(db, audit_id=excluded_audit.id, delivery_status="failed").id
        included_id = _seed_alert_event(db, audit_id=included_audit.id, delivery_status="failed").id
        db.add(
            CanonicalEntitlementMutationAlertEventHandlingModel(
                alert_event_id=excluded_id,
                handling_status="suppressed",
                handled_by_user_id=7,
                handled_at=datetime(2026, 3, 29, 11, 0, tzinfo=timezone.utc),
                ops_comment="known-noise",
                suppression_key="incident-1",
            )
        )
        db.commit()

    response = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["alert_event_ids"] == [included_id]
