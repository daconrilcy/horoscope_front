import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models import LlmPersonaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import GatewayError


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


@pytest.mark.asyncio
async def test_persona_strategy_forbidden(db_session, monkeypatch):
    """AC 3: Forbidden strategy bypasses everything."""
    use_case = LlmUseCaseConfigModel(
        key="support", display_name="Support", description="D", persona_strategy="forbidden"
    )
    db_session.add(use_case)
    p = LlmPromptVersionModel(
        use_case_key="support",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="P {{locale}}",
        created_by="a",
    )
    db_session.add(p)
    db_session.commit()

    monkeypatch.setattr(
        "app.llm_orchestration.gateway.settings", MagicMock(llm_orchestration_v2=True)
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=MagicMock(meta=MagicMock()))

    gateway = LLMGateway(responses_client=mock_client)

    # Provide a persona_id, should be ignored
    result = await gateway.execute(
        "support",
        {},
        {"locale": "fr", "use_case": "support", "persona_id": "some_id"},
        "r",
        "t",
        db=db_session,
    )

    assert result.meta.persona_id is None
    # Verify Layer 3 is omitted
    messages = mock_client.execute.call_args.kwargs["messages"]
    assert len([m for m in messages if m["role"] == "developer"]) == 1  # Only developer prompt


@pytest.mark.asyncio
async def test_persona_override_rejected(db_session, monkeypatch):
    """AC 5: Persona override rejected fallback to default_safe."""
    persona_safe = LlmPersonaModel(id=uuid.uuid4(), name="Safe", enabled=True)
    db_session.add(persona_safe)
    db_session.flush()

    use_case = LlmUseCaseConfigModel(
        key="natal",
        display_name="N",
        description="D",
        persona_strategy="required",
        allowed_persona_ids=[str(persona_safe.id)],
    )
    db_session.add(use_case)
    p = LlmPromptVersionModel(
        use_case_key="natal",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="P {{locale}}",
        created_by="a",
    )
    db_session.add(p)
    db_session.commit()

    monkeypatch.setattr(
        "app.llm_orchestration.gateway.settings", MagicMock(llm_orchestration_v2=True)
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=MagicMock(meta=MagicMock()))

    gateway = LLMGateway(responses_client=mock_client)

    # Request unauthorized persona_id
    result = await gateway.execute(
        "natal",
        {},
        {"locale": "fr", "use_case": "natal", "persona_id": str(uuid.uuid4())},
        "r",
        "t",
        db=db_session,
    )

    # Should fallback to persona_safe
    assert result.meta.persona_id == str(persona_safe.id)


@pytest.mark.asyncio
async def test_persona_override_authorized(db_session, monkeypatch):
    """AC 5: Persona override authorized."""
    p1 = LlmPersonaModel(id=uuid.uuid4(), name="P1", enabled=True)
    p2 = LlmPersonaModel(id=uuid.uuid4(), name="P2", enabled=True)
    db_session.add_all([p1, p2])
    db_session.flush()

    use_case = LlmUseCaseConfigModel(
        key="natal",
        display_name="N",
        description="D",
        persona_strategy="required",
        allowed_persona_ids=[str(p1.id), str(p2.id)],
    )
    db_session.add(use_case)
    p = LlmPromptVersionModel(
        use_case_key="natal",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="P {{locale}}",
        created_by="a",
    )
    db_session.add(p)
    db_session.commit()

    monkeypatch.setattr(
        "app.llm_orchestration.gateway.settings", MagicMock(llm_orchestration_v2=True)
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=MagicMock(meta=MagicMock()))

    gateway = LLMGateway(responses_client=mock_client)

    # Request p2 specifically
    result = await gateway.execute(
        "natal",
        {},
        {"locale": "fr", "use_case": "natal", "persona_id": str(p2.id)},
        "r",
        "t",
        db=db_session,
    )

    assert result.meta.persona_id == str(p2.id)


def test_lint_usecase_placeholders():
    """AC 4: Lint verify use-case specific placeholders."""
    from app.llm_orchestration.services.prompt_lint import PromptLint

    required = ["{{chart_json}}"]

    # Missing chart_json
    text_fail = "Hello {{locale}} {{use_case}}"
    res_fail = PromptLint.lint_prompt(text_fail, use_case_required_placeholders=required)
    assert res_fail.passed is False
    assert "Use-case specific placeholder '{{chart_json}}' is missing." in res_fail.errors

    # Present
    text_pass = "Hello {{locale}} {{use_case}} {{chart_json}}"
    res_pass = PromptLint.lint_prompt(text_pass, use_case_required_placeholders=required)
    assert res_pass.passed is True


@pytest.mark.asyncio
async def test_input_validation_failure(db_session, monkeypatch):
    """AC 8: Input validation failure returns GatewayError (InputValidationError expected)."""
    schema = {
        "type": "object",
        "required": ["message"],
        "properties": {"message": {"type": "string", "minLength": 5}},
    }
    use_case = LlmUseCaseConfigModel(
        key="chat", display_name="C", description="D", input_schema=schema
    )
    db_session.add(use_case)
    p = LlmPromptVersionModel(
        use_case_key="chat",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="P {{locale}}",
        created_by="a",
    )
    db_session.add(p)
    db_session.commit()

    monkeypatch.setattr(
        "app.llm_orchestration.gateway.settings", MagicMock(llm_orchestration_v2=True)
    )

    gateway = LLMGateway()

    # Invalid input (too short)
    with pytest.raises(GatewayError) as exc:
        await gateway.execute(
            "chat", {"message": "hi"}, {"locale": "fr", "use_case": "chat"}, "r", "t", db=db_session
        )

    assert "Input validation failed" in str(exc.value)
