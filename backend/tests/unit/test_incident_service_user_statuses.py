from datetime import datetime, timezone

from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.ops.incident_service import (
    ALLOWED_STATUS_TRANSITIONS,
    IncidentService,
    SupportIncidentUpdatePayload,
)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(SupportIncidentModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_user(email: str, role: str = "user") -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.user.id


def test_incident_status_transitions_user():
    # Valid transitions from pending
    assert "solved" in ALLOWED_STATUS_TRANSITIONS["pending"]
    assert "canceled" in ALLOWED_STATUS_TRANSITIONS["pending"]
    assert "in_progress" in ALLOWED_STATUS_TRANSITIONS["pending"]

    # Valid transitions from solved
    assert "canceled" in ALLOWED_STATUS_TRANSITIONS["solved"]

    # Invalid transition from solved
    assert "pending" not in ALLOWED_STATUS_TRANSITIONS["solved"]


def test_resolved_at_logic_user() -> None:
    _cleanup_tables()
    user_id = _create_user("test-user-status@example.com")

    with SessionLocal() as db:
        # Create incident with status pending
        incident_model = SupportIncidentModel(
            user_id=user_id,
            category="account",
            title="Test",
            description="Test",
            status="pending",
            priority="low",
            created_at=datetime.now(timezone.utc),
        )
        db.add(incident_model)
        db.commit()

        incident_id = incident_model.id
        assert incident_model.resolved_at is None

        # Update to solved (Valid: pending -> solved)
        IncidentService.update_incident(
            db,
            incident_id=incident_id,
            payload=SupportIncidentUpdatePayload(status="solved"),
            request_id="test-rid-1",
        )
        db.refresh(incident_model)
        assert incident_model.resolved_at is not None

        # Update to canceled (Valid: solved -> canceled)
        IncidentService.update_incident(
            db,
            incident_id=incident_id,
            payload=SupportIncidentUpdatePayload(status="canceled"),
            request_id="test-rid-2",
        )
        db.refresh(incident_model)
        assert incident_model.resolved_at is not None

        # Reset to pending for another test path
        # Note: transitions to pending are not explicitly in ALLOWED_STATUS_TRANSITIONS for users
        # but let's assume we can manually set it or we create a new incident.
        db.execute(delete(SupportIncidentModel))
        db.commit()

        incident_model = SupportIncidentModel(
            user_id=user_id,
            category="account",
            title="T2",
            description="D2",
            status="pending",
            priority="low",
            created_at=datetime.now(timezone.utc),
        )
        db.add(incident_model)
        db.commit()
        incident_id = incident_model.id

        # Update to in_progress (Valid: pending -> in_progress)
        IncidentService.update_incident(
            db,
            incident_id=incident_id,
            payload=SupportIncidentUpdatePayload(status="in_progress"),
            request_id="test-rid-3",
        )
        db.refresh(incident_model)
        assert incident_model.resolved_at is None
