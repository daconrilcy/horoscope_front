from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_application import (
    CanonicalEntitlementMutationAlertSuppressionApplicationModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)

ALERTS_PATH = "/v1/ops/entitlements/mutation-audits/alerts"
RULES_PATH = f"{ALERTS_PATH}/suppression-rules"


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserModel))
        db.execute(delete(CanonicalEntitlementMutationAuditModel))
        db.execute(delete(CanonicalEntitlementMutationAlertHandlingModel))
        db.execute(delete(CanonicalEntitlementMutationAlertEventModel))
        db.execute(delete(CanonicalEntitlementMutationAlertSuppressionRuleModel))
        db.commit()


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _seed_audit(db) -> CanonicalEntitlementMutationAuditModel:
    audit = CanonicalEntitlementMutationAuditModel(
        occurred_at=datetime.now(timezone.utc),
        operation="upsert_plan_feature_configuration",
        plan_id=1,
        plan_code_snapshot="premium",
        feature_code="feature-a",
        actor_type="script",
        actor_identifier="test.py",
        source_origin="manual",
        before_payload={},
        after_payload={"is_enabled": True},
    )
    db.add(audit)
    db.flush()
    return audit


def _seed_alert(
    db,
    audit_id: int,
    *,
    dedupe_suffix: str,
    feature_code: str,
    delivery_status: str = "failed",
) -> CanonicalEntitlementMutationAlertEventModel:
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"key-{dedupe_suffix}",
        alert_kind="sla_overdue",
        delivery_status=delivery_status,
        delivery_channel="webhook",
        payload={},
        feature_code_snapshot=feature_code,
        plan_id_snapshot=1,
        plan_code_snapshot="premium",
        risk_level_snapshot="high",
        effective_review_status_snapshot="pending_review",
        actor_type_snapshot="user",
        actor_identifier_snapshot="u1",
        age_seconds_snapshot=100,
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    db.flush()
    return event


