from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import delete

from app.core.rate_limit import RateLimitError
from app.core.security import create_access_token
from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.entitlement_mutation.audit.review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.infra.db.models.user import UserModel
from app.main import app
from app.services.api_contracts.ops.entitlement_mutation_audits import ReviewEventItem
from app.services.auth_service import AuthService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        db.execute(delete(UserModel))
        db.execute(delete(CanonicalEntitlementMutationAuditModel))
        db.commit()


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with open_app_test_db_session() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _register_user_and_issue_token_with_role_claim(email: str, role: str, claim_role: str) -> str:
    with open_app_test_db_session() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return create_access_token(subject=str(auth.user.id), role=claim_role)


def _seed_audit(
    db,
    *,
    occurred_at=None,
    operation="upsert_plan_feature_configuration",
    plan_id=1,
    plan_code="basic",
    feature_code="astrologer_chat",
    actor_type="script",
    actor_identifier="test.py",
    source_origin="manual",
    request_id=None,
    before_payload=None,
    after_payload=None,
):
    audit = CanonicalEntitlementMutationAuditModel(
        occurred_at=occurred_at or datetime.now(timezone.utc),
        operation=operation,
        plan_id=plan_id,
        plan_code_snapshot=plan_code,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        source_origin=source_origin,
        request_id=request_id,
        before_payload=before_payload if before_payload is not None else {},
        after_payload=after_payload if after_payload is not None else {"is_enabled": True},
    )
    db.add(audit)
    db.flush()
    return audit


def test_list_returns_empty_when_no_audits() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["items"] == []
    assert payload["data"]["total_count"] == 0
    assert payload["data"]["page"] == 1
    assert payload["data"]["page_size"] == 20


def test_list_returns_audits_sorted_desc() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc), feature_code="f1")
        _seed_audit(db, occurred_at=datetime(2026, 1, 3, tzinfo=timezone.utc), feature_code="f3")
        _seed_audit(db, occurred_at=datetime(2026, 1, 2, tzinfo=timezone.utc), feature_code="f2")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 3
    assert items[0]["feature_code"] == "f3"
    assert items[1]["feature_code"] == "f2"
    assert items[2]["feature_code"] == "f1"


def test_list_filter_by_feature_code() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, feature_code="chat")
        _seed_audit(db, feature_code="daily")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"feature_code": "chat"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "chat"


def test_list_filter_by_actor_type() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, actor_type="script")
        _seed_audit(db, actor_type="admin")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"actor_type": "script"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["actor_type"] == "script"


def test_list_filter_by_plan_code() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, plan_code="basic")
        _seed_audit(db, plan_code="premium")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"plan_code": "basic"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["plan_code_snapshot"] == "basic"


def test_list_filter_by_request_id() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, request_id="rid-1")
        _seed_audit(db, request_id="rid-2")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"request_id": "rid-1"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["request_id"] == "rid-1"


def test_list_filter_by_actor_identifier() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, actor_identifier="seed_product_entitlements.py")
        _seed_audit(db, actor_identifier="backfill_plan_catalog_from_legacy.py")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"actor_identifier": "seed_product_entitlements.py"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["actor_identifier"] == "seed_product_entitlements.py"


def test_list_filter_by_source_origin() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, source_origin="manual")
        _seed_audit(db, source_origin="repair")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"source_origin": "repair"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["source_origin"] == "repair"


def test_list_filter_by_date_range() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc), feature_code="f1")
        _seed_audit(db, occurred_at=datetime(2026, 1, 10, tzinfo=timezone.utc), feature_code="f10")
        _seed_audit(db, occurred_at=datetime(2026, 1, 20, tzinfo=timezone.utc), feature_code="f20")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={
            "date_from": "2026-01-05T00:00:00Z",
            "date_to": "2026-01-15T00:00:00Z",
        },
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "f10"


def test_list_filter_by_date_range_is_inclusive() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, occurred_at=datetime(2026, 1, 5, tzinfo=timezone.utc), feature_code="f5")
        _seed_audit(db, occurred_at=datetime(2026, 1, 10, tzinfo=timezone.utc), feature_code="f10")
        _seed_audit(db, occurred_at=datetime(2026, 1, 15, tzinfo=timezone.utc), feature_code="f15")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={
            "date_from": "2026-01-05T00:00:00Z",
            "date_to": "2026-01-15T00:00:00Z",
        },
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert [item["feature_code"] for item in items] == ["f15", "f10", "f5"]


