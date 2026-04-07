import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    LLMExecutionRequest,
    ExecutionUserInput,
    ExecutionContext,
    GatewayResult,
    GatewayMeta,
    UsageInfo,
    UseCaseConfig
)
from app.llm_orchestration.services.output_validator import validate_output

@pytest.mark.asyncio
async def test_validate_output_with_highlights_list():
    """Reproduce and fix NameError when highlights/advice are lists."""
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "highlights": {"type": "array", "items": {"type": "string"}},
            "evidence": {"type": "array", "items": {"type": "string"}}
        }
    }
    raw_output = '{"summary": "Test", "highlights": ["Point 1"], "evidence": ["SUN_LEO"]}'
    
    # Should NOT raise NameError: name 'v' is not defined
    result = validate_output(raw_output, schema, evidence_catalog=["SUN_LEO"])
    assert result.valid is True
    assert result.parsed["highlights"] == ["Point 1"]

@pytest.mark.asyncio
async def test_prompt_version_id_propagation():
    """Verify that prompt_version_id from config is preserved in final GatewayResult."""
    mock_client = MagicMock()
    real_prompt_id = str(uuid.uuid4())
    
    # Mock result from provider (which might have a default meta)
    provider_res = GatewayResult(
        use_case="test",
        request_id="r",
        trace_id="t",
        raw_output="{}",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m", prompt_version_id="hardcoded-v1")
    )
    mock_client.execute = AsyncMock(return_value=provider_res)
    
    gateway = LLMGateway(responses_client=mock_client)
    
    # Use config override to set a real prompt_version_id
    config = UseCaseConfig(
        model="m",
        developer_prompt="hello",
        prompt_version_id=real_prompt_id
    )
    
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test", locale="fr"),
        request_id="r",
        trace_id="t",
        user_id=1
    )
    
    # Mocking _resolve_config to return our config
    gateway._resolve_config = AsyncMock(return_value=config)
    
    result = await gateway.execute_request(request)
    
    # Critical: final result must carry the resolved prompt_version_id, not the provider default
    assert result.meta.prompt_version_id == real_prompt_id
