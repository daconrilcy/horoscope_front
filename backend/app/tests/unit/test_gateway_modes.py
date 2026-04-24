# Tests unitaires du gateway sur les modes d interaction et la resolution de schema.
"""Valide les comportements chat/structured et les schemas canoniques du gateway LLM."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.llm.prompting.catalog import NATAL_FREE_SHORT_SCHEMA
from app.domain.llm.runtime import gateway as gateway_module
from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayConfigError,
    GatewayMeta,
    GatewayResult,
    InputValidationError,
    LLMExecutionRequest,
    UsageInfo,
    UseCaseConfig,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


@pytest.fixture
def db_session():
    """Construit une base SQLite memoire isolee pour les tests du gateway."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(bind=test_engine)
    session = test_session()
    try:
        yield session
    finally:
        session.close()


def _make_mock_result(
    use_case: str,
    raw_output: str,
    structured_output: dict | None = None,
) -> GatewayResult:
    """Fabrique une reponse provider minimaliste exploitable par le gateway."""
    return GatewayResult(
        use_case=use_case,
        request_id="req",
        trace_id="trace",
        raw_output=raw_output,
        structured_output=structured_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="gpt-4o-mini"),
    )


def _install_fallback_registry(
    monkeypatch: pytest.MonkeyPatch,
    *configs: UseCaseConfig,
) -> None:
    """Installe un registre fallback local borne aux use cases testes."""
    registry = {config.prompt_version_id: config for config in configs}

    def _resolver(use_case: str) -> UseCaseConfig | None:
        return registry.get(use_case)

    monkeypatch.setattr(gateway_module, "build_fallback_use_case_config", _resolver)


def _fallback_config(
    use_case: str,
    *,
    developer_prompt: str = "Dev",
    interaction_mode: str = "structured",
    user_question_policy: str = "none",
    output_schema_id: str | None = None,
    model: str = "gpt-4o-mini",
) -> UseCaseConfig:
    """Construit un contrat fallback canonique pour un test unitaire."""
    return UseCaseConfig(
        model=model,
        developer_prompt=developer_prompt,
        prompt_version_id=use_case,
        interaction_mode=interaction_mode,
        user_question_policy=user_question_policy,
        output_schema_id=output_schema_id,
        required_prompt_placeholders=[],
    )


@pytest.mark.asyncio
async def test_structured_mode_no_question(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ignore la question utilisateur en mode structured quand la policy vaut none."""
    db_session.add(
        LlmUseCaseConfigModel(key="test_none", display_name="T", description="D")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="test_none",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Dev",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_registry(
        monkeypatch,
        _fallback_config("test_none", interaction_mode="structured", user_question_policy="none"),
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("test_none", "Result"))
    gateway = LLMGateway(responses_client=mock_client)

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test_none", locale="fr", question="Ignored?"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    await gateway.execute_request(request=request, db=db_session)

    messages = mock_client.execute.call_args.kwargs["messages"]
    user_msg = next(message for message in messages if message["role"] == "user")
    assert "Ignored?" not in user_msg["content"]
    assert "Interpr" in user_msg["content"]


@pytest.mark.asyncio
async def test_structured_mode_optional_question(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Injecte la question uniquement quand elle existe en mode structured optional."""
    db_session.add(
        LlmUseCaseConfigModel(key="test_opt", display_name="T", description="D")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="test_opt",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Dev",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_registry(
        monkeypatch,
        _fallback_config(
            "test_opt",
            interaction_mode="structured",
            user_question_policy="optional",
        ),
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("test_opt", "Result"))
    gateway = LLMGateway(responses_client=mock_client)

    request_with_question = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test_opt", locale="fr", question="How am I?"),
        request_id="r1",
        trace_id="t1",
        user_id=1,
    )
    await gateway.execute_request(request=request_with_question, db=db_session)
    user_msg = next(
        message
        for message in mock_client.execute.call_args.kwargs["messages"]
        if message["role"] == "user"
    )
    assert "How am I?" in user_msg["content"]

    request_without_question = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test_opt", locale="fr"),
        request_id="r2",
        trace_id="t2",
        user_id=1,
    )
    await gateway.execute_request(request=request_without_question, db=db_session)
    user_msg = next(
        message
        for message in mock_client.execute.call_args.kwargs["messages"]
        if message["role"] == "user"
    )
    assert "Interpr" in user_msg["content"]


