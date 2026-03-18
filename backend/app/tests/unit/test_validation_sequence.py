from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway


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
        Base.metadata.drop_all(bind=test_engine)


@pytest.mark.asyncio
async def test_gateway_repair_sequence(db_session, monkeypatch):
    # 1. Setup DB
    schema_dict = {
        "type": "object",
        "required": ["message"],
        "properties": {"message": {"type": "string"}},
    }
    output_schema = LlmOutputSchemaModel(name="test_schema", json_schema=schema_dict)
    db_session.add(output_schema)
    db_session.flush()

    use_case = LlmUseCaseConfigModel(
        key="test_repair",
        display_name="Test",
        description="Test",
        output_schema_id=str(output_schema.id),
    )
    db_session.add(use_case)

    prompt = LlmPromptVersionModel(
        use_case_key="test_repair",
        status=PromptStatus.PUBLISHED,
        developer_prompt="Hello {{locale}}",
        model="gpt-4o-mini",
        created_by="admin",
    )
    db_session.add(prompt)
    db_session.commit()

    # 3. Mock ResponsesClient to fail once then succeed
    mock_client = MagicMock()

    # First response: invalid JSON
    res1 = MagicMock()
    res1.raw_output = "INVALID JSON"
    res1.usage = MagicMock()
    res1.meta = MagicMock()
    res1.meta.latency_ms = 100

    # Second response: valid JSON (repair success)
    res2 = MagicMock()
    res2.raw_output = '{"message": "fixed"}'
    res2.usage = MagicMock()
    res2.meta = MagicMock()
    res2.meta.latency_ms = 100

    mock_client.execute = AsyncMock(side_effect=[res1, res2])

    gateway = LLMGateway(responses_client=mock_client)

    # 4. Execute
    result = await gateway.execute(
        use_case="test_repair",
        user_input={},
        context={"locale": "fr", "use_case": "test_repair"},
        request_id="req-repair",
        trace_id="trace-repair",
        db=db_session,
    )

    # 5. Verify
    assert result.structured_output["message"] == "fixed"
    assert result.meta.repair_attempted is True
    assert mock_client.execute.call_count == 2


@pytest.mark.asyncio
async def test_gateway_fallback_sequence(db_session, monkeypatch):
    # 1. Setup DB
    schema_dict = {"type": "object", "required": ["msg"]}
    output_schema = LlmOutputSchemaModel(name="test_schema", json_schema=schema_dict)
    db_session.add(output_schema)
    db_session.flush()

    # Primary use case with fallback
    use_case = LlmUseCaseConfigModel(
        key="primary",
        display_name="Primary",
        description="Test",
        output_schema_id=str(output_schema.id),
        fallback_use_case_key="fallback_uc",
    )
    # Fallback use case (no schema)
    fallback_uc = LlmUseCaseConfigModel(
        key="fallback_uc", display_name="Fallback", description="Test"
    )
    db_session.add_all([use_case, fallback_uc])

    p1 = LlmPromptVersionModel(
        use_case_key="primary",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="P {{locale}}",
        created_by="a",
    )
    p2 = LlmPromptVersionModel(
        use_case_key="fallback_uc",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="F {{locale}}",
        created_by="a",
    )
    db_session.add_all([p1, p2])
    db_session.commit()

    # 3. Mock ResponsesClient to always fail primary, then succeed fallback
    mock_client = MagicMock()

    # Responses for primary (call + repair)
    res_fail = MagicMock()
    res_fail.raw_output = "FAIL"
    res_fail.usage = MagicMock()
    res_fail.meta = MagicMock()

    # Response for fallback
    res_fallback = MagicMock()
    res_fallback.raw_output = "Fallback Success"
    res_fallback.usage = MagicMock()
    res_fallback.meta = MagicMock()

    mock_client.execute = AsyncMock(side_effect=[res_fail, res_fail, res_fallback])

    gateway = LLMGateway(responses_client=mock_client)

    # 4. Execute
    result = await gateway.execute(
        use_case="primary",
        user_input={},
        context={"locale": "fr", "use_case": "primary"},
        request_id="req-fallback",
        trace_id="trace-fallback",
        db=db_session,
    )

    # 5. Verify
    assert result.raw_output == "Fallback Success"
    assert result.meta.fallback_triggered is True
    assert mock_client.execute.call_count == 3
