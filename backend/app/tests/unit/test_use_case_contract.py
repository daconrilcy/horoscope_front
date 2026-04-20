import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models import LlmPersonaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionUserInput,
    GatewayError,
    GatewayMeta,
    GatewayResult,
    InputValidationError,
    LLMExecutionRequest,
    UsageInfo,
    UseCaseConfig,
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


def _make_mock_result(use_case, persona_id=None):
    return GatewayResult(
        use_case=use_case,
        request_id="req",
        trace_id="trace",
        raw_output="ok",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m", persona_id=persona_id),
    )


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
        developer_prompt="P {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    db_session.add(p)
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("support"))

    gateway = LLMGateway(responses_client=mock_client)

    # Provide a persona_id, should be ignored
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="support", locale="fr", question="help", persona_id_override="some_id"
        ),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    result = await gateway.execute_request(
        request=request,
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
        developer_prompt="P {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    db_session.add(p)
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=_make_mock_result("natal", persona_id=str(persona_safe.id))
    )

    gateway = LLMGateway(responses_client=mock_client)

    # Request unauthorized persona_id
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal", locale="fr", question="me", persona_id_override=str(uuid.uuid4())
        ),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    result = await gateway.execute_request(
        request=request,
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
        developer_prompt="P {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    db_session.add(p)
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("natal", persona_id=str(p2.id)))

    gateway = LLMGateway(responses_client=mock_client)

    # Request p2 specifically
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal", locale="fr", question="me", persona_id_override=str(p2.id)
        ),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    result = await gateway.execute_request(
        request=request,
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
    # Create use_case correctly in DB
    use_case_config = LlmUseCaseConfigModel(
        key="chat",
        display_name="C",
        description="D",
        input_schema=schema,
        interaction_mode="chat",
        user_question_policy="optional",
    )
    db_session.add(use_case_config)
    db_session.flush()  # Ensure it has an id if needed

    p = LlmPromptVersionModel(
        use_case_key="chat",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="P {{locale}} {{last_user_msg}}",
        created_by="a",
    )
    db_session.add(p)
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("chat"))
    gateway = LLMGateway(responses_client=mock_client)

    # Invalid input (too short)
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", locale="fr", message="hi"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )

    # We must skip common context to avoid birth profile errors in this unit test
    request.flags.skip_common_context = True

    # Use monkeypatch to ensure the legacy compatibility resolver is NOT used here.
    # if we want to test DB resolution.
    # Actually, the real LLMGateway should find it in db_session if provided.

    # Direct test of _validate_input
    with pytest.raises(InputValidationError) as exc:
        gateway._validate_input(
            UseCaseConfig(model="m", developer_prompt="p", input_schema=schema),
            user_input={"message": "hi"},
        )
    assert "Input validation failed" in str(exc.value)

    # Full request path: supported families now fail on missing canonical assembly
    # before any legacy Stage 0.5 use-case validation can rescue the request.
    with pytest.raises(GatewayError) as exc:
        await gateway.execute_request(
            request=request,
            db=db_session,
        )

    assert "Mandatory assembly missing for supported chat family" in str(exc.value)
