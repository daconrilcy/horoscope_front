# Commentaire global: garde legacy free-short apres suppression de l'ancien POST natal.
"""Verifie que l'ancien POST natal n'est plus une surface publique active."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session
from app.main import app


def test_old_public_endpoint_no_longer_resolves_free_short_variant(db_session) -> None:
    """La compat free_short n'est plus exposee par l'ancien endpoint generateur."""
    auth_user = AuthenticatedUser(
        id=432,
        email="free@example.com",
        role="user",
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[require_authenticated_user] = lambda: auth_user
    app.dependency_overrides[get_db_session] = lambda: db_session

    try:
        client = TestClient(app)
        with (
            patch("app.domain.llm.runtime.gateway.LLMGateway.execute_request") as gateway_mock,
            patch(
                "app.services.llm_generation.natal.interpretation_service."
                "NatalInterpretationService.interpret"
            ) as interpret_mock,
        ):
            response = client.post(
                "/v1/natal/interpretation",
                json={
                    "use_case_level": "complete",
                    "locale": "fr-FR",
                    "force_refresh": True,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    gateway_mock.assert_not_called()
    interpret_mock.assert_not_called()
