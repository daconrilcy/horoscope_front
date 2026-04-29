import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.llm.runtime.contracts import (
    ContextCompensationStatus,
    ExecutionObservabilitySnapshot,
    ExecutionPathKind,
    GatewayMeta,
    GatewayResult,
    MaxTokensSource,
    UsageInfo,
)
from app.ops.llm.golden_regression_service import GoldenRegressionService


def _mock_release_context(db: MagicMock, manifest: dict | None = None) -> uuid.UUID:
    snapshot_id = uuid.uuid4()
    snapshot = MagicMock()
    snapshot.version = "snapshot-v1"
    snapshot.manifest = manifest or {
        "targets": {
            "natal:interpretation:free:fr-FR": {},
        }
    }
    db.execute.return_value.scalar_one_or_none.return_value = snapshot
    return snapshot_id


@pytest.mark.asyncio
async def test_golden_regression_campaign_pass():
    # Setup mocks
    mock_result = MagicMock(spec=GatewayResult)
    mock_result.structured_output = {
        "interpretation": "Lune en Cancer",
        "key_points": ["Sensibilité"],
    }
    mock_result.meta = MagicMock(spec=GatewayMeta)
    mock_result.meta.validation_status = "valid"
    mock_result.meta.execution_profile_source = "assembly"
    mock_result.meta.obs_snapshot = ExecutionObservabilitySnapshot(
        pipeline_kind="nominal_canonical",
        execution_path_kind=ExecutionPathKind.CANONICAL_ASSEMBLY,
        fallback_kind=None,
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        context_quality="nominal",
        context_compensation_status=ContextCompensationStatus.INJECTOR_APPLIED,
        max_output_tokens_source=MaxTokensSource.EXECUTION_PROFILE,
        max_output_tokens_final=1000,
    )
    mock_result.usage = UsageInfo(input_tokens=100, output_tokens=50)

    db = MagicMock()
    snapshot_id = _mock_release_context(db)

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        with patch(
            "app.domain.llm.configuration.active_release.get_active_release_id",
            new_callable=AsyncMock,
            return_value=snapshot_id,
        ):
            report = await GoldenRegressionService.run_campaign(
                use_case_key="natal",
                prompt_version_id="test-v1",
                golden_set_path="tests/fixtures/golden/natal_test.yaml",
                db=db,
            )

        assert report.verdict == "pass"
        assert report.total == 1
        assert report.passed == 1
        assert report.active_snapshot_id == snapshot_id
        assert report.active_snapshot_version == "snapshot-v1"
        assert report.manifest_entry_id == "natal:interpretation:free:fr-FR"


@pytest.mark.asyncio
async def test_golden_regression_campaign_fail_legacy():
    # Legacy path detected -> Fail
    mock_result = MagicMock(spec=GatewayResult)
    mock_result.structured_output = {
        "interpretation": "Lune en Cancer",
        "key_points": ["Sensibilité"],
    }
    mock_result.meta = MagicMock(spec=GatewayMeta)
    mock_result.meta.execution_profile_source = "fallback_resolve_model"
    mock_result.meta.obs_snapshot = ExecutionObservabilitySnapshot(
        pipeline_kind="transitional_governance",
        execution_path_kind=ExecutionPathKind.LEGACY_USE_CASE_FALLBACK,
        fallback_kind="use_case_first",
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        context_quality="unknown",
        context_compensation_status=ContextCompensationStatus.UNKNOWN,
        max_output_tokens_source=MaxTokensSource.UNSET,
        max_output_tokens_final=500,
    )
    mock_result.usage = UsageInfo(input_tokens=100, output_tokens=50)

    db = MagicMock()
    snapshot_id = _mock_release_context(db)

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        with patch(
            "app.domain.llm.configuration.active_release.get_active_release_id",
            new_callable=AsyncMock,
            return_value=snapshot_id,
        ):
            report = await GoldenRegressionService.run_campaign(
                use_case_key="natal",
                prompt_version_id="test-v1",
                golden_set_path="tests/fixtures/golden/natal_test.yaml",
                db=db,
            )

        assert report.verdict == "fail"
        assert len(report.results[0].legacy_errors) > 0
        assert "Forbidden legacy execution path" in report.results[0].legacy_errors[0]
        assert any(
            "Forbidden legacy execution profile source" in error
            for error in report.results[0].legacy_errors
        )


