"""Valide des comportements runtime du gateway sans dependre du registre LLM global."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.domain.llm.runtime.gateway as gateway_module
from app.domain.llm.runtime.contracts import (
    ExecutionUserInput,
    GatewayError,
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    UsageInfo,
    UseCaseConfig,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


@pytest.fixture
def db_session():
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_mock_result(use_case, raw_output):
    return GatewayResult(
        use_case=use_case,
        request_id="req",
        trace_id="trace",
        raw_output=raw_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="gpt-4o-mini"),
    )


def _install_fallback_registry(
    monkeypatch: pytest.MonkeyPatch, configs: dict[str, UseCaseConfig]
) -> None:
    """Injecte un registre fallback borne aux use cases du test."""
    monkeypatch.setattr(
        gateway_module,
        "build_fallback_use_case_config",
        lambda use_case: configs.get(use_case),
    )


@pytest.mark.asyncio
async def test_check_1_fallback_priority(
    db_session, monkeypatch: pytest.MonkeyPatch
):
    """Point 1: Le fallback nominal vient du contrat canonique / use-case config."""
    schema = LlmOutputSchemaModel(name="s", json_schema={"type": "object", "required": ["ok"]})
    db_session.add(schema)
    db_session.flush()

    use_case = LlmUseCaseConfigModel(
        key="primary",
        display_name="P",
        description="D",
    )
    fallback_A = LlmUseCaseConfigModel(key="fallback_A", display_name="A", description="D")
    db_session.add_all([use_case, fallback_A])

    p1 = LlmPromptVersionModel(
        use_case_key="primary",
        status=PromptStatus.PUBLISHED,
        developer_prompt="P {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    p_A = LlmPromptVersionModel(
        use_case_key="fallback_A",
        status=PromptStatus.PUBLISHED,
        developer_prompt="A {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    db_session.add_all([p1, p_A])
    db_session.commit()

    _install_fallback_registry(
        monkeypatch,
        {
            "primary": UseCaseConfig(
                model="gpt-4o-mini",
                developer_prompt="registry-primary",
                prompt_version_id="registry-primary",
                output_schema_id=str(schema.id),
                fallback_target_use_case="fallback_A",
            ),
            "fallback_A": UseCaseConfig(
                model="gpt-4o-mini",
                developer_prompt="registry-fallback",
                prompt_version_id="registry-fallback",
                output_schema_id=str(schema.id),
            ),
        },
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        side_effect=[
            create_mock_result("primary", "FAIL"),  # initial
            create_mock_result("primary", "FAIL"),  # repair
            create_mock_result("fallback_A", '{"ok": true}'),  # fallback
        ]
    )

    gateway = LLMGateway(responses_client=mock_client)
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="primary", locale="fr", question="Hello"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    result = await gateway.execute_request(
        request=request,
        db=db_session,
    )

    assert result.use_case == "fallback_A"
    assert result.meta.validation_status == "fallback"


@pytest.mark.asyncio
async def test_check_3_repair_call_stable_prompt(
    db_session, monkeypatch: pytest.MonkeyPatch
):
    """Point 3: Repair call utilise un developer_prompt technique minimal."""
    schema = LlmOutputSchemaModel(name="s", json_schema={"type": "object", "required": ["ok"]})
    db_session.add(schema)
    db_session.flush()

    uc = LlmUseCaseConfigModel(key="test", display_name="T", description="D")
    p = LlmPromptVersionModel(
        use_case_key="test",
        status=PromptStatus.PUBLISHED,
        developer_prompt="ORIGINAL {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    db_session.add_all([uc, p])
    db_session.commit()

    _install_fallback_registry(
        monkeypatch,
        {
            "test": UseCaseConfig(
                model="gpt-4o-mini",
                developer_prompt="registry-test",
                prompt_version_id="registry-test",
                output_schema_id=str(schema.id),
            )
        },
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        side_effect=[
            create_mock_result("test", "INVALID"),
            create_mock_result("test", '{"ok": true}'),
        ]
    )

    gateway = LLMGateway(responses_client=mock_client)
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test", locale="fr", question="Hello"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    await gateway.execute_request(
        request=request,
        db=db_session,
    )

    # Verify 2nd call messages
    repair_call_args = mock_client.execute.call_args_list[1]
    messages = repair_call_args.kwargs["messages"]
    dev_msg = next(m for m in messages if m["role"] == "developer")
    assert "assistant technique" in dev_msg["content"]
    assert "ORIGINAL" not in dev_msg["content"]


@pytest.mark.asyncio
async def test_check_4_repair_limit_and_anti_loop(
    db_session, monkeypatch: pytest.MonkeyPatch
):
    """Point 4 & B: Une seule tentative de repair + protection anti-boucle fallback."""
    schema = LlmOutputSchemaModel(name="s", json_schema={"type": "object", "required": ["ok"]})
    db_session.add(schema)
    db_session.flush()

    # Loop A -> B -> A
    uc_a = LlmUseCaseConfigModel(
        key="A",
        display_name="A",
        description="D",
    )
    uc_b = LlmUseCaseConfigModel(
        key="B",
        display_name="B",
        description="D",
    )
    p_a = LlmPromptVersionModel(
        use_case_key="A",
        status=PromptStatus.PUBLISHED,
        developer_prompt="A {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    p_b = LlmPromptVersionModel(
        use_case_key="B",
        status=PromptStatus.PUBLISHED,
        developer_prompt="B {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    db_session.add_all([uc_a, uc_b, p_a, p_b])
    db_session.commit()

    _install_fallback_registry(
        monkeypatch,
        {
            "A": UseCaseConfig(
                model="gpt-4o-mini",
                developer_prompt="registry-A",
                prompt_version_id="registry-A",
                output_schema_id=str(schema.id),
                fallback_target_use_case="B",
            ),
            "B": UseCaseConfig(
                model="gpt-4o-mini",
                developer_prompt="registry-B",
                prompt_version_id="registry-B",
                output_schema_id=str(schema.id),
                fallback_target_use_case="A",
            ),
        },
    )

    mock_client = MagicMock()

    # Use a lambda to avoid StopAsyncIteration
    # Use a lambda to avoid StopAsyncIteration
    async def mock_execute(**kwargs):
        return create_mock_result(kwargs.get("use_case", "unknown"), "INVALID")

    mock_client.execute.side_effect = mock_execute

    gateway = LLMGateway(responses_client=mock_client)
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="A", locale="fr", question="Hello"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )

    with pytest.raises(GatewayError) as exc:
        await gateway.execute_request(
            request=request,
            db=db_session,
        )

    assert "Infinite fallback loop detected" in str(exc.value)


@pytest.mark.asyncio
async def test_check_2_fail_fast_missing_vars(db_session):
    """Point 2: Validation runtime locale et use_case."""
    # This test is less relevant now as Pydantic validates the request object
    # but we can still check for UnknownUseCase if it's not in catalog and no DB.
    gateway = LLMGateway()

    # Missing locale/use_case in ExecutionUserInput will be caught by Pydantic if we use models
    # But let's check UnknownUseCaseError
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="unknown", locale="fr"), request_id="r", trace_id="t"
    )
    with pytest.raises(GatewayError) as exc:
        await gateway.execute_request(request=request, db=db_session)
    assert "Use case 'unknown' not found" in str(exc.value)