def test_list_pagination() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        for i in range(1, 6):
            _seed_audit(
                db,
                occurred_at=datetime(2026, 1, i, tzinfo=timezone.utc),
                feature_code=f"f{i}",
            )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"page": 2, "page_size": 2},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    items = payload["data"]["items"]
    assert len(items) == 2
    assert payload["data"]["total_count"] == 5
    assert payload["data"]["page"] == 2
    assert payload["data"]["page_size"] == 2
    # Sorted desc: f5, f4, f3, f2, f1. Page 2 of size 2: f3, f2.
    assert items[0]["feature_code"] == "f3"
    assert items[1]["feature_code"] == "f2"


def test_list_include_payloads_false() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, before_payload={"old": 1}, after_payload={"new": 2})
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"include_payloads": "false"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert "before_payload" not in item
    assert "after_payload" not in item


def test_list_include_payloads_true() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, before_payload={"old": 1}, after_payload={"new": 2})
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"include_payloads": "true"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["before_payload"] == {"old": 1}
    assert item["after_payload"] == {"new": 2}


def test_detail_returns_audit_with_payloads() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db, before_payload={"old": 1}, after_payload={"new": 2})
        db.commit()
        audit_id = audit.id

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]
    assert item["id"] == audit_id
    assert item["before_payload"] == {"old": 1}
    assert item["after_payload"] == {"new": 2}


def test_detail_returns_404_on_unknown_id() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/9999",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "audit_not_found"


def test_detail_returns_403_for_non_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/1",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_detail_returns_403_for_b2b_role() -> None:
    _cleanup_tables()
    b2b_token = _register_user_and_issue_token_with_role_claim(
        "b2b@example.com",
        "user",
        "b2b",
    )
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/1",
        headers={"Authorization": f"Bearer {b2b_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_detail_returns_401_when_unauthenticated() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/entitlements/mutation-audits/1")
    assert response.status_code == 401


def test_list_returns_403_for_non_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_list_returns_403_for_b2b_role() -> None:
    _cleanup_tables()
    b2b_token = _register_user_and_issue_token_with_role_claim(
        "b2b-list@example.com",
        "user",
        "b2b",
    )
    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {b2b_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_list_returns_401_when_unauthenticated() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/entitlements/mutation-audits")
    assert response.status_code == 401


def test_list_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-429@example.com", "ops")

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
        "/v1/ops/entitlements/mutation-audits",
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-entitlement-audits-429",
        },
    )
    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-entitlement-audits-429"


def test_list_includes_diff_fields() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            before_payload={},
            after_payload={
                "is_enabled": True,
                "access_mode": "unlimited",
                "variant_code": None,
                "source_origin": "manual",
                "quotas": [],
            },
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert "change_kind" in item
    assert "risk_level" in item
    assert "changed_fields" in item
    assert "quota_changes" in item
    assert item["change_kind"] == "binding_created"


def test_filter_by_risk_level() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        # High risk: is_enabled change
        _seed_audit(
            db,
            before_payload={
                "is_enabled": True,
                "access_mode": "quota",
                "variant_code": None,
                "source_origin": "manual",
                "quotas": [],
            },
            after_payload={
                "is_enabled": False,
                "access_mode": "quota",
                "variant_code": None,
                "source_origin": "manual",
                "quotas": [],
            },
            feature_code="high_risk",
        )
        # Low risk: only source_origin change
        _seed_audit(
            db,
            before_payload={
                "is_enabled": True,
                "access_mode": "quota",
                "variant_code": None,
                "source_origin": "src1",
                "quotas": [],
            },
            after_payload={
                "is_enabled": True,
                "access_mode": "quota",
                "variant_code": None,
                "source_origin": "src2",
                "quotas": [],
            },
            feature_code="low_risk",
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"risk_level": "high"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "high_risk"


def test_filter_by_change_kind() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        # Created
        _seed_audit(db, before_payload={}, feature_code="created")
        # Updated
        _seed_audit(
            db,
            before_payload={"is_enabled": True},
            after_payload={"is_enabled": False},
            feature_code="updated",
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"change_kind": "binding_created"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "created"


def test_filter_by_changed_field() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            before_payload={"is_enabled": True, "access_mode": "quota"},
            after_payload={"is_enabled": False, "access_mode": "quota"},
            feature_code="match",
        )
        _seed_audit(
            db,
            before_payload={"is_enabled": True, "access_mode": "quota"},
            after_payload={"is_enabled": True, "access_mode": "unlimited"},
            feature_code="no_match",
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"changed_field": "binding.is_enabled"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "match"


def test_diff_filters_paginate_after_application_level_filtering() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-paginated@example.com", "ops")
    with open_app_test_db_session() as db:
        for index in range(1, 6):
            _seed_audit(
                db,
                occurred_at=datetime(2026, 1, index, tzinfo=timezone.utc),
                before_payload={
                    "is_enabled": True,
                    "access_mode": "quota",
                    "variant_code": None,
                    "source_origin": "manual",
                    "quotas": [],
                },
                after_payload={
                    "is_enabled": False,
                    "access_mode": "quota",
                    "variant_code": None,
                    "source_origin": "manual",
                    "quotas": [],
                },
                feature_code=f"high-{index}",
            )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"risk_level": "high", "page": 2, "page_size": 2},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 5
    assert payload["page"] == 2
    assert payload["page_size"] == 2
    assert [item["feature_code"] for item in payload["items"]] == ["high-3", "high-2"]


def test_detail_includes_diff_fields() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db)
        db.commit()
        audit_id = audit.id

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]
    assert "change_kind" in item
    assert "risk_level" in item


