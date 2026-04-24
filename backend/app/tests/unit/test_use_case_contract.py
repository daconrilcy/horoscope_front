# Tests unitaires du contrat runtime des use cases LLM.
"""Verifie les placeholders, les strategies persona et la validation d entree canoniques."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.llm.runtime import gateway as gateway_module
from app.domain.llm.runtime.contracts import (
    ExecutionUserInput,
    GatewayMeta,
    GatewayResult,
    InputValidationError,
    LLMExecutionRequest,
    UsageInfo,
    UseCaseConfig,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


@pytest.fixture
def db_session():
    """Construit une base memoire de test pour les contrats runtime."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(bind=test_engine)
    session = test_session()
    try:
        yield session
    finally:
        session.close()


def _make_mock_result(use_case: str, persona_id: str | None = None) -> GatewayResult:
    """Retourne une reponse provider minimale compatible avec le gateway."""
    return GatewayResult(
        use_case=use_case,
        request_id="req",
        trace_id="trace",
        raw_output="ok",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m", persona_id=persona_id),
    )


def _install_fallback_config(
    monkeypatch: pytest.MonkeyPatch,
    use_case: str,
    *,
    persona_strategy: str = "optional",
    interaction_mode: str = "structured",
    user_question_policy: str = "none",
    input_schema: dict | None = None,
) -> None:
    """Installe une definition fallback locale bornee au use case de test."""

    def _resolver(requested_use_case: str) -> UseCaseConfig | None:
        if requested_use_case != use_case:
            return None
        return UseCaseConfig(
            model="gpt-4o-mini",
            developer_prompt="P {{locale}} {{last_user_msg}}",
            prompt_version_id=use_case,
            persona_strategy=persona_strategy,
            interaction_mode=interaction_mode,
            user_question_policy=user_question_policy,
            input_schema=input_schema,
            required_prompt_placeholders=[],
        )

    monkeypatch.setattr(gateway_module, "build_fallback_use_case_config", _resolver)


@pytest.mark.asyncio
async def test_persona_strategy_forbidden(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La strategie forbidden ignore tout override persona demande par l appelant."""
    db_session.add(LlmUseCaseConfigModel(key="support", display_name="Support", description="D"))
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="support",
            status=PromptStatus.PUBLISHED,
            developer_prompt="P {{locale}} {{last_user_msg}}",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_config(monkeypatch, "support", persona_strategy="forbidden")

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("support"))
    gateway = LLMGateway(responses_client=mock_client)

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="support",
            locale="fr",
            question="help",
            persona_id_override="some_id",
        ),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    await gateway.execute_request(request=request, db=db_session)

    messages = mock_client.execute.call_args.kwargs["messages"]
    assert len([message for message in messages if message["role"] == "developer"]) == 1
    assert all("## Directives de persona" not in message["content"] for message in messages)


@pytest.mark.asyncio
async def test_persona_override_rejected(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un override persona non autorise retombe sur le premier persona autorise actif."""
    persona_safe = LlmPersonaModel(id=uuid.uuid4(), name="Safe", enabled=True)
    db_session.add(persona_safe)
    db_session.add(LlmUseCaseConfigModel(key="natal", display_name="N", description="D"))
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="natal",
            status=PromptStatus.PUBLISHED,
            developer_prompt="P {{locale}} {{last_user_msg}}",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_config(monkeypatch, "natal", persona_strategy="required")

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=_make_mock_result("natal", persona_id=str(persona_safe.id))
    )
    gateway = LLMGateway(responses_client=mock_client)

    result = await gateway.execute(
        use_case="natal",
        user_input={"question": "me", "persona_id": str(uuid.uuid4())},
        context={"locale": "fr", "allowed_persona_ids": [str(persona_safe.id)]},
        request_id="r",
        trace_id="t",
        user_id=1,
        db=db_session,
    )

    assert result.meta.persona_id == str(persona_safe.id)


@pytest.mark.asyncio
async def test_persona_override_authorized(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un override persona autorise est conserve tel quel."""
    first_persona = LlmPersonaModel(id=uuid.uuid4(), name="P1", enabled=True)
    second_persona = LlmPersonaModel(id=uuid.uuid4(), name="P2", enabled=True)
    db_session.add_all([first_persona, second_persona])
    db_session.add(LlmUseCaseConfigModel(key="natal", display_name="N", description="D"))
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="natal",
            status=PromptStatus.PUBLISHED,
            developer_prompt="P {{locale}} {{last_user_msg}}",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_config(monkeypatch, "natal", persona_strategy="required")

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=_make_mock_result("natal", persona_id=str(second_persona.id))
    )
    gateway = LLMGateway(responses_client=mock_client)

    result = await gateway.execute(
        use_case="natal",
        user_input={"question": "me", "persona_id": str(second_persona.id)},
        context={
            "locale": "fr",
            "allowed_persona_ids": [str(first_persona.id), str(second_persona.id)],
        },
        request_id="r",
        trace_id="t",
        user_id=1,
        db=db_session,
    )

    assert result.meta.persona_id == str(second_persona.id)


def test_lint_usecase_placeholders() -> None:
    """Le lint de prompt reste responsable des placeholders specifiques au use case."""
    from app.ops.llm.prompt_lint import PromptLint

    required = ["{{chart_json}}"]
    text_fail = "Hello {{locale}} {{use_case}}"
    result_fail = PromptLint.lint_prompt(text_fail, use_case_required_placeholders=required)
    assert result_fail.passed is False
    assert "Use-case specific placeholder '{{chart_json}}' is missing." in result_fail.errors

    text_pass = "Hello {{locale}} {{use_case}} {{chart_json}}"
    result_pass = PromptLint.lint_prompt(text_pass, use_case_required_placeholders=required)
    assert result_pass.passed is True


@pytest.mark.asyncio
async def test_input_validation_failure(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le validateur d entree canonique rejette un payload non conforme au schema."""
    schema = {
        "type": "object",
        "required": ["message"],
        "properties": {"message": {"type": "string", "minLength": 5}},
    }
    db_session.add(LlmUseCaseConfigModel(key="chat_test", display_name="C", description="D"))
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="chat_test",
            status=PromptStatus.PUBLISHED,
            developer_prompt="P {{locale}} {{last_user_msg}}",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_config(
        monkeypatch,
        "chat_test",
        input_schema=schema,
        interaction_mode="chat",
        user_question_policy="optional",
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("chat_test"))
    gateway = LLMGateway(responses_client=mock_client)

    with pytest.raises(InputValidationError) as exc:
        gateway._validate_input(
            UseCaseConfig(model="m", developer_prompt="p", input_schema=schema),
            user_input={"message": "hi"},
        )
    assert "Input validation failed" in str(exc.value)

    persona_block, persona_id, persona_name = await gateway._resolve_persona(
        db_session,
        UseCaseConfig(
            model="m",
            developer_prompt="p",
            persona_strategy="optional",
            input_schema=schema,
        ),
        {"locale": "fr"},
        "chat_test",
    )
    assert persona_block is None
    assert persona_id is None
    assert persona_name is None
