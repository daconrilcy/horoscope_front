import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.infra.db.models import LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import GatewayMeta, GatewayResult, PromptRenderError, UsageInfo
from app.services.ai_engine_adapter import AIEngineAdapter, AIEngineAdapterError


@pytest.mark.asyncio
async def test_security_allowlist_blocks_internal_vars(db):
    """
    Checklist: Placeholders security.
    If a prompt in DB tries to use {{messages}}, it must be ignored/filtered
    by the allowlist, leading to a PromptRenderError if it was 'required'.
    """
    # 1. Create use case and prompt using internal variable
    uc = LlmUseCaseConfigModel(
        key="leak_test",
        display_name="Test",
        description="Test",
        required_prompt_placeholders=["messages"],
    )
    db.add(uc)
    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="leak_test",
        status=PromptStatus.PUBLISHED,
        developer_prompt="Hello {{messages}} {{locale}} {{use_case}}",
        model="gpt-4o-mini",
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
    with pytest.raises(PromptRenderError):
        await gateway.execute(
            use_case="leak_test",
            user_input={},
            context={"messages": "SECRET_INTERNAL_DATA", "locale": "fr", "use_case": "leak_test"},
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
    # 1. Setup prompt with a REQUIRED authorized variable
    uc = LlmUseCaseConfigModel(
        key="chat_astrologer",
        display_name="Test Chat",
        description="Test",
        required_prompt_placeholders=["natal_chart_summary"],
    )
    db.add(uc)
    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="chat_astrologer",
        status=PromptStatus.PUBLISHED,
        developer_prompt="Hello {{natal_chart_summary}} {{locale}} {{use_case}}",
        model="gpt-4o-mini",
        created_by="admin",
    )
    db.add(prompt)
    db.commit()

    # 1.5 Seed dummy assembly to satisfy Story 66.20 enforcement
    from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel

    asm = PromptAssemblyConfigModel(
        feature="chat",
        subfeature="astrologer",
        plan="free",
        locale="fr-FR",
        feature_template_ref=prompt.id,
        execution_config={"model": "gpt-4o-mini"},
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(asm)
    db.commit()

    try:
        # Disable test fallback for this specific call
        with patch("app.services.ai_engine_adapter._is_non_production_env", return_value=False):
            await AIEngineAdapter.generate_chat_reply(
                messages=[{"role": "user", "content": "hi"}],
                context={"locale": "fr"},  # Missing natal_chart_summary
                user_id=1,
                request_id="r1",
                trace_id="t1",
                db=db,
            )
        pytest.fail("Should have raised AIEngineAdapterError")

    except AIEngineAdapterError as err:
        # Assert
        assert err.code == "prompt_render_error"
        assert err.status_code == 400  # Story 66.3 changed it to 400
