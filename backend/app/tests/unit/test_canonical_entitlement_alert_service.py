from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.services.canonical_entitlement.alert.service import (
    AlertRunResult,
    CanonicalEntitlementAlertService,
)
from app.services.canonical_entitlement.audit.review_queue import ReviewQueueRow


@pytest.fixture
def mock_row():
    audit = MagicMock()
    audit.id = 42
    audit.feature_code = "feat1"
    audit.plan_id = 7
    audit.plan_code_snapshot = "p1"
    audit.actor_type = "user"
    audit.actor_identifier = "user1"

    diff = MagicMock()
    diff.risk_level = "high"

    return ReviewQueueRow(
        audit=audit,
        diff=diff,
        review_record=None,
        effective_review_status="pending_review",
        sla_target_seconds=14400,
        due_at=datetime.now(timezone.utc) + timedelta(hours=1),
        sla_status="due_soon",
        overdue_seconds=None,
        age_seconds=3600,
        age_hours=1.0,
    )


def test_emit_disabled_config_short_circuits(db_session: Session):
    with patch.object(settings, "ops_review_queue_alerts_enabled", False):
        result = CanonicalEntitlementAlertService.emit_sla_alerts(db_session)
        assert result == AlertRunResult(0, 0, 0, 0, 0, False)


def test_emit_dry_run_creates_no_rows(db_session: Session, mock_row):
    with patch.object(settings, "ops_review_queue_alerts_enabled", True):
        service_path = "app.services.canonical_entitlement.audit.review_queue"
        mock_target = (
            f"{service_path}.CanonicalEntitlementReviewQueueService.build_review_queue_rows"
        )
        with patch(mock_target) as mock_build:
            mock_row.sla_status = "overdue"
            mock_build.return_value = [mock_row]

            result = CanonicalEntitlementAlertService.emit_sla_alerts(db_session, dry_run=True)

            assert result.emitted_count == 1
            assert result.candidate_count == 1
            assert result.dry_run is True

            # Verify no rows in DB
            count = db_session.query(CanonicalEntitlementMutationAlertEventModel).count()
            assert count == 0


def test_emit_due_soon_alert_once(db_session: Session, mock_row):
    service_path = "app.services.canonical_entitlement.audit.review_queue"
    mock_target = f"{service_path}.CanonicalEntitlementReviewQueueService.build_review_queue_rows"
    with patch.object(settings, "ops_review_queue_alerts_enabled", True):
        with patch.object(settings, "ops_review_queue_alert_webhook_url", None):
            with patch(mock_target) as mock_build:
                mock_build.return_value = [mock_row]

                result = CanonicalEntitlementAlertService.emit_sla_alerts(db_session)
                assert result.emitted_count == 1

                # Verify row in DB
                event = db_session.query(CanonicalEntitlementMutationAlertEventModel).first()
                assert event.audit_id == 42
                assert event.alert_kind == "sla_due_soon"
                assert event.delivery_channel == "log"
                assert event.delivery_status == "sent"


def test_emit_skips_duplicate_dedupe_key(db_session: Session, mock_row):
    service_path = "app.services.canonical_entitlement.audit.review_queue"
    mock_target = f"{service_path}.CanonicalEntitlementReviewQueueService.build_review_queue_rows"
    with patch.object(settings, "ops_review_queue_alerts_enabled", True):
        with patch.object(settings, "ops_review_queue_alert_webhook_url", None):
            with patch(mock_target) as mock_build:
                mock_build.return_value = [mock_row]

                # First run
                CanonicalEntitlementAlertService.emit_sla_alerts(db_session)

                # Second run
                result = CanonicalEntitlementAlertService.emit_sla_alerts(db_session)
                assert result.emitted_count == 0
                assert result.skipped_duplicate_count == 1


