import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models import LlmPersonaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_persona import PersonaTone, PersonaVerbosity
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway


@pytest.fixture
def db_session():
    # Use an in-memory database for tests
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
async def test_persona_injection_success(db_session, monkeypatch):
    # Setup: Create a persona and a use case config in the DB
    persona = LlmPersonaModel(
        id=uuid.uuid4(),
        name="Luna",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        enabled=True,
    )
    db_session.add(persona)

    use_case_config = LlmUseCaseConfigModel(
        key="test_use_case",
        display_name="Test",
        description="Test",
        allowed_persona_ids=[str(persona.id)],
    )
    db_session.add(use_case_config)

    prompt_version = LlmPromptVersionModel(
        use_case_key="test_use_case",
        status=PromptStatus.PUBLISHED,
        developer_prompt="Hello {{name}} {{locale}}",
        model="gpt-4o-mini",
        created_by="admin",
    )
    db_session.add(prompt_version)
    db_session.commit()

    # Mock ResponsesClient
    mock_client = MagicMock()
    # Mock return value of execute
    mock_result = MagicMock()
    mock_result.meta = MagicMock()
    mock_result.usage = MagicMock()
    mock_client.execute = AsyncMock(return_value=mock_result)

    gateway = LLMGateway(responses_client=mock_client)

    result = await gateway.execute(
        use_case="test_use_case",
        user_input={"name": "Cyril"},
        context={"locale": "fr", "use_case": "test_use_case"},
        request_id="req-1",
        trace_id="trace-1",
        db=db_session,
    )

    # Verify persona injection in messages
    call_args = mock_client.execute.call_args[1]
    messages = call_args["messages"]

    # Layer 3 (index 2) should be the persona block
    assert len(messages) >= 3
    assert messages[2]["role"] == "developer"
    assert "## Directives de persona : Luna" in messages[2]["content"]

    # Verify persona_id in meta
    assert result.meta.persona_id == str(persona.id)


@pytest.mark.asyncio
async def test_persona_injection_disabled(db_session, monkeypatch):
    # Setup: Create a DISABLED persona
    persona = LlmPersonaModel(
        id=uuid.uuid4(),
        name="Luna",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        enabled=False,  # DISABLED
    )
    db_session.add(persona)

    use_case_config = LlmUseCaseConfigModel(
        key="test_use_case_disabled",
        display_name="Test",
        description="Test",
        allowed_persona_ids=[str(persona.id)],
        persona_strategy="optional",
    )
    db_session.add(use_case_config)

    prompt_version = LlmPromptVersionModel(
        use_case_key="test_use_case_disabled",
        status=PromptStatus.PUBLISHED,
        developer_prompt="Hello {{locale}}",
        model="gpt-4o-mini",
        created_by="admin",
    )
    db_session.add(prompt_version)
    db_session.commit()

    # Mock ResponsesClient
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.meta = MagicMock()
    mock_result.usage = MagicMock()
    mock_client.execute = AsyncMock(return_value=mock_result)

    gateway = LLMGateway(responses_client=mock_client)

    result = await gateway.execute(
        use_case="test_use_case_disabled",
        user_input={},
        context={"locale": "en", "use_case": "test_use_case_disabled"},
        request_id="req-2",
        trace_id="trace-2",
        db=db_session,
    )

    # Verify persona injection is OMITTED
    call_args = mock_client.execute.call_args[1]
    messages = call_args["messages"]

    # Layer 3 should be OMITTED or not contain persona
    # messages should have: system, developer (prompt), user (data) -> total 3
    assert len(messages) == 3
    # Check roles
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "developer"
    assert messages[2]["role"] == "user"

    # Verify persona_id in meta is None
    assert result.meta.persona_id is None


@pytest.mark.asyncio
async def test_persona_required_but_missing(db_session, monkeypatch):
    # Setup: Use case with strategy REQUIRED but no enabled persona
    from app.llm_orchestration.models import GatewayConfigError

    use_case_config = LlmUseCaseConfigModel(
        key="req_use_case",
        display_name="Required",
        description="Test",
        persona_strategy="required",  # REQUIRED
        allowed_persona_ids=[],  # Empty list
    )
    db_session.add(use_case_config)

    prompt_version = LlmPromptVersionModel(
        use_case_key="req_use_case",
        status=PromptStatus.PUBLISHED,
        developer_prompt="Hello {{locale}}",
        model="gpt-4o-mini",
        created_by="admin",
    )
    db_session.add(prompt_version)
    db_session.commit()

    gateway = LLMGateway()

    with pytest.raises(GatewayConfigError) as exc_info:
        await gateway.execute(
            use_case="req_use_case",
            user_input={},
            context={"locale": "fr", "use_case": "req_use_case"},
            request_id="req-3",
            trace_id="trace-3",
            db=db_session,
        )

    assert "No active persona available for required use case 'req_use_case'" in str(exc_info.value)
