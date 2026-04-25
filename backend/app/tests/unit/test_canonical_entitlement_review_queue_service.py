from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.services.canonical_entitlement.audit.review_queue import (
    CanonicalEntitlementReviewQueueService,
)


def test_build_review_queue_rows_empty(db_session: Session):
    # Setup
    now_utc = datetime.now(timezone.utc)

    # Mock CanonicalEntitlementMutationAuditQueryService
    with pytest.MonkeyPatch.context() as mp:
        mock_query = MagicMock()
        mock_query.list_mutation_audits.return_value = ([], 0)
        mp.setattr(
            "app.services.canonical_entitlement.audit.review_queue.CanonicalEntitlementMutationAuditQueryService",
            mock_query,
        )

        # Execute
        rows = CanonicalEntitlementReviewQueueService.build_review_queue_rows(
            db_session, now_utc=now_utc
        )

        # Verify
        assert rows == []


def test_summarize_review_queue_rows_empty():
    # Execute
    summary = CanonicalEntitlementReviewQueueService.summarize_review_queue_rows([])

    # Verify
    assert summary.total_count == 0
    assert summary.pending_review_count == 0
    assert summary.overdue_count == 0


def test_compute_sla_within_sla():
    now = datetime(2026, 3, 29, 12, 0, 0, tzinfo=timezone.utc)
    occurred = now - timedelta(hours=1)
    # Target for high/pending_review is 4h (14400s)
    # Age is 1h (3600s). Remaining is 3h.
    # Due soon is 20% of 4h = 48 min (2880s).
    # 3h > 48 min -> within_sla

    res = CanonicalEntitlementReviewQueueService._compute_sla(
        "high", "pending_review", occurred, now
    )
    assert res["sla_status"] == "within_sla"
    assert res["sla_target_seconds"] == 14400


def test_compute_sla_due_soon():
    now = datetime(2026, 3, 29, 12, 0, 0, tzinfo=timezone.utc)
    # Target 4h. Due soon threshold is 48 min.
    # We want remaining < 48 min.
    # Age = 4h - 30 min = 3h 30 min (12600s)
    occurred = now - timedelta(hours=3, minutes=30)

    res = CanonicalEntitlementReviewQueueService._compute_sla(
        "high", "pending_review", occurred, now
    )
    assert res["sla_status"] == "due_soon"


def test_compute_sla_overdue():
    now = datetime(2026, 3, 29, 12, 0, 0, tzinfo=timezone.utc)
    # Age 5h > 4h
    occurred = now - timedelta(hours=5)

    res = CanonicalEntitlementReviewQueueService._compute_sla(
        "high", "pending_review", occurred, now
    )
    assert res["sla_status"] == "overdue"
    assert res["overdue_seconds"] == 3600


def test_compute_review_state_status():
    # Record exists
    mock_rev = MagicMock()
    mock_rev.review_status = "investigating"
    res = CanonicalEntitlementReviewQueueService._compute_review_state_status("high", mock_rev)
    assert res == "investigating"

    # No record, high risk
    res = CanonicalEntitlementReviewQueueService._compute_review_state_status("high", None)
    assert res == "pending_review"

    # No record, low risk
    res = CanonicalEntitlementReviewQueueService._compute_review_state_status("low", None)
    assert res is None


def test_build_review_queue_rows_returns_business_sorted_rows(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
):
    older_audit = MagicMock()
    older_audit.id = 1
    older_audit.occurred_at = datetime(2026, 3, 29, 7, 0, tzinfo=timezone.utc)
    older_audit.before_payload = {}
    older_audit.after_payload = {"is_enabled": False}

    newer_audit = MagicMock()
    newer_audit.id = 2
    newer_audit.occurred_at = datetime(2026, 3, 29, 8, 0, tzinfo=timezone.utc)
    newer_audit.before_payload = {}
    newer_audit.after_payload = {"is_enabled": False}

    mock_query = MagicMock()
    mock_query.list_mutation_audits.return_value = ([newer_audit, older_audit], 2)
    monkeypatch.setattr(
        "app.services.canonical_entitlement.audit.review_queue."
        "CanonicalEntitlementMutationAuditQueryService",
        mock_query,
    )

    mock_diff = MagicMock()
    mock_diff.risk_level = "high"
    monkeypatch.setattr(
        "app.services.canonical_entitlement.audit.review_queue."
        "CanonicalEntitlementMutationDiffService.compute_diff",
        lambda before_payload, after_payload: mock_diff,
    )

    reviews_result = MagicMock()
    reviews_result.scalars.return_value.all.return_value = []
    monkeypatch.setattr(db_session, "execute", lambda statement: reviews_result)

    rows = CanonicalEntitlementReviewQueueService.build_review_queue_rows(
        db_session,
        now_utc=datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc),
    )

    assert [row.audit.id for row in rows] == [1, 2]
