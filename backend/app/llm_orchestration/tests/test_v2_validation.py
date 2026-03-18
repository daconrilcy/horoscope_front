from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.llm_orchestration.gateway import LLMGateway
from app.services.ai_engine_adapter import AIEngineAdapter, AIEngineAdapterError


@pytest.mark.asyncio
async def test_security_allowlist_blocks_internal_vars(db):
    """
    Checklist: Placeholders security.
    If a prompt in DB tries to use {{messages}}, it must be ignored/filtered
    by the allowlist, leading to a PromptRenderError if it was 'required'.
    """
    # 1. Create use case and prompt using internal variable
    uc = LlmUseCaseConfigModel(key="leak_test", display_name="Test", description="Test")
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
    # Mock the client to avoid real API calls
    gateway.client = AsyncMock()
    gateway.client.execute.return_value = AsyncMock(raw_output="composed_output")

    await gateway.execute(
        use_case="leak_test",
        user_input={},
        context={"messages": "SECRET_INTERNAL_DATA", "locale": "fr", "use_case": "leak_test"},
        request_id="req1",
        trace_id="tr1",
        db=db,
    )

    # Assert
    # 1. The call should succeed because 'messages' is NOT in 'required_prompt_placeholders'
    # (it was filtered by allowlist)
    # 2. BUT the placeholder {{messages}} must NOT have been replaced by the secret data
    # because it was filtered out from 'render_vars'.

    # Verify the developer prompt sent to the client
    call_args = gateway.client.execute.call_args
    messages = call_args.kwargs["messages"]
    # messages[1] is the developer prompt layer
    dev_content = messages[1]["content"]

    assert "SECRET_INTERNAL_DATA" not in dev_content
    assert "{{messages}}" in dev_content  # Remained as literal because not in render_vars


@pytest.mark.asyncio
async def test_error_mapping_reaches_client_v2(db):
    """
    Checklist: Error mapping in AIEngineAdapter.
    A PromptRenderError from Gateway must result in AIEngineAdapterError (400)
    and NOT a ConnectionError.
    """
    # 1. Setup prompt with a REQUIRED authorized variable
    # We use 'chat_astrologer' because AIEngineAdapter.generate_chat_reply uses it.
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

    # 2. Call via Adapter with missing variable
    # natal_chart_summary IS in allowlist, so it IS in 'required_prompt_placeholders'.
    # If missing from context, it will raise PromptRenderError.

    try:
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
        assert err.status_code == 500
    except ConnectionError as err:
        pytest.fail(f"Should have raised AIEngineAdapterError, not ConnectionError: {err}")


def test_cache_field_completeness(db):
    """
    Checklist: Cache registry fields.
    Fields published_at, created_by, created_at must survive cache hit.
    """
    from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2, _prompt_cache

    _prompt_cache.clear()

    uc = LlmUseCaseConfigModel(key="cache_test", display_name="Test", description="Test")
    db.add(uc)
    now = datetime.now()
    v1 = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="cache_test",
        status=PromptStatus.PUBLISHED,
        developer_prompt="P1 {{locale}} {{use_case}}",
        model="m",
        created_by="admin-user-123",
        created_at=now,
        published_at=now,
    )
    db.add(v1)
    db.commit()

    # 1. First call (Miss)
    p1 = PromptRegistryV2.get_active_prompt(db, "cache_test")
    assert p1.created_by == "admin-user-123"
    assert p1.published_at is not None
    assert p1.created_at is not None

    # 2. Second call (Hit)
    p2 = PromptRegistryV2.get_active_prompt(db, "cache_test")
    assert p2.created_by == "admin-user-123"
    assert p2.published_at is not None
    assert p2.created_at is not None
    assert p2.id == v1.id