def _create_rule(headers: dict[str, str], **payload: object) -> int:
    response = client.post(RULES_PATH, headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_list_alerts_marks_matching_future_alert_as_rule_suppressed() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        _seed_alert(db, audit.id, dedupe_suffix="match", feature_code="feature-a")
        db.commit()

    rule_id = _create_rule(
        headers,
        alert_kind="sla_overdue",
        feature_code="feature-a",
        ops_comment="Known noise",
        suppression_key="noise",
    )

    response = client.get(ALERTS_PATH, headers=headers)

    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["handling"]["handling_status"] == "suppressed"
    assert item["handling"]["source"] == "rule"
    assert item["handling"]["suppression_rule_id"] == rule_id
    assert item["retryable"] is False

    with SessionLocal() as db:
        application = db.execute(
            select(CanonicalEntitlementMutationAlertSuppressionApplicationModel)
        ).scalar_one()
        assert application.application_mode == "rule"
        assert application.suppression_rule_id == rule_id
        assert application.suppression_key == "noise"


def test_create_rule_materializes_suppression_application_for_existing_alert() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-applications@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-rule-apply"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert(db, audit.id, dedupe_suffix="existing", feature_code="feature-a")
        event_id = event.id
        db.commit()

    rule_id = _create_rule(
        headers,
        alert_kind="sla_overdue",
        feature_code="feature-a",
        ops_comment="Known noise",
        suppression_key="noise",
    )

    with SessionLocal() as db:
        application = db.execute(
            select(CanonicalEntitlementMutationAlertSuppressionApplicationModel).where(
                CanonicalEntitlementMutationAlertSuppressionApplicationModel.alert_event_id
                == event_id
            )
        ).scalar_one()
        assert application.application_mode == "rule"
        assert application.suppression_rule_id == rule_id
        assert application.request_id == "rid-rule-apply"


def test_list_alerts_manual_resolved_wins_over_rule() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-resolved@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert(db, audit.id, dedupe_suffix="resolved", feature_code="feature-a")
        db.add(
            CanonicalEntitlementMutationAlertHandlingModel(
                alert_event_id=event.id,
                handling_status="resolved",
                handled_by_user_id=1,
                ops_comment="handled manually",
            )
        )
        db.commit()

    _create_rule(headers, alert_kind="sla_overdue", feature_code="feature-a")

    response = client.get(ALERTS_PATH, headers=headers)

    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["handling"]["handling_status"] == "resolved"
    assert item["handling"]["source"] == "manual"
    assert item["retryable"] is False


def test_summary_includes_rule_suppressed_count() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-summary@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        _seed_alert(db, audit.id, dedupe_suffix="suppressed", feature_code="feature-a")
        _seed_alert(db, audit.id, dedupe_suffix="retryable", feature_code="feature-b")
        db.commit()

    _create_rule(headers, alert_kind="sla_overdue", feature_code="feature-a")

    response = client.get(f"{ALERTS_PATH}/summary", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["suppressed_count"] == 1
    assert data["retryable_count"] == 1


def test_retry_batch_excludes_matching_rule_suppressed_alert() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-batch@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        matching = _seed_alert(db, audit.id, dedupe_suffix="suppressed", feature_code="feature-a")
        retryable = _seed_alert(db, audit.id, dedupe_suffix="retryable", feature_code="feature-b")
        matching_id = matching.id
        retryable_id = retryable.id
        db.commit()

    _create_rule(headers, alert_kind="sla_overdue", feature_code="feature-a")
    response = client.post(
        f"{ALERTS_PATH}/retry-batch",
        headers=headers,
        json={"limit": 10, "dry_run": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["alert_event_ids"] == [retryable_id]
    assert matching_id not in response.json()["data"]["alert_event_ids"]


def test_retry_unitary_returns_409_when_rule_matches() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-retry@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert(db, audit.id, dedupe_suffix="suppressed", feature_code="feature-a")
        event_id = event.id
        db.commit()

    _create_rule(headers, alert_kind="sla_overdue", feature_code="feature-a")
    response = client.post(
        f"{ALERTS_PATH}/{event_id}/retry",
        headers=headers,
        json={"dry_run": True},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "alert_event_not_retryable"
    assert "suppression rule" in response.json()["error"]["message"]


def test_handling_status_filter_suppressed_includes_rule_matches() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-filter1@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        matching = _seed_alert(db, audit.id, dedupe_suffix="suppressed", feature_code="feature-a")
        matching_id = matching.id
        _seed_alert(db, audit.id, dedupe_suffix="pending", feature_code="feature-b")
        db.commit()

    _create_rule(headers, alert_kind="sla_overdue", feature_code="feature-a")
    response = client.get(
        ALERTS_PATH,
        headers=headers,
        params={"handling_status": "suppressed"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["data"]["items"]] == [matching_id]


def test_handling_status_filter_pending_retry_excludes_rule_matches() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-filter2@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        _seed_alert(db, audit.id, dedupe_suffix="suppressed", feature_code="feature-a")
        retryable = _seed_alert(db, audit.id, dedupe_suffix="pending", feature_code="feature-b")
        retryable_id = retryable.id
        db.commit()

    _create_rule(headers, alert_kind="sla_overdue", feature_code="feature-a")
    response = client.get(
        ALERTS_PATH,
        headers=headers,
        params={"handling_status": "pending_retry"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["data"]["items"]] == [retryable_id]


def test_disabling_rule_restores_retryability_and_visibility() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-disable@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert(db, audit.id, dedupe_suffix="suppressed", feature_code="feature-a")
        event_id = event.id
        db.commit()

    rule_id = _create_rule(headers, alert_kind="sla_overdue", feature_code="feature-a")
    patch_response = client.patch(
        f"{RULES_PATH}/{rule_id}",
        headers=headers,
        json={"is_active": False},
    )
    assert patch_response.status_code == 200

    list_response = client.get(
        ALERTS_PATH,
        headers=headers,
        params={"handling_status": "pending_retry"},
    )
    retry_response = client.post(
        f"{ALERTS_PATH}/{event_id}/retry",
        headers=headers,
        json={"dry_run": True},
    )

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()["data"]["items"]] == [event_id]
    assert retry_response.status_code == 200
    assert retry_response.json()["data"]["attempted"] is True
