import pytest
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.incident_service import (
    IncidentService,
    IncidentServiceError,
    SupportIncidentCreatePayload,
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


def test_create_and_update_incident_to_closed() -> None:
    _cleanup_tables()
    customer_user_id = _create_user("incident-customer@example.com", role="user")
    support_user_id = _create_user("incident-support@example.com", role="support")

    with SessionLocal() as db:
        incident = IncidentService.create_incident(
            db,
            payload=SupportIncidentCreatePayload(
                user_id=customer_user_id,
                category="account",
                title="Probleme de connexion",
                description="Impossible de me connecter depuis mobile.",
                priority="high",
                assigned_to_user_id=support_user_id,
            ),
            actor_user_id=support_user_id,
            request_id="rid-inc-unit-1",
        )
        assert incident.status == "open"

        moved = IncidentService.update_incident(
            db,
            incident_id=incident.incident_id,
            payload=SupportIncidentUpdatePayload(status="in_progress"),
            request_id="rid-inc-unit-2",
        )
        assert moved.status == "in_progress"

        closed = IncidentService.update_incident(
            db,
            incident_id=incident.incident_id,
            payload=SupportIncidentUpdatePayload(status="closed"),
            request_id="rid-inc-unit-3",
        )
        db.commit()
        assert closed.status == "closed"
        assert closed.resolved_at is not None


def test_update_incident_rejects_invalid_transition() -> None:
    _cleanup_tables()
    customer_user_id = _create_user("incident-customer-2@example.com", role="user")
    support_user_id = _create_user("incident-support-2@example.com", role="support")

    with SessionLocal() as db:
        incident = IncidentService.create_incident(
            db,
            payload=SupportIncidentCreatePayload(
                user_id=customer_user_id,
                category="content",
                title="Reponse hors sujet",
                description="Le chat a repondu hors scope.",
                priority="medium",
            ),
            actor_user_id=support_user_id,
            request_id="rid-inc-unit-4",
        )
        IncidentService.update_incident(
            db,
            incident_id=incident.incident_id,
            payload=SupportIncidentUpdatePayload(status="resolved"),
            request_id="rid-inc-unit-5",
        )
        with pytest.raises(IncidentServiceError) as error:
            IncidentService.update_incident(
                db,
                incident_id=incident.incident_id,
                payload=SupportIncidentUpdatePayload(status="in_progress"),
                request_id="rid-inc-unit-6",
            )

    assert error.value.code == "incident_invalid_transition"