@pytest.mark.asyncio
async def test_structured_mode_required_question(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exige une question en mode structured quand la policy vaut required."""
    db_session.add(
        LlmUseCaseConfigModel(key="test_req", display_name="T", description="D")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="test_req",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Dev",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_registry(
        monkeypatch,
        _fallback_config(
            "test_req",
            interaction_mode="structured",
            user_question_policy="required",
        ),
    )

    gateway = LLMGateway(responses_client=MagicMock())
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test_req", locale="fr"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    with pytest.raises(InputValidationError) as exc:
        await gateway.execute_request(request=request, db=db_session)
    assert "User question is required" in str(exc.value)


@pytest.mark.asyncio
async def test_chat_mode_with_history(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Injecte l historique complet en mode chat avant le message utilisateur courant."""
    db_session.add(
        LlmUseCaseConfigModel(key="test_chat", display_name="T", description="D")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="test_chat",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Dev",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_registry(
        monkeypatch,
        _fallback_config("test_chat", interaction_mode="chat", user_question_policy="optional"),
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("test_chat", "Reply"))
    gateway = LLMGateway(responses_client=mock_client)

    history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there"}]
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test_chat", locale="fr", question="How are you?"),
        context=ExecutionContext(history=history),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    await gateway.execute_request(request=request, db=db_session)

    messages = mock_client.execute.call_args.kwargs["messages"]
    assert len(messages) == 5
    assert messages[2]["content"] == "Hello"
    assert messages[3]["content"] == "Hi there"
    assert messages[4]["content"] == "How are you?"


@pytest.mark.asyncio
async def test_schema_blocking_paid_use_case(db_session) -> None:
    """Bloque un use case payant nominal si aucun schema de sortie n est resolu."""
    use_case = "natal_interpretation"
    db_session.add(
        LlmUseCaseConfigModel(key=use_case, display_name="N", description="D")
    )
    prompt = LlmPromptVersionModel(
        use_case_key=use_case,
        status=PromptStatus.PUBLISHED,
        developer_prompt="Dev",
        created_by="a",
    )
    db_session.add(prompt)
    db_session.flush()

    profile = LlmExecutionProfileModel(
        name="natal-paid-test",
        provider="openai",
        model="gpt-4o",
        reasoning_profile="off",
        verbosity_profile="balanced",
        output_mode="structured_json",
        tool_mode="none",
        feature="natal",
        subfeature="interpretation",
        plan="premium",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db_session.add(profile)
    db_session.flush()
    db_session.add(
        PromptAssemblyConfigModel(
            feature="natal",
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=prompt.id,
            execution_profile_ref=profile.id,
            status=PromptStatus.PUBLISHED,
            created_by="test",
        )
    )
    db_session.commit()

    gateway = LLMGateway(responses_client=MagicMock())
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case=use_case,
            locale="fr-FR",
            feature="natal",
            subfeature="interpretation",
            plan="premium",
        ),
        context=ExecutionContext(chart_json='{"sun_sign":"aries"}'),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    with pytest.raises(GatewayConfigError) as exc:
        await gateway.execute_request(request=request, db=db_session)
    assert "Mandatory output schema missing" in str(exc.value)


@pytest.mark.asyncio
async def test_schema_name_in_payload(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reprend le nom canonique du schema SQLAlchemy dans le payload provider."""
    schema = LlmOutputSchemaModel(name="test_schema", json_schema={"type": "object"})
    db_session.add(schema)
    db_session.flush()
    db_session.add(
        LlmUseCaseConfigModel(key="test_schema", display_name="T", description="D")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="test_schema",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Dev",
            created_by="a",
        )
    )
    db_session.commit()
    _install_fallback_registry(
        monkeypatch,
        _fallback_config("test_schema", output_schema_id=str(schema.id)),
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("test_schema", "{}"))
    gateway = LLMGateway(responses_client=mock_client)

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test_schema", locale="fr"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    await gateway.execute_request(request=request, db=db_session)

    response_format = mock_client.execute.call_args.kwargs["response_format"]
    assert response_format["json_schema"]["name"] == "test_schema"


@pytest.mark.asyncio
async def test_catalog_schema_is_used_for_free_natal_fallback(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reutilise le schema catalogue pour `natal_long_free` hors chemin assembly."""
    use_case = "natal_long_free"
    db_session.add(
        LlmUseCaseConfigModel(key=use_case, display_name="Free Natal", description="D")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key=use_case,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Dev {{locale}}",
            created_by="test",
        )
    )
    db_session.commit()
    _install_fallback_registry(monkeypatch, _fallback_config(use_case))

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=_make_mock_result(
            use_case,
            (
                '{"title":"Votre thème révèle une intuition vibrante.",'
                '"summary":"Resume","accordion_titles":["A","B"]}'
            ),
            {
                "title": "Votre thème révèle une intuition vibrante.",
                "summary": "Resume",
                "accordion_titles": ["A", "B"],
            },
        )
    )
    gateway = LLMGateway(responses_client=mock_client)

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case=use_case, locale="fr-FR"),
        context=ExecutionContext(chart_json='{"meta": {"birth_date": "2017-03-14"}}'),
        request_id="r",
        trace_id="t",
        user_id=1,
    )
    await gateway.execute_request(request=request, db=db_session)

    response_format = mock_client.execute.call_args.kwargs["response_format"]
    assert response_format["json_schema"]["schema"] == NATAL_FREE_SHORT_SCHEMA