def test_filter_invalid_risk_level_returns_422() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"risk_level": "extreme"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 422


def test_filter_invalid_change_kind_returns_422() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"change_kind": "foo"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 422


def test_filter_returns_400_when_diff_scope_is_too_large(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-too-large@example.com", "ops")

    def _list_mutation_audits(*args: object, **kwargs: object) -> tuple[list[object], int]:
        return [], 10_001

    monkeypatch.setattr(
        "app.api.v1.routers.ops.entitlement_mutation_audits."
        "CanonicalEntitlementMutationAuditQueryService.list_mutation_audits",
        _list_mutation_audits,
    )

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"risk_level": "high"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 400
    payload = response.json()["error"]
    assert payload["code"] == "diff_filter_result_set_too_large"
    assert payload["details"] == {"sql_count": 10001, "max_allowed": 10000}


# ---------------------------------------------------------------------------
# Helpers Story 61.35
# ---------------------------------------------------------------------------

_HIGH_RISK_BEFORE = {
    "is_enabled": True,
    "access_mode": "quota",
    "variant_code": None,
    "source_origin": "manual",
    "quotas": [],
}
_HIGH_RISK_AFTER = {
    "is_enabled": False,
    "access_mode": "quota",
    "variant_code": None,
    "source_origin": "manual",
    "quotas": [],
}
_LOW_RISK_BEFORE = {
    "is_enabled": True,
    "access_mode": "quota",
    "variant_code": None,
    "source_origin": "src_a",
    "quotas": [],
}
_LOW_RISK_AFTER = {
    "is_enabled": True,
    "access_mode": "quota",
    "variant_code": None,
    "source_origin": "src_b",
    "quotas": [],
}


def _seed_review(
    db, *, audit_id: int, review_status: str = "acknowledged"
) -> CanonicalEntitlementMutationAuditReviewModel:
    from datetime import datetime, timezone

    review = CanonicalEntitlementMutationAuditReviewModel(
        audit_id=audit_id,
        review_status=review_status,
        reviewed_by_user_id=1,
        reviewed_at=datetime.now(timezone.utc),
        review_comment="Test review",
        incident_key=None,
    )
    db.add(review)
    db.flush()
    return review


# ---------------------------------------------------------------------------
# Tests Story 61.35
# ---------------------------------------------------------------------------


def test_post_review_creates_review_returns_201() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db, before_payload=_HIGH_RISK_BEFORE, after_payload=_HIGH_RISK_AFTER)
        db.commit()
        audit_id = audit.id

    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "acknowledged", "review_comment": "OK", "incident_key": "INC-001"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["audit_id"] == audit_id
    assert data["review_status"] == "acknowledged"
    assert data["review_comment"] == "OK"
    assert data["incident_key"] == "INC-001"
    assert "reviewed_at" in data


def test_post_review_updates_existing_review() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db, before_payload=_HIGH_RISK_BEFORE, after_payload=_HIGH_RISK_AFTER)
        db.commit()
        audit_id = audit.id

    # Première revue
    client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "acknowledged"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    # Mise à jour
    response = client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "closed", "review_comment": "Clôturé"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["review_status"] == "closed"
    assert data["review_comment"] == "Clôturé"


