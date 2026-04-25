import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.llm.runtime.adapter import AIEngineAdapter, AIEngineAdapterError
from app.domain.llm.runtime.contracts import (
    GatewayMeta,
    GatewayResult,
    PromptRenderError,
    UsageInfo,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


@pytest.mark.asyncio
async def test_security_allowlist_blocks_internal_vars(db):
    """
    Checklist: Placeholders security.
    If a prompt in DB tries to use {{messages}}, it must be ignored/filtered
    by the allowlist, leading to a PromptRenderError if it was 'required'.
    """
    # 1. Create use case and prompt using internal variable
    uc = LlmUseCaseConfigModel(
        key="guidance_daily",
        display_name="Test",
        description="Test",
        required_prompt_placeholders=["messages"],
    )
    db.add(uc)
    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="guidance_daily",
        status=PromptStatus.PUBLISHED,
        developer_prompt="Hello {{messages}} {{locale}} {{use_case}}",
        created_by="admin",
    )
    db.add(prompt)
    db.commit()

    gateway = LLMGateway()

    # Act
    # Mock the client to return a real GatewayResult instead of AsyncMock
    mock_res = GatewayResult(
        use_case="leak_test",
        request_id="req1",
        trace_id="tr1",
        raw_output='{"message": "composed_output"}',
        structured_output={"message": "composed_output"},
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=1, model="gpt-4o-mini"),
    )
    gateway.client = AsyncMock()
    gateway.client.execute.return_value = mock_res

    # Should raise PromptRenderError because 'messages' is NOT in authorized_vars
    # but IS in required_prompt_placeholders
    with patch(
        "app.domain.llm.runtime.gateway.get_canonical_use_case_contract",
        return_value=None,
    ):
        with pytest.raises(PromptRenderError):
            await gateway.execute(
                use_case="guidance_daily",
                user_input={},
                context={
                    "messages": "SECRET_INTERNAL_DATA",
                    "locale": "fr",
                    "use_case": "guidance_daily",
                },
                request_id="req1",
                trace_id="tr1",
                db=db,
            )


@pytest.mark.asyncio
async def test_error_mapping_reaches_client_v2(db):
    """
    Checklist: Error mapping in AIEngineAdapter.
    A PromptRenderError from Gateway must result in AIEngineAdapterError (400)
    and NOT a ConnectionError.
    """
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
        new_callable=AsyncMock,
    ) as mock_execute:
        mock_execute.side_effect = PromptRenderError("boom", details={"field": "prompt"})

        with pytest.raises(AIEngineAdapterError) as exc_info:
            await AIEngineAdapter.generate_chat_reply(
                messages=[{"role": "user", "content": "hi"}],
                context={"locale": "fr"},
                user_id=1,
                request_id="r1",
                trace_id="t1",
                db=db,
            )

    assert exc_info.value.code == "prompt_render_error"
    assert exc_info.value.status_code == 400
