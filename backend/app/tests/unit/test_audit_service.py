from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.user import UserModel
from app.services.auth_service import AuthService
from app.services.ops.audit_service import (
    AuditEventCreatePayload,
    AuditEventListFilters,
    AuditService,
    AuditServiceError,
)
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        db.execute(delete(AuditEventModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_user_id(email: str) -> int:
    with open_app_test_db_session() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123")
        db.commit()
        return auth.user.id


def test_record_and_list_audit_events_with_filters() -> None:
    _cleanup_tables()
    user_id = _create_user_id("audit-user@example.com")
    now = datetime.now(timezone.utc)

    with open_app_test_db_session() as db:
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id="rid-1",
                actor_user_id=user_id,
                actor_role="user",
                action="privacy_export",
                target_type="user",
                target_id=str(user_id),
                status="success",
            ),
        )
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id="rid-2",
                actor_user_id=user_id,
                actor_role="user",
                action="billing_plan_change",
                target_type="user",
                target_id=str(user_id),
                status="failed",
            ),
        )
        db.commit()

    with open_app_test_db_session() as db:
        result = AuditService.list_events(
            db,
            filters=AuditEventListFilters(
                action="privacy_export",
                status="success",
                target_user_id=user_id,
                date_from=now - timedelta(minutes=1),
                date_to=now + timedelta(minutes=1),
                limit=10,
                offset=0,
            ),
        )

    assert result.total == 1
    assert len(result.events) == 1
    assert result.events[0].action == "privacy_export"
    assert result.events[0].status == "success"


def test_list_events_rejects_invalid_limit() -> None:
    _cleanup_tables()
    with open_app_test_db_session() as db:
        with pytest.raises(AuditServiceError) as error:
            AuditService.list_events(
                db,
                filters=AuditEventListFilters(limit=0, offset=0),
            )
    assert error.value.code == "audit_validation_error"