@pytest.mark.asyncio
async def test_golden_regression_campaign_fail_structure():
    # Structural drift -> Fail
    mock_result = MagicMock(spec=GatewayResult)
    mock_result.structured_output = {
        "interpretation": 123,
        "key_points": "not a list",
    }  # WRONG SHAPE
    mock_result.meta = MagicMock(spec=GatewayMeta)
    mock_result.meta.validation_status = "error"
    mock_result.meta.execution_profile_source = "assembly"
    mock_result.meta.obs_snapshot = ExecutionObservabilitySnapshot(
        pipeline_kind="nominal_canonical",
        execution_path_kind=ExecutionPathKind.CANONICAL_ASSEMBLY,
        fallback_kind=None,
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        context_quality="nominal",
        context_compensation_status=ContextCompensationStatus.INJECTOR_APPLIED,
        max_output_tokens_source=MaxTokensSource.EXECUTION_PROFILE,
        max_output_tokens_final=1000,
    )
    mock_result.usage = UsageInfo(input_tokens=100, output_tokens=50)

    db = MagicMock()
    snapshot_id = _mock_release_context(db)

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        with patch(
            "app.domain.llm.configuration.active_release.get_active_release_id",
            new_callable=AsyncMock,
            return_value=snapshot_id,
        ):
            report = await GoldenRegressionService.run_campaign(
                use_case_key="natal",
                prompt_version_id="test-v1",
                golden_set_path="tests/fixtures/golden/natal_test.yaml",
                db=db,
            )

        assert report.verdict == "fail"
        assert "output_shape" in report.results[0].diffs_structure
        assert "validation_status" in report.results[0].diffs_structure


@pytest.mark.asyncio
async def test_golden_regression_campaign_fail_obs_strict():
    # Strict field mismatch -> Fail
    mock_result = MagicMock(spec=GatewayResult)
    mock_result.structured_output = {
        "interpretation": "Lune en Cancer",
        "key_points": ["Sensibilité"],
    }
    mock_result.meta = MagicMock(spec=GatewayMeta)
    mock_result.meta.validation_status = "valid"
    mock_result.meta.execution_profile_source = "assembly"
    mock_result.meta.obs_snapshot = ExecutionObservabilitySnapshot(
        pipeline_kind="nominal_canonical",
        execution_path_kind=ExecutionPathKind.CANONICAL_ASSEMBLY,
        fallback_kind=None,
        requested_provider="anthropic",  # DIFFERENT
        resolved_provider="openai",
        executed_provider="anthropic",  # DIFFERENT
        context_quality="nominal",
        context_compensation_status=ContextCompensationStatus.INJECTOR_APPLIED,
        max_output_tokens_source=MaxTokensSource.EXECUTION_PROFILE,
        max_output_tokens_final=1000,
    )
    mock_result.usage = UsageInfo(input_tokens=100, output_tokens=50)

    db = MagicMock()
    snapshot_id = _mock_release_context(db)

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        with patch(
            "app.domain.llm.configuration.active_release.get_active_release_id",
            new_callable=AsyncMock,
            return_value=snapshot_id,
        ):
            report = await GoldenRegressionService.run_campaign(
                use_case_key="natal",
                prompt_version_id="test-v1",
                golden_set_path="tests/fixtures/golden/natal_test.yaml",
                db=db,
            )

        assert report.verdict == "fail"
        assert "requested_provider" in report.results[0].diffs_obs


@pytest.mark.asyncio
async def test_golden_regression_canonicalization():
    # Verify that key order in structured output doesn't cause a failure
    mock_result = MagicMock(spec=GatewayResult)
    # Different key order than what might be expected but same shape
    mock_result.structured_output = {
        "key_points": ["Sensibilité"],
        "interpretation": "Lune en Cancer",
    }
    mock_result.meta = MagicMock(spec=GatewayMeta)
    mock_result.meta.validation_status = "valid"
    mock_result.meta.execution_profile_source = "assembly"
    mock_result.meta.obs_snapshot = ExecutionObservabilitySnapshot(
        pipeline_kind="nominal_canonical",
        execution_path_kind=ExecutionPathKind.CANONICAL_ASSEMBLY,
        fallback_kind=None,
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        context_quality="nominal",
        context_compensation_status=ContextCompensationStatus.INJECTOR_APPLIED,
        max_output_tokens_source=MaxTokensSource.EXECUTION_PROFILE,
        max_output_tokens_final=1000,
    )
    mock_result.usage = UsageInfo(input_tokens=100, output_tokens=50)

    db = MagicMock()
    snapshot_id = _mock_release_context(db)

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        with patch(
            "app.domain.llm.configuration.active_release.get_active_release_id",
            new_callable=AsyncMock,
            return_value=snapshot_id,
        ):
            report = await GoldenRegressionService.run_campaign(
                use_case_key="natal",
                prompt_version_id="test-v1",
                golden_set_path="tests/fixtures/golden/natal_test.yaml",
                db=db,
            )

        # Should pass because _canonicalize handles sorting and _get_shape focuses on structure
        assert report.verdict == "pass"