def test_post_review_invalid_status_returns_422() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.post(
        "/v1/ops/entitlements/mutation-audits/1/review",
        json={"review_status": "invalid_status"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 422


def test_post_review_nonexistent_audit_returns_404() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.post(
        "/v1/ops/entitlements/mutation-audits/99999/review",
        json={"review_status": "acknowledged"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "audit_not_found"


def test_post_review_requires_ops_or_admin_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    response = client.post(
        "/v1/ops/entitlements/mutation-audits/1/review",
        json={"review_status": "acknowledged"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_list_review_virtual_pending_for_high_risk_no_review() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, before_payload=_HIGH_RISK_BEFORE, after_payload=_HIGH_RISK_AFTER)
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert "review" in item
    assert item["review"]["status"] == "pending_review"
    # Les champs null sont omis par response_model_exclude_none=True
    assert "reviewed_by_user_id" not in item["review"]
    assert "reviewed_at" not in item["review"]


def test_list_review_populated_when_review_exists() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db, before_payload=_HIGH_RISK_BEFORE, after_payload=_HIGH_RISK_AFTER)
        db.flush()
        _seed_review(db, audit_id=audit.id, review_status="acknowledged")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["review"]["status"] == "acknowledged"
    assert item["review"]["review_comment"] == "Test review"


def test_list_review_null_for_low_risk_no_review() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, before_payload=_LOW_RISK_BEFORE, after_payload=_LOW_RISK_AFTER)
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    # review omis car null (response_model_exclude_none=True)
    assert "review" not in item


def test_filter_by_review_status_pending_review() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        # High risk sans revue → virtual pending_review
        _seed_audit(
            db,
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
            feature_code="high_no_review",
        )
        # Low risk sans revue → pas de statut virtuel
        _seed_audit(
            db,
            before_payload=_LOW_RISK_BEFORE,
            after_payload=_LOW_RISK_AFTER,
            feature_code="low_no_review",
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"review_status": "pending_review"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "high_no_review"


def test_filter_by_review_status_closed() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit_closed = _seed_audit(
            db,
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
            feature_code="closed_review",
        )
        db.flush()
        _seed_review(db, audit_id=audit_closed.id, review_status="closed")
        _seed_audit(
            db,
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
            feature_code="no_review",
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"review_status": "closed"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "closed_review"


def test_detail_includes_review_field() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db, before_payload=_HIGH_RISK_BEFORE, after_payload=_HIGH_RISK_AFTER)
        db.flush()
        _seed_review(db, audit_id=audit.id, review_status="investigating")
        db.commit()
        audit_id = audit.id

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]
    assert "review" in item
    assert item["review"]["status"] == "investigating"


# ---------------------------------------------------------------------------
# Tests Story 61.36
# ---------------------------------------------------------------------------


def test_get_review_history_empty_returns_200() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db)
        db.commit()
        audit_id = audit.id

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review-history",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["items"] == []
    assert data["total_count"] == 0


def test_get_review_history_after_one_review() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db)
        db.commit()
        audit_id = audit.id

    client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "acknowledged", "review_comment": "Checked"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review-history",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_count"] == 1
    item = data["items"][0]
    assert item["event_type"] == "created"
    assert item["new_review_status"] == "acknowledged"
    assert item["new_review_comment"] == "Checked"
    # previous_* fields should be omitted because they are None
    assert "previous_review_status" not in item
    assert "previous_review_comment" not in item


def test_get_review_history_chain_of_transitions() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db)
        db.commit()
        audit_id = audit.id

    # 1. First review
    client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "acknowledged"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    # 2. Transition to investigating
    client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "investigating", "review_comment": "Investigating"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    # 3. Transition to closed
    client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "closed", "incident_key": "INC-123"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review-history",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 3

    # Order ASC: occurred_at
    assert [item["event_type"] for item in items] == ["created", "updated", "updated"]
    assert items[0]["new_review_status"] == "acknowledged"
    assert "previous_review_status" not in items[0]

    assert items[1]["previous_review_status"] == "acknowledged"
    assert items[1]["new_review_status"] == "investigating"
    assert items[1]["new_review_comment"] == "Investigating"

    assert items[2]["previous_review_status"] == "investigating"
    assert items[2]["new_review_status"] == "closed"
    assert items[2]["new_incident_key"] == "INC-123"


def test_get_review_history_noop_no_event_created() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db)
        db.commit()
        audit_id = audit.id

    # First review
    client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "acknowledged", "review_comment": "OK"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    # No-op review
    client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "acknowledged", "review_comment": "OK"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review-history",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.json()["data"]["total_count"] == 1


