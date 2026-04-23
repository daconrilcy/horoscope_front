import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_admin_user
from app.domain.llm.runtime.contracts import GoldenRegressionReport
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.main import app


# Mocking admin user
async def mock_admin_user():
    return MagicMock(id=123, role="admin")


@pytest.mark.asyncio
async def test_publish_prompt_blocks_on_golden_regression():
    app.dependency_overrides[require_admin_user] = mock_admin_user
    client = TestClient(app)

    # We need to patch the DB session dependency
    from app.infra.db.session import get_db_session

    db = MagicMock()
    app.dependency_overrides[get_db_session] = lambda: db

    try:
        # 1. Setup use case with golden_set_path
        uc = LlmUseCaseConfigModel(
            key="natal_test_66_36",
            display_name="Natal Test",
            golden_set_path="tests/fixtures/golden/natal_test.yaml",
            eval_fixtures_path=None,  # Disable eval harness for this test
        )

        from datetime import datetime, timezone

        version_id = uuid.uuid4()
        version = LlmPromptVersionModel(
            id=version_id,
            use_case_key="natal_test_66_36",
            status=PromptStatus.DRAFT,
            developer_prompt="Test",
            model="gpt-4o",
            temperature=0.7,
            max_output_tokens=1000,
            created_by="test",
            created_at=datetime.now(timezone.utc),
        )

        def mock_get(model, key):
            if model == LlmUseCaseConfigModel:
                return uc
            if model == LlmPromptVersionModel or str(model) == str(LlmPromptVersionModel):
                return version
            return None

        db.get.side_effect = mock_get

        # 2. Mock GoldenRegressionService to fail
        mock_report = GoldenRegressionReport(
            environment="test",
            verdict="fail",
            total=1,
            passed=0,
            failed=1,
            constrained=0,
            results=[],
        )

        with patch(
            "app.ops.llm.golden_regression_service.GoldenRegressionService.run_campaign",
            return_value=mock_report,
        ):
            response = client.patch(
                f"/v1/admin/llm/use-cases/natal_test_66_36/prompts/{version_id}/publish"
            )

            assert response.status_code == 409
            assert response.json()["error"]["code"] == "golden_regression_failed"
            assert "fail" in response.json()["error"]["message"]

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_publish_prompt_blocks_on_golden_invalid():
    app.dependency_overrides[require_admin_user] = mock_admin_user
    client = TestClient(app)

    from app.infra.db.session import get_db_session

    db = MagicMock()
    app.dependency_overrides[get_db_session] = lambda: db

    try:
        uc = LlmUseCaseConfigModel(
            key="natal_test_invalid",
            display_name="Natal Test Invalid",
            golden_set_path="NON_EXISTENT_PATH",
            eval_fixtures_path=None,
        )

        from datetime import datetime, timezone

        version_id = uuid.uuid4()
        version = LlmPromptVersionModel(
            id=version_id,
            use_case_key="natal_test_invalid",
            status=PromptStatus.DRAFT,
            developer_prompt="Test",
            model="gpt-4o",
            temperature=0.7,
            max_output_tokens=1000,
            created_by="test",
            created_at=datetime.now(timezone.utc),
        )

        def mock_get(model, key):
            if model == LlmUseCaseConfigModel:
                return uc
            return version

        db.get.side_effect = mock_get

        # Mock GoldenRegressionService to return invalid
        mock_report = GoldenRegressionReport(
            environment="test",
            verdict="invalid",
            total=0,
            passed=0,
            failed=0,
            constrained=0,
            results=[],
        )

        with patch(
            "app.ops.llm.golden_regression_service.GoldenRegressionService.run_campaign",
            return_value=mock_report,
        ):
            response = client.patch(
                f"/v1/admin/llm/use-cases/natal_test_invalid/prompts/{version_id}/publish"
            )

            # High Fix: invalid MUST block
            assert response.status_code == 409
            assert response.json()["error"]["code"] == "golden_regression_failed"
            assert "invalid" in response.json()["error"]["message"]

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_publish_prompt_warns_on_golden_constrained():
    app.dependency_overrides[require_admin_user] = mock_admin_user
    client = TestClient(app)

    from app.infra.db.session import get_db_session

    db = MagicMock()
    app.dependency_overrides[get_db_session] = lambda: db

    try:
        uc = LlmUseCaseConfigModel(
            key="natal_test_warn",
            display_name="Natal Test Warn",
            golden_set_path="tests/fixtures/golden/natal_test.yaml",
            eval_fixtures_path=None,
        )

        from datetime import datetime, timezone

        version_id = uuid.uuid4()
        version = LlmPromptVersionModel(
            id=version_id,
            use_case_key="natal_test_warn",
            status=PromptStatus.DRAFT,
            developer_prompt="Test",
            model="gpt-4o",
            temperature=0.7,
            max_output_tokens=1000,
            created_by="test",
            created_at=datetime.now(timezone.utc),
        )

        def mock_get(model, key):
            if model == LlmUseCaseConfigModel:
                return uc
            return version

        db.get.side_effect = mock_get

        # Mock GoldenRegressionService to return constrained
        mock_report = GoldenRegressionReport(
            environment="test",
            verdict="constrained",
            total=1,
            passed=0,
            failed=0,
            constrained=1,
            results=[],
        )

        with patch(
            "app.ops.llm.golden_regression_service.GoldenRegressionService.run_campaign",
            return_value=mock_report,
        ):
            with patch(
                "app.ops.llm.prompt_registry_v2.PromptRegistryV2.publish_prompt",
                return_value=version,
            ):
                response = client.patch(
                    f"/v1/admin/llm/use-cases/natal_test_warn/prompts/{version_id}/publish"
                )

                # Medium Fix: constrained allows publish but with warning
                assert response.status_code == 200
                assert "golden_regression_constrained_drift" in response.json()["meta"]["warnings"]

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_publish_prompt_passes_on_golden_success():
    app.dependency_overrides[require_admin_user] = mock_admin_user
    client = TestClient(app)

    from app.infra.db.session import get_db_session

    db = MagicMock()
    app.dependency_overrides[get_db_session] = lambda: db

    try:
        # 1. Setup use case with golden_set_path
        uc = LlmUseCaseConfigModel(
            key="natal_test_ok",
            display_name="Natal Test OK",
            golden_set_path="tests/fixtures/golden/natal_test.yaml",
            eval_fixtures_path=None,
        )

        from datetime import datetime, timezone

        version_id = uuid.uuid4()
        version = LlmPromptVersionModel(
            id=version_id,
            use_case_key="natal_test_ok",
            status=PromptStatus.DRAFT,
            developer_prompt="Test",
            model="gpt-4o",
            temperature=0.7,
            max_output_tokens=1000,
            created_by="test",
            created_at=datetime.now(timezone.utc),
        )

        def mock_get(model, key):
            if model == LlmUseCaseConfigModel:
                return uc
            return version

        db.get.side_effect = mock_get

        # 2. Mock GoldenRegressionService to pass
        mock_report = GoldenRegressionReport(
            environment="test",
            verdict="pass",
            total=1,
            passed=1,
            failed=0,
            constrained=0,
            results=[],
        )

        # Need to mock PromptRegistryV2.publish_prompt too
        with patch(
            "app.ops.llm.golden_regression_service.GoldenRegressionService.run_campaign",
            return_value=mock_report,
        ):
            with patch(
                "app.ops.llm.prompt_registry_v2.PromptRegistryV2.publish_prompt",
                return_value=version,
            ):
                response = client.patch(
                    f"/v1/admin/llm/use-cases/natal_test_ok/prompts/{version_id}/publish"
                )

                assert response.status_code == 200

                assert response.json()["meta"]["golden_report"] is not None
                assert response.json()["meta"]["golden_report"]["verdict"] == "pass"

    finally:
        app.dependency_overrides.clear()
