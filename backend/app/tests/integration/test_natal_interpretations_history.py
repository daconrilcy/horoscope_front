"""Tests d'intégration pour l'extinction publique de l'historique natal."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session
from app.main import app


def _override_auth() -> AuthenticatedUser:
    return AuthenticatedUser(
        id=1,
        role="user",
        email="test-user@example.com",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_db():
    mock = MagicMock()
    return mock


@pytest.fixture
def test_client(mock_db):
    app.dependency_overrides[require_authenticated_user] = _override_auth
    app.dependency_overrides[get_db_session] = lambda: mock_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestNatalInterpretationsHistory:
    """Verrouille l'absence des anciennes routes publiques d'historique."""

    @pytest.mark.parametrize(
        ("method_name", "path"),
        [
            ("get", "/v1/natal/interpretations"),
            ("get", "/v1/natal/interpretations/123"),
            ("delete", "/v1/natal/interpretations/123"),
        ],
    )
    def test_historical_routes_are_unmounted(
        self,
        test_client: TestClient,
        mock_db: MagicMock,
        method_name: str,
        path: str,
    ) -> None:
        """Les anciennes routes list/get/delete ne gardent aucune facade publique."""
        response = getattr(test_client, method_name)(path)

        assert response.status_code == 404
        mock_db.execute.assert_not_called()
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()

    def test_historical_routes_are_absent_from_openapi(self) -> None:
        """OpenAPI ne publie plus le sous-arbre historique d'interpretations."""
        openapi_paths = set(app.openapi()["paths"])

        assert all(not path.startswith("/v1/natal/interpretations") for path in openapi_paths)