@pytest.mark.asyncio
async def test_golden_regression_campaign_invalid_without_active_release():
    mock_result = MagicMock(spec=GatewayResult)
    mock_result.structured_output = {"interpretation": "ok", "key_points": ["a"]}
    mock_result.meta = MagicMock(spec=GatewayMeta)
    mock_result.meta.validation_status = "valid"
    mock_result.meta.execution_profile_source = "assembly"
    mock_result.meta.obs_snapshot = ExecutionObservabilitySnapshot(
        pipeline_kind="nominal_canonical",
        execution_path_kind=ExecutionPathKind.CANONICAL_ASSEMBLY,
        fallback_kind=None,
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        context_quality="nominal",
        context_compensation_status=ContextCompensationStatus.INJECTOR_APPLIED,
        max_output_tokens_source=MaxTokensSource.EXECUTION_PROFILE,
        max_output_tokens_final=1000,
    )
    mock_result.usage = UsageInfo(input_tokens=10, output_tokens=5)

    db = MagicMock()
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        with patch(
            "app.domain.llm.configuration.active_release.get_active_release_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            report = await GoldenRegressionService.run_campaign(
                use_case_key="natal",
                prompt_version_id="test-v1",
                golden_set_path="tests/fixtures/golden/natal_test.yaml",
                db=db,
            )

    assert report.verdict == "invalid"
    assert report.results[0].verdict == "invalid"


@pytest.mark.asyncio
async def test_golden_regression_campaign_invalid_when_manifest_unresolved():
    mock_result = MagicMock(spec=GatewayResult)
    mock_result.structured_output = {"interpretation": "ok", "key_points": ["a"]}
    mock_result.meta = MagicMock(spec=GatewayMeta)
    mock_result.meta.validation_status = "valid"
    mock_result.meta.execution_profile_source = "assembly"
    mock_result.meta.obs_snapshot = ExecutionObservabilitySnapshot(
        pipeline_kind="nominal_canonical",
        execution_path_kind=ExecutionPathKind.CANONICAL_ASSEMBLY,
        fallback_kind=None,
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        context_quality="nominal",
        context_compensation_status=ContextCompensationStatus.INJECTOR_APPLIED,
        max_output_tokens_source=MaxTokensSource.EXECUTION_PROFILE,
        max_output_tokens_final=1000,
    )
    mock_result.usage = UsageInfo(input_tokens=10, output_tokens=5)

    db = MagicMock()
    snapshot_id = _mock_release_context(
        db,
        manifest={
            "targets": {
                "chat:None:free:fr-FR": {},
                "guidance:None:free:fr-FR": {},
            }
        },
    )

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        with patch(
            "app.domain.llm.configuration.active_release.get_active_release_id",
            new_callable=AsyncMock,
            return_value=snapshot_id,
        ):
            report = await GoldenRegressionService.run_campaign(
                use_case_key="natal",
                prompt_version_id="test-v1",
                golden_set_path="tests/fixtures/golden/natal_test.yaml",
                db=db,
            )

    assert report.verdict == "invalid"


@pytest.mark.asyncio
async def test_golden_regression_projects_chart_json_into_context():
    captured: dict[str, object] = {}

    mock_result = MagicMock(spec=GatewayResult)
    mock_result.structured_output = {
        "interpretation": "Lune en Cancer",
        "key_points": ["Sensibilité"],
    }
    mock_result.meta = MagicMock(spec=GatewayMeta)
    mock_result.meta.validation_status = "valid"
    mock_result.meta.execution_profile_source = "assembly"
    mock_result.meta.obs_snapshot = ExecutionObservabilitySnapshot(
        pipeline_kind="nominal_canonical",
        execution_path_kind=ExecutionPathKind.CANONICAL_ASSEMBLY,
        fallback_kind=None,
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        context_quality="nominal",
        context_compensation_status=ContextCompensationStatus.INJECTOR_APPLIED,
        max_output_tokens_source=MaxTokensSource.EXECUTION_PROFILE,
        max_output_tokens_final=1000,
    )
    mock_result.usage = UsageInfo(input_tokens=10, output_tokens=5)

    async def _fake_execute(request, **kwargs):
        captured["use_case"] = request.user_input.use_case
        captured["feature"] = request.user_input.feature
        captured["subfeature"] = request.user_input.subfeature
        captured["plan"] = request.user_input.plan
        captured["context"] = request.context
        return mock_result

    db = MagicMock()
    snapshot_id = _mock_release_context(db)

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        side_effect=_fake_execute,
    ):
        with patch(
            "app.domain.llm.configuration.active_release.get_active_release_id",
            new_callable=AsyncMock,
            return_value=snapshot_id,
        ):
            report = await GoldenRegressionService.run_campaign(
                use_case_key="natal",
                prompt_version_id="test-v1",
                golden_set_path="tests/fixtures/golden/natal_test.yaml",
                db=db,
            )

    assert report.verdict == "pass"
    assert captured["use_case"] == "natal"
    assert captured["feature"] == "natal"
    assert captured["subfeature"] == "interpretation"
    assert captured["plan"] == "free"
    assert captured["context"].chart_json == "{}"