def test_get_review_history_nonexistent_audit_returns_404() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/99999/review-history",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "audit_not_found"


def test_get_review_history_unauthenticated_returns_401() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/entitlements/mutation-audits/1/review-history")
    assert response.status_code == 401


def test_get_review_history_requires_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/1/review-history",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_get_review_history_request_id_propagated() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(db)
        db.commit()
        audit_id = audit.id

    client.post(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review",
        json={"review_status": "acknowledged"},
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "my-trace-id"},
    )

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}/review-history",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.json()["data"]["items"][0]["request_id"] == "my-trace-id"


def test_review_history_schema_rejects_pending_review_status() -> None:
    with pytest.raises(ValidationError):
        ReviewEventItem(
            id=1,
            audit_id=42,
            new_review_status="pending_review",
            occurred_at=datetime.now(timezone.utc),
        )


# ---------------------------------------------------------------------------
# Tests Story 61.37 — Work Queue & Summary
# ---------------------------------------------------------------------------


def test_review_queue_empty_returns_200() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["items"] == []
    assert data["total_count"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 20


def test_review_queue_summary_counts() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            feature_code="pending-1",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        _seed_audit(
            db,
            feature_code="pending-2",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        investigating_audit = _seed_audit(
            db,
            feature_code="investigating-1",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.flush()
        _seed_review(
            db,
            audit_id=investigating_audit.id,
            review_status="investigating",
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue/summary",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_count"] == 3
    assert data["pending_review_count"] == 2
    assert data["investigating_count"] == 1
    assert data["acknowledged_count"] == 0
    assert data["expected_count"] == 0
    assert data["closed_count"] == 0
    assert data["no_review_count"] == 0
    assert data["high_unreviewed_count"] == 2


def test_review_queue_filter_by_feature_code() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            feature_code="f1",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        _seed_audit(
            db,
            feature_code="f2",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        params={"feature_code": "f1"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "f1"


def test_review_queue_pending_review_from_high_risk_audit() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(db, before_payload=_HIGH_RISK_BEFORE, after_payload=_HIGH_RISK_AFTER)
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total_count"] == 1
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["effective_review_status"] == "pending_review"
    assert "age_seconds" in item
    assert "age_hours" in item
    assert item["is_pending"] is True
    assert item["is_closed"] is False


def test_review_queue_age_fields_populated() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["age_seconds"] >= 0
    assert item["age_hours"] >= 0
    assert item["age_hours"] == round(item["age_seconds"] / 3600, 2)


def test_review_queue_sort_priority_order() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        pending_audit = _seed_audit(
            db,
            occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            feature_code="pending-review",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        investigating_audit = _seed_audit(
            db,
            occurred_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
            feature_code="investigating-review",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        acknowledged_audit = _seed_audit(
            db,
            occurred_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
            feature_code="acknowledged-review",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.flush()
        assert pending_audit.id is not None
        _seed_review(db, audit_id=investigating_audit.id, review_status="investigating")
        _seed_review(db, audit_id=acknowledged_audit.id, review_status="acknowledged")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    statuses = [item["effective_review_status"] for item in items]
    assert statuses == ["pending_review", "investigating", "acknowledged"]


def test_review_queue_filter_by_effective_review_status() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            feature_code="f-pending",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        a2 = _seed_audit(
            db,
            feature_code="f-investigating",
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.flush()
        _seed_review(db, audit_id=a2.id, review_status="investigating")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        params={"effective_review_status": "investigating"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "f-investigating"
    assert items[0]["effective_review_status"] == "investigating"


def test_review_queue_filter_by_incident_key() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        a1 = _seed_audit(db, feature_code="f1")
        db.flush()
        r1 = _seed_review(db, audit_id=a1.id)
        r1.incident_key = "INC-1"
        _seed_audit(db, feature_code="f2")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        params={"incident_key": "INC-1"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "f1"


def test_review_queue_pagination() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        for i in range(1, 4):
            _seed_audit(
                db,
                occurred_at=datetime(2026, 1, i, tzinfo=timezone.utc),
                feature_code=f"f{i}",
                before_payload=_HIGH_RISK_BEFORE,
                after_payload=_HIGH_RISK_AFTER,
            )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        params={"page": 2, "page_size": 1},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert len(payload["items"]) == 1
    assert payload["total_count"] == 3
    assert payload["page"] == 2
    assert payload["page_size"] == 1
    assert payload["items"][0]["feature_code"] == "f2"


def test_review_queue_requires_ops_role_returns_403() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_review_queue_summary_requires_ops_role_returns_403() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue/summary",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_review_queue_unauthenticated_returns_401() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/entitlements/mutation-audits/review-queue")
    assert response.status_code == 401


def test_review_queue_summary_unauthenticated_returns_401() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/entitlements/mutation-audits/review-queue/summary")
    assert response.status_code == 401


def test_review_queue_returns_400_when_diff_scope_is_too_large(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-too-large@example.com", "ops")

    def _list_mutation_audits(*args: object, **kwargs: object) -> tuple[list[object], int]:
        return [], 10_001

    monkeypatch.setattr(
        "app.api.v1.routers.ops.entitlement_mutation_audits."
        "CanonicalEntitlementMutationAuditQueryService.list_mutation_audits",
        _list_mutation_audits,
    )

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 400


def test_review_queue_summary_returns_400_when_diff_scope_is_too_large(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-too-large@example.com", "ops")

    def _list_mutation_audits(*args: object, **kwargs: object) -> tuple[list[object], int]:
        return [], 10_001

    monkeypatch.setattr(
        "app.api.v1.routers.ops.entitlement_mutation_audits."
        "CanonicalEntitlementMutationAuditQueryService.list_mutation_audits",
        _list_mutation_audits,
    )

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue/summary",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Tests Story 61.38 — SLA ops
# ---------------------------------------------------------------------------


def test_review_queue_sla_within_sla_high_pending() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["sla_status"] == "within_sla"
    assert item["sla_target_seconds"] == 14400
    assert "due_at" in item
    assert "overdue_seconds" not in item


def test_review_queue_sla_overdue_high_pending() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc) - timedelta(hours=5),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["sla_status"] == "overdue"
    assert item["overdue_seconds"] >= 3600


def test_review_queue_sla_due_soon_high_pending() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        # SLA 4h = 14400s. Due soon < 20% restant = 2880s.
        # Restant ≈ 1440s (24min) if age = 3h36 = 12960s.
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc) - timedelta(minutes=216),  # 3h36
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["sla_status"] == "due_soon"


def test_review_queue_sla_null_for_low_risk() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            before_payload=_LOW_RISK_BEFORE,
            after_payload=_LOW_RISK_AFTER,
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert "sla_status" not in item
    assert "sla_target_seconds" not in item


def test_review_queue_sla_null_for_closed() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(
            db,
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.flush()
        _seed_review(db, audit_id=audit.id, review_status="closed")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert "sla_status" not in item


def test_review_queue_filter_by_sla_status_overdue() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        # Overdue
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc) - timedelta(hours=5),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
            feature_code="overdue",
        )
        # Within SLA
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
            feature_code="within",
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        params={"sla_status": "overdue"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "overdue"


def test_review_queue_summary_overdue_count() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        # 1 Overdue
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc) - timedelta(hours=5),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        # 1 Within SLA
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue/summary",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["overdue_count"] == 1
    assert data["due_soon_count"] == 0


def test_review_queue_summary_filter_by_sla_status_restricts_all_counters() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc) - timedelta(hours=5),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
            feature_code="overdue",
        )
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
            feature_code="within",
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue/summary",
        params={"sla_status": "overdue"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_count"] == 1
    assert data["pending_review_count"] == 1
    assert data["overdue_count"] == 1
    assert data["due_soon_count"] == 0
    assert data["high_unreviewed_count"] == 1
    assert data["oldest_pending_age_seconds"] >= 18000


def test_review_queue_summary_oldest_pending_age_seconds() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc) - timedelta(seconds=100),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue/summary",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["oldest_pending_age_seconds"] >= 100


def test_review_queue_summary_oldest_pending_ignores_investigating() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(
            db,
            occurred_at=datetime.now(timezone.utc) - timedelta(hours=8),
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.flush()
        _seed_review(db, audit_id=audit.id, review_status="investigating")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue/summary",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_count"] == 1
    assert data["investigating_count"] == 1
    assert "oldest_pending_age_seconds" not in data


def test_review_queue_summary_oldest_pending_none_when_no_pending() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with open_app_test_db_session() as db:
        audit = _seed_audit(
            db,
            before_payload=_HIGH_RISK_BEFORE,
            after_payload=_HIGH_RISK_AFTER,
        )
        db.flush()
        _seed_review(db, audit_id=audit.id, review_status="closed")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue/summary",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "oldest_pending_age_seconds" not in data