def test_emit_new_alert_when_status_phase_changes(db_session: Session, mock_row):
    service_path = "app.services.canonical_entitlement.audit.review_queue"
    mock_target = f"{service_path}.CanonicalEntitlementReviewQueueService.build_review_queue_rows"
    with patch.object(settings, "ops_review_queue_alerts_enabled", True):
        with patch.object(settings, "ops_review_queue_alert_webhook_url", None):
            with patch(mock_target) as mock_build:
                # Phase 1: due_soon
                mock_build.return_value = [mock_row]
                CanonicalEntitlementAlertService.emit_sla_alerts(db_session)

                # Phase 2: overdue
                mock_row.sla_status = "overdue"
                result = CanonicalEntitlementAlertService.emit_sla_alerts(db_session)

                assert result.emitted_count == 1
                assert result.skipped_duplicate_count == 0

                count = db_session.query(CanonicalEntitlementMutationAlertEventModel).count()
                assert count == 2


def test_emit_ignores_closed_and_expected_items(db_session: Session, mock_row):
    with patch.object(settings, "ops_review_queue_alerts_enabled", True):
        service_path = "app.services.canonical_entitlement.audit.review_queue"
        mock_target = (
            f"{service_path}.CanonicalEntitlementReviewQueueService.build_review_queue_rows"
        )
        with patch(mock_target) as mock_build:
            mock_row.effective_review_status = "closed"
            mock_build.return_value = [mock_row]

            result = CanonicalEntitlementAlertService.emit_sla_alerts(db_session)
            assert result.candidate_count == 0
            assert result.emitted_count == 0


def test_emit_failed_webhook_persists_failed_event(db_session: Session, mock_row):
    with patch.object(settings, "ops_review_queue_alerts_enabled", True):
        with patch.object(settings, "ops_review_queue_alert_webhook_url", "http://fail"):
            service_path = "app.services.canonical_entitlement.audit.review_queue"
            alert_service_path = "app.services.canonical_entitlement.alert.service"
            mock_target_queue = (
                f"{service_path}.CanonicalEntitlementReviewQueueService.build_review_queue_rows"
            )
            mock_target_webhook = (
                f"{alert_service_path}.CanonicalEntitlementAlertDeliveryRuntime._deliver_webhook"
            )

            with patch(mock_target_queue) as mock_build:
                with patch(mock_target_webhook) as mock_deliver:
                    mock_deliver.return_value = (False, "Timeout")
                    mock_build.return_value = [mock_row]

                    result = CanonicalEntitlementAlertService.emit_sla_alerts(db_session)

                    assert result.failed_count == 1
                    assert result.emitted_count == 0

                    event = db_session.query(CanonicalEntitlementMutationAlertEventModel).first()
                    assert event.delivery_status == "failed"
                    assert event.delivery_error == "Timeout"


@patch(
    "app.services.canonical_entitlement.alert.service.CanonicalEntitlementAlertDeliveryRuntime._deliver_webhook"
)
def test_emit_concurrent_insert_handled_as_skipped_duplicate(
    mock_deliver, db_session: Session, mock_row
):
    mock_deliver.return_value = (True, None)
    with patch.object(settings, "ops_review_queue_alerts_enabled", True):
        with patch.object(settings, "ops_review_queue_alert_webhook_url", "http://ok"):
            service_path = "app.services.canonical_entitlement.audit.review_queue"
            mock_target = (
                f"{service_path}.CanonicalEntitlementReviewQueueService.build_review_queue_rows"
            )
            with patch(mock_target) as mock_build:
                mock_build.return_value = [mock_row]

                # Simulate race condition
                original_add = db_session.add
                call_count = 0

                def side_effect(obj):
                    nonlocal call_count
                    is_event = isinstance(obj, CanonicalEntitlementMutationAlertEventModel)
                    if is_event and call_count == 0:
                        call_count += 1
                        from sqlalchemy.exc import IntegrityError

                        raise IntegrityError("duplicate key", params={}, orig=Exception())
                    return original_add(obj)

                with patch.object(db_session, "add", side_effect=side_effect):
                    result = CanonicalEntitlementAlertService.emit_sla_alerts(db_session)

                    assert result.skipped_duplicate_count == 1
                    assert result.emitted_count == 0


