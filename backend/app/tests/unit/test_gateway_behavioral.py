from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    GatewayConfigError,
    GatewayError,
    GatewayMeta,
    GatewayResult,
    UsageInfo,
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


@pytest.mark.asyncio
async def test_check_1_fallback_priority(db_session, monkeypatch):
    """Point 1: Priorité fallback UseCaseConfig > PromptVersion."""
    schema = LlmOutputSchemaModel(name="s", json_schema={"type": "object", "required": ["ok"]})
    db_session.add(schema)
    db_session.flush()

    use_case = LlmUseCaseConfigModel(
        key="primary",
        display_name="P",
        description="D",
        fallback_use_case_key="fallback_A",  # Priority 1
        output_schema_id=str(schema.id),
    )
    fallback_A = LlmUseCaseConfigModel(key="fallback_A", display_name="A", description="D")
    db_session.add_all([use_case, fallback_A])

    p1 = LlmPromptVersionModel(
        use_case_key="primary",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="P {{locale}}",
        created_by="a",
        fallback_use_case_key="fallback_B",  # Priority 2
    )
    p_A = LlmPromptVersionModel(
        use_case_key="fallback_A",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="A {{locale}}",
        created_by="a",
    )
    db_session.add_all([p1, p_A])
    db_session.commit()

    monkeypatch.setattr(
        "app.llm_orchestration.gateway.settings", MagicMock(llm_orchestration_v2=True)
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        side_effect=[
            create_mock_result("primary", "FAIL"),  # initial
            create_mock_result("primary", "FAIL"),  # repair
            create_mock_result("fallback_A", "SUCCESS"),  # fallback
        ]
    )

    gateway = LLMGateway(responses_client=mock_client)
    result = await gateway.execute(
        "primary", {}, {"locale": "fr", "use_case": "primary"}, "r", "t", db=db_session
    )

    assert result.use_case == "fallback_A"
    assert result.meta.validation_status == "fallback"


@pytest.mark.asyncio
async def test_check_3_repair_call_stable_prompt(db_session, monkeypatch):
    """Point 3: Repair call utilise un developer_prompt technique minimal."""
    schema = LlmOutputSchemaModel(name="s", json_schema={"type": "object", "required": ["ok"]})
    db_session.add(schema)
    db_session.flush()

    uc = LlmUseCaseConfigModel(
        key="test", display_name="T", description="D", output_schema_id=str(schema.id)
    )
    p = LlmPromptVersionModel(
        use_case_key="test",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="ORIGINAL {{locale}}",
        created_by="a",
    )
    db_session.add_all([uc, p])
    db_session.commit()

    monkeypatch.setattr(
        "app.llm_orchestration.gateway.settings", MagicMock(llm_orchestration_v2=True)
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        side_effect=[
            create_mock_result("test", "INVALID"),
            create_mock_result("test", '{"ok": true}'),
        ]
    )

    gateway = LLMGateway(responses_client=mock_client)
    await gateway.execute("test", {}, {"locale": "fr", "use_case": "test"}, "r", "t", db=db_session)

    # Verify 2nd call messages
    repair_call_args = mock_client.execute.call_args_list[1]
    messages = repair_call_args.kwargs["messages"]
    dev_msg = next(m for m in messages if m["role"] == "developer")
    assert "assistant technique" in dev_msg["content"]
    assert "ORIGINAL" not in dev_msg["content"]


@pytest.mark.asyncio
async def test_check_4_repair_limit_and_anti_loop(db_session, monkeypatch):
    """Point 4 & B: Une seule tentative de repair + protection anti-boucle fallback."""
    schema = LlmOutputSchemaModel(name="s", json_schema={"type": "object", "required": ["ok"]})
    db_session.add(schema)
    db_session.flush()

    # Loop A -> B -> A
    uc_a = LlmUseCaseConfigModel(
        key="A",
        display_name="A",
        description="D",
        output_schema_id=str(schema.id),
        fallback_use_case_key="B",
    )
    uc_b = LlmUseCaseConfigModel(
        key="B",
        display_name="B",
        description="D",
        output_schema_id=str(schema.id),
        fallback_use_case_key="A",
    )
    p_a = LlmPromptVersionModel(
        use_case_key="A",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="A {{locale}}",
        created_by="a",
    )
    p_b = LlmPromptVersionModel(
        use_case_key="B",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="B {{locale}}",
        created_by="a",
    )
    db_session.add_all([uc_a, uc_b, p_a, p_b])
    db_session.commit()

    monkeypatch.setattr(
        "app.llm_orchestration.gateway.settings", MagicMock(llm_orchestration_v2=True)
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        side_effect=[
            create_mock_result("A", "INVALID"),  # A init
            create_mock_result("A", "INVALID"),  # A repair
            create_mock_result("B", "INVALID"),  # B init
            create_mock_result("B", "INVALID"),  # B repair
            create_mock_result("A", "INVALID"),  # A fallback (should be blocked)
        ]
    )

    gateway = LLMGateway(responses_client=mock_client)

    with pytest.raises(GatewayError) as exc:
        await gateway.execute("A", {}, {"locale": "fr", "use_case": "A"}, "r", "t", db=db_session)

    assert "Infinite fallback loop detected" in str(exc.value)
    # Total calls: A(init), A(repair), B(init), B(repair)
    assert mock_client.execute.call_count == 4


@pytest.mark.asyncio
async def test_check_2_fail_fast_missing_vars(db_session, monkeypatch):
    """Point 2: Validation runtime locale et use_case."""
    monkeypatch.setattr(
        "app.llm_orchestration.gateway.settings", MagicMock(llm_orchestration_v2=True)
    )
    gateway = LLMGateway()

    with pytest.raises(GatewayConfigError) as exc:
        await gateway.execute("chat", {}, {}, "r", "t", db=db_session)
    assert "Missing mandatory platform variable: 'locale'" in str(exc.value)

    with pytest.raises(GatewayConfigError) as exc:
        await gateway.execute("chat", {}, {"locale": "fr"}, "r", "t", db=db_session)
    assert "Missing mandatory platform variable: 'use_case'" in str(exc.value)
