import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    UsageInfo,
    UseCaseConfig,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.domain.llm.runtime.output_validator import validate_output


@pytest.mark.asyncio
async def test_validate_output_with_highlights_list():
    """Reproduce and fix NameError when highlights/advice are lists."""
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "highlights": {"type": "array", "items": {"type": "string"}},
            "evidence": {"type": "array", "items": {"type": "string"}},
        },
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
        meta=GatewayMeta(latency_ms=10, model="m", prompt_version_id="hardcoded-v1"),
    )
    mock_client.execute = AsyncMock(return_value=(provider_res, {}))

    gateway = LLMGateway(responses_client=mock_client)

    # Use config override to set a real prompt_version_id
    config = UseCaseConfig(model="m", developer_prompt="hello", prompt_version_id=real_prompt_id)

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test", locale="fr"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )

    # Mock the bounded legacy compatibility resolver.
    gateway._resolve_fallback_use_case_config = AsyncMock(return_value=config)

    result = await gateway.execute_request(request)

    # Critical: final result must carry the resolved prompt_version_id, not the provider default
    assert result.meta.prompt_version_id == real_prompt_id


@pytest.mark.asyncio
async def test_observability_success_persists_to_db():
    """Verify that a successful execute_request creates an LlmCallLogModel entry."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.infra.db.base import Base
    from app.infra.db.models.llm.llm_observability import LlmCallLogModel
    from app.infra.db.models.llm.llm_prompt import (
        LlmPromptVersionModel,
        LlmUseCaseConfigModel,
        PromptStatus,
    )

    # 1. Setup in-memory DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 2. Setup use case and prompt
        use_case_key = "test_obs"
        uc = LlmUseCaseConfigModel(key=use_case_key, display_name="Test", description="D")
        db.add(uc)
        prompt = LlmPromptVersionModel(
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            model="m",
            developer_prompt="hello",
            created_by="test",
        )
        db.add(prompt)
        db.commit()

        # 3. Mock provider
        mock_client = MagicMock()
        provider_res = GatewayResult(
            use_case=use_case_key,
            request_id="req-obs",
            trace_id="trace-obs",
            raw_output='{"ok": true}',
            usage=UsageInfo(input_tokens=10, output_tokens=20),
            meta=GatewayMeta(latency_ms=15, model="m"),
        )
        mock_client.execute = AsyncMock(return_value=(provider_res, {}))

        gateway = LLMGateway(responses_client=mock_client)

        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(use_case=use_case_key, locale="fr"),
            request_id="req-obs",
            trace_id="trace-obs",
            user_id=1,
        )

        # 4. Execute
        await gateway.execute_request(request, db=db)

        # 5. Verify DB persistence
        stmt = select(LlmCallLogModel).where(LlmCallLogModel.request_id == "req-obs")
        log_entry = db.execute(stmt).scalar_one_or_none()

        assert log_entry is not None
        assert log_entry.use_case == use_case_key
        assert log_entry.tokens_in == 10
        assert log_entry.tokens_out == 20
        # Check that it's NOT hardcoded-v1 if prompt was found
        assert str(log_entry.prompt_version_id) == str(prompt.id)

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.mark.asyncio
async def test_observability_success_ignores_missing_fk_references():
    """A valid-but-missing FK UUID must not break success logging."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.infra.db.base import Base
    from app.infra.db.models.llm.llm_observability import LlmCallLogModel

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        missing_prompt_id = str(uuid.uuid4())
        mock_client = MagicMock()
        provider_res = GatewayResult(
            use_case="test_missing_fk",
            request_id="req-missing-fk",
            trace_id="trace-missing-fk",
            raw_output="plain text response",
            usage=UsageInfo(input_tokens=3, output_tokens=5),
            meta=GatewayMeta(latency_ms=12, model="m", prompt_version_id="hardcoded-v1"),
        )
        mock_client.execute = AsyncMock(return_value=(provider_res, {}))

        gateway = LLMGateway(responses_client=mock_client)
        gateway._resolve_fallback_use_case_config = AsyncMock(
            return_value=UseCaseConfig(
                model="m",
                developer_prompt="hello",
                prompt_version_id=missing_prompt_id,
                interaction_mode="structured",
                user_question_policy="none",
            )
        )

        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(use_case="test_missing_fk", locale="fr"),
            context=ExecutionContext(),
            request_id="req-missing-fk",
            trace_id="trace-missing-fk",
            user_id=1,
        )

        result = await gateway.execute_request(request, db=db)

        stmt = select(LlmCallLogModel).where(LlmCallLogModel.request_id == "req-missing-fk")
        log_entry = db.execute(stmt).scalar_one_or_none()

        assert result.meta.prompt_version_id == missing_prompt_id
        assert log_entry is not None
        assert log_entry.prompt_version_id is None
        assert log_entry.tokens_in == 3
        assert log_entry.tokens_out == 5
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
