# Commentaire global: preuves API publiques accepted-only du theme natal.
"""Valide GET/list publics via TestClient et services canoniques."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.infra.db.session import get_db_session
from app.main import app
from tests.integration.app_db import open_app_db_session

_REJECTED_PAYLOAD = {
    "status": "rejected",
    "rejection_reason": {"code": "theme_natal_basic_provider_rejected"},
    "client_message": "Message controle.",
    "title": "",
    "summary": "Message controle.",
    "sections": [],
    "highlights": [],
    "advice": [],
    "evidence": [],
}


def test_public_list_and_get_return_only_accepted_interpretations() -> None:
    """Les routes publiques masquent les lignes rejetees et exposent seulement accepted."""
    chart_id = f"chart-cs-440-public-read-{uuid.uuid4().hex}"
    user = UserModel(
        id=435,
        email=f"cs-440-public-read-{uuid.uuid4().hex}@example.com",
        password_hash="x",
        role="user",
    )
    accepted = UserNatalInterpretationModel(
        user_id=435,
        chart_id=chart_id,
        level=InterpretationLevel.SHORT,
        use_case="natal_interpretation_short",
        interpretation_payload={
            "title": "Lecture acceptee",
            "summary": "Resume accepte suffisamment clair.",
            "sections": [
                {"key": "overall", "heading": "Vue", "content": "Contenu public."},
                {"key": "career", "heading": "Focus", "content": "Deuxieme contenu public."},
            ],
            "highlights": ["Point un", "Point deux", "Point trois"],
            "advice": ["Conseil un", "Conseil deux", "Conseil trois"],
            "evidence": [],
        },
        grounding_status="grounded",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    rejected = UserNatalInterpretationModel(
        user_id=435,
        chart_id=chart_id,
        level=InterpretationLevel.COMPLETE,
        use_case="natal_interpretation",
        interpretation_payload=_REJECTED_PAYLOAD,
        grounding_status="rejected",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    with open_app_db_session() as db:
        db.merge(user)
        db.add_all([accepted, rejected])
        db.commit()
        db.refresh(accepted)
        accepted_id = accepted.id
        rejected_id = rejected.id

    app.dependency_overrides[require_authenticated_user] = _authenticated_user
    app.dependency_overrides[get_db_session] = _override_db_session
    try:
        client = TestClient(app)
        list_response = client.get(
            "/v1/natal/interpretations",
            params={"chart_id": chart_id},
        )
        accepted_response = client.get(f"/v1/natal/interpretations/{accepted_id}")
        rejected_response = client.get(f"/v1/natal/interpretations/{rejected_id}")
    finally:
        app.dependency_overrides.clear()

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert [item["id"] for item in list_response.json()["items"]] == [accepted_id]
    assert accepted_response.status_code == 200
    assert accepted_response.json()["data"]["meta"]["id"] == accepted_id
    assert rejected_response.status_code == 404


def _authenticated_user() -> AuthenticatedUser:
    """Retourne l'utilisateur public CS-435."""
    return AuthenticatedUser(
        id=435,
        role="user",
        email="cs-435@example.com",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )


def _override_db_session() -> Iterator[Session]:
    """Ouvre une session DB dans le thread effectif du TestClient."""
    with open_app_db_session() as db:
        yield db
