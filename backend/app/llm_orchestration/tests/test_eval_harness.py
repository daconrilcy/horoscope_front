from unittest.mock import AsyncMock, patch

import pytest
import yaml

from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo
from app.llm_orchestration.services.eval_harness import run_eval


@pytest.mark.asyncio
async def test_run_eval_empty_path(db):
    report = await run_eval("test", "v1", "/non/existent", db)
    assert report.total == 0
    assert report.passed == 0


@pytest.mark.asyncio
async def test_run_eval_success(db, tmp_path):
    # Setup fixture
    fixture = [
        {
            "id": "f1",
            "input": {"message": "hi"},
            "expected_schema_valid": True,
            "expected_fields": {"content": {"min_length": 5}},
        }
    ]
    f_path = tmp_path / "test.yaml"
    f_path.write_text(yaml.dump(fixture))

    # Mock Gateway
    mock_result = GatewayResult(
        use_case="test",
        request_id="r1",
        trace_id="t1",
        raw_output='{"content": "hello world"}',
        structured_output={"content": "hello world"},
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m", validation_status="valid"),
    )

    with patch(
        "app.llm_orchestration.services.eval_harness.LLMGateway.execute", new_callable=AsyncMock
    ) as mock_exec:
        mock_execute = AsyncMock(return_value=mock_result)
        mock_exec.side_effect = mock_execute

        report = await run_eval("test", "v1", str(f_path), db)

        assert report.total == 1
        assert report.passed == 1
        assert report.failure_rate == 0.0
        assert report.results[0].status == "passed"


@pytest.mark.asyncio
async def test_run_eval_failure(db, tmp_path):
    # Setup fixture
    fixture = [
        {"id": "f1", "input": {"message": "hi"}, "expected_fields": {"content": {"min_length": 50}}}
    ]
    f_path = tmp_path / "test.yaml"
    f_path.write_text(yaml.dump(fixture))

    # Mock Gateway (output too short)
    mock_result = GatewayResult(
        use_case="test",
        request_id="r1",
        trace_id="t1",
        raw_output='{"content": "short"}',
        structured_output={"content": "short"},
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m", validation_status="valid"),
    )

    with patch(
        "app.llm_orchestration.services.eval_harness.LLMGateway.execute", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = mock_result

        report = await run_eval("test", "v1", str(f_path), db)

        assert report.total == 1
        assert report.passed == 0
        assert report.failed == 1
        assert report.failure_rate == 1.0
        assert report.results[0].status == "failed"
        assert "Value too short" in report.results[0].field_mismatches[0]["error"]
