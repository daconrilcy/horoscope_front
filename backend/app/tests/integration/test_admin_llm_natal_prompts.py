"""Tests d'intégration pour la gestion des prompts LLM via l'API admin."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.session import get_db_session
from app.main import app


def _override_admin_auth() -> AuthenticatedUser:
    """Override de l'authentification pour un admin."""
    return AuthenticatedUser(
        id=1,
        role="admin",
        email="admin@example.com",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def test_client(mock_db):
    """Client de test avec dépendances mockées."""
    app.dependency_overrides[require_authenticated_user] = _override_admin_auth
    app.dependency_overrides[get_db_session] = lambda: mock_db
    client = TestClient(app)
    # Mocking AuditService to avoid DB side effects and validation errors
    with patch("app.services.ops.audit_service.AuditService.record_event"):
        yield client
    app.dependency_overrides.clear()


class TestAdminLlmNatalPrompts:
    """Tests pour la gestion des prompts nataux."""

    def test_create_prompt_draft_valid(self, test_client, mock_db):
        key = "natal"
        uc_mock = LlmUseCaseConfigModel(
            key=key,
            display_name="Natal",
            description="...",
            required_prompt_placeholders=["chart_json", "persona_name"],
        )

        # Patching db.add to simulate auto-assignment of fields
        def mock_add(obj):
            if isinstance(obj, LlmPromptVersionModel):
                obj.id = uuid.uuid4()
                obj.created_at = datetime.now(timezone.utc)

        mock_db.add.side_effect = mock_add

        # Mocking db.get to return uc_mock
        mock_db.get.return_value = uc_mock

        prompt_text = (
            "Langue: {{locale}}. UC: {{use_case}}. Persona: {{persona_name}}. Chart: {{chart_json}}"
        )
        payload = {
            "developer_prompt": prompt_text,
        }

        response = test_client.post(f"/v1/admin/llm/use-cases/{key}/prompts", json=payload)

        assert response.status_code == 200
        assert response.json()["data"]["use_case_key"] == key
        assert response.json()["data"]["status"] == "draft"

    def test_create_prompt_draft_invalid_lint(self, test_client, mock_db):
        key = "natal"
        uc_mock = LlmUseCaseConfigModel(
            key=key,
            display_name="Natal",
            description="...",
            required_prompt_placeholders=["chart_json", "persona_name"],
        )

        mock_db.get.return_value = uc_mock

        # Missing {{persona_name}}
        payload = {
            "developer_prompt": "Langue: {{locale}}. UC: {{use_case}}. Chart: {{chart_json}}",
        }

        response = test_client.post(f"/v1/admin/llm/use-cases/{key}/prompts", json=payload)

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "lint_failed"
        assert any("persona_name" in e for e in response.json()["error"]["details"]["errors"])

    def test_publish_prompt_success(self, test_client, mock_db):
        key = "natal_interpretation_short"
        version_id = str(uuid.uuid4())
        uc_mock = LlmUseCaseConfigModel(
            key=key, display_name="Natal", description="...", eval_fixtures_path=None
        )

        version_mock = LlmPromptVersionModel(
            id=uuid.UUID(version_id),
            use_case_key=key,
            status=PromptStatus.DRAFT,
            developer_prompt="...",
            created_by="1",
            created_at=datetime.now(timezone.utc),
        )

        mock_db.get.return_value = uc_mock

        with (
            patch("app.ops.llm.prompt_registry_v2.PromptRegistryV2.publish_prompt") as mock_publish,
            patch(
                "app.api.v1.routers.admin.llm.prompts.PromptRegistryV2.get_active_prompt",
                return_value=version_mock,
            ),
            patch(
                "app.api.v1.routers.admin.llm.prompts._build_canonical_admin_use_case_config",
                return_value=None,
            ),
        ):
            mock_publish.return_value = version_mock
            version_mock.status = PromptStatus.PUBLISHED  # simulate effect

            response = test_client.patch(
                f"/v1/admin/llm/use-cases/{key}/prompts/{version_id}/publish"
            )

        assert response.status_code == 200
        assert response.json()["data"]["status"] == "published"

    def test_publish_prompt_blocked_by_eval(self, test_client, mock_db):
        from app.domain.llm.runtime.contracts import EvalReport

        key = "natal_interpretation_short"
        version_id = str(uuid.uuid4())
        uc_mock = LlmUseCaseConfigModel(
            key=key,
            display_name="Natal",
            description="...",
            eval_fixtures_path="path/to/fixtures",
            eval_failure_threshold=0.20,
        )

        mock_db.get.return_value = uc_mock

        # Mock a report with 50% failure
        report = EvalReport(
            use_case=key,
            prompt_version_id=version_id,
            total=10,
            passed=5,
            failed=5,
            failure_rate=0.5,
            blocked_publication=False,
            results=[],
        )

        active_prompt = LlmPromptVersionModel(
            id=uuid.uuid4(),
            use_case_key=key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="...",
            created_by="qa",
            created_at=datetime.now(timezone.utc),
        )

        with (
            patch("app.api.v1.routers.admin.llm.prompts.run_eval") as mock_run_eval,
            patch(
                "app.api.v1.routers.admin.llm.prompts.PromptRegistryV2.get_active_prompt",
                return_value=active_prompt,
            ),
            patch(
                "app.api.v1.routers.admin.llm.prompts._build_canonical_admin_use_case_config",
                return_value=None,
            ),
            patch(
                "app.api.v1.routers.admin.llm.prompts.PromptRegistryV2.publish_prompt",
                return_value=active_prompt,
            ),
        ):
            mock_run_eval.return_value = report

            url = f"/v1/admin/llm/use-cases/{key}/prompts/{version_id}/publish"
            response = test_client.patch(url)

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "eval_failed"
        assert response.json()["error"]["details"]["failure_rate"] == 0.5

    def test_publish_prompt_forbidden_for_legacy_daily_prediction(self, test_client, mock_db):
        key = "daily_prediction"
        version_id = str(uuid.uuid4())
        uc_mock = LlmUseCaseConfigModel(
            key=key, display_name="Legacy Daily", description="...", eval_fixtures_path=None
        )
        mock_db.get.return_value = uc_mock

        response = test_client.patch(f"/v1/admin/llm/use-cases/{key}/prompts/{version_id}/publish")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "use_case_not_found"

    def test_rollback_prompt_forbidden_for_legacy_daily_prediction(self, test_client, mock_db):
        key = "daily_prediction"
        uc_mock = LlmUseCaseConfigModel(key=key, display_name="Legacy Daily", description="...")
        mock_db.get.return_value = uc_mock

        response = test_client.post(f"/v1/admin/llm/use-cases/{key}/rollback")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "use_case_not_found"
