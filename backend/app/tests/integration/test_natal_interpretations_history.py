"""Tests d'intégration pour l'historique des interprétations natales."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
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
    def test_list_interpretations_empty(self, test_client, mock_db):
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        mock_db.scalar.return_value = 0

        response = test_client.get("/v1/natal/interpretations")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_interpretations_with_items(self, test_client, mock_db):
        item = UserNatalInterpretationModel(
            id=123,
            user_id=1,
            chart_id="chart-1",
            level=InterpretationLevel.SHORT,
            use_case="natal_interpretation_short",
            interpretation_payload={"title": "Test"},
            created_at=datetime.now(timezone.utc),
            was_fallback=False,
        )
        mock_db.execute.return_value.scalars.return_value.all.return_value = [item]
        mock_db.scalar.return_value = 1

        response = test_client.get("/v1/natal/interpretations", params={"chart_id": "chart-1"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == 123
        assert data["items"][0]["chart_id"] == "chart-1"

    def test_list_interpretations_with_module_filter(self, test_client, mock_db):
        item = UserNatalInterpretationModel(
            id=456,
            user_id=1,
            chart_id="chart-1",
            level=InterpretationLevel.COMPLETE,
            use_case="natal_psy_profile",
            interpretation_payload={
                "title": "Psy Profile",
                "summary": "A complete psy profile interpretation.",
            },
            created_at=datetime.now(timezone.utc),
            was_fallback=False,
        )
        mock_db.execute.return_value.scalars.return_value.all.return_value = [item]
        mock_db.scalar.return_value = 1

        response = test_client.get(
            "/v1/natal/interpretations",
            params={"chart_id": "chart-1", "module": "NATAL_PSY_PROFILE"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["module"] == "natal_psy_profile"

    def test_get_interpretation_success(self, test_client, mock_db):
        item = UserNatalInterpretationModel(
            id=123,
            user_id=1,
            chart_id="chart-1",
            level=InterpretationLevel.SHORT,
            use_case="natal_interpretation_short",
            interpretation_payload={
                "title": "Test",
                "summary": "...",
                "sections": [
                    {"key": "overall", "heading": "h1", "content": "c1"},
                    {"key": "career", "heading": "h2", "content": "c2"},
                ],
                "highlights": ["1", "2", "3"],
                "advice": ["1", "2", "3"],
                "evidence": [],
            },
            created_at=datetime.now(timezone.utc),
            was_fallback=False,
        )
        mock_db.execute.return_value.scalar_one_or_none.return_value = item

        response = test_client.get("/v1/natal/interpretations/123")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["chart_id"] == "chart-1"
        assert data["data"]["interpretation"]["title"] == "Test"

    def test_get_interpretation_not_found(self, test_client, mock_db):
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        response = test_client.get("/v1/natal/interpretations/999")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "interpretation_not_found"

    def test_delete_interpretation_success(self, test_client, mock_db):
        item = UserNatalInterpretationModel(
            id=123,
            user_id=1,
            chart_id=1,
            level=InterpretationLevel.SHORT,
            use_case="natal_interpretation_short",
            created_at=datetime.now(timezone.utc),
        )
        mock_db.execute.return_value.scalar_one_or_none.return_value = item

        with patch("app.services.ops.audit_service.AuditService.record_event") as mock_audit:
            response = test_client.delete("/v1/natal/interpretations/123")
            assert response.status_code == 204
            mock_db.delete.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_audit.assert_called_once()

    def test_delete_interpretation_not_found(self, test_client, mock_db):
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        response = test_client.delete("/v1/natal/interpretations/999")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "interpretation_not_found"
