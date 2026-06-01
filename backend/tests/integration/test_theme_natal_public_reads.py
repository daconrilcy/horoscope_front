# Commentaire global: preuves API publiques accepted-only du theme natal.
"""Valide GET/list publics via TestClient et services canoniques."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.infra.db.session import get_db_session
from app.main import app

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


def test_public_list_and_get_return_only_accepted_interpretations(db: Session) -> None:
    """Les routes publiques masquent les lignes rejetees et exposent seulement accepted."""
    accepted = UserNatalInterpretationModel(
        user_id=435,
        chart_id="chart-cs-435-public-read",
        level=InterpretationLevel.SHORT,
        use_case="natal_interpretation_short",
        interpretation_payload={
            "title": "Lecture acceptee",
            "summary": "Resume accepte suffisamment clair.",
            "sections": [{"key": "overall", "heading": "Vue", "content": "Contenu public."}],
            "highlights": ["Point"],
            "advice": ["Conseil"],
            "evidence": [],
        },
        grounding_status="grounded",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    rejected = UserNatalInterpretationModel(
        user_id=435,
        chart_id="chart-cs-435-public-read",
        level=InterpretationLevel.COMPLETE,
        use_case="natal_interpretation",
        interpretation_payload=_REJECTED_PAYLOAD,
        grounding_status="rejected",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    db.add_all([accepted, rejected])
    db.commit()
    db.refresh(accepted)
    rejected_id = rejected.id

    app.dependency_overrides[require_authenticated_user] = _authenticated_user
    app.dependency_overrides[get_db_session] = lambda: db
    try:
        client = TestClient(app)
        list_response = client.get(
            "/v1/natal/interpretations",
            params={"chart_id": "chart-cs-435-public-read"},
        )
        accepted_response = client.get(f"/v1/natal/interpretations/{accepted.id}")
        rejected_response = client.get(f"/v1/natal/interpretations/{rejected_id}")
    finally:
        app.dependency_overrides.clear()

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert [item["id"] for item in list_response.json()["items"]] == [accepted.id]
    assert accepted_response.status_code == 200
    assert accepted_response.json()["meta"]["id"] == accepted.id
    assert rejected_response.status_code == 404


def _authenticated_user() -> AuthenticatedUser:
    """Retourne l'utilisateur public CS-435."""
    return AuthenticatedUser(
        id=435,
        role="user",
        email="cs-435@example.com",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
