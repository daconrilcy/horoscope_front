# Tests unitaires de resolution de persona pour le gateway LLM.
"""Valide l injection et le fallback de persona via le contrat canonique runtime."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.llm.runtime import gateway as gateway_module
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo, UseCaseConfig
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_persona import LlmPersonaModel, PersonaTone, PersonaVerbosity
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


@pytest.fixture
def db_session():
    """Construit une base memoire isolee pour les tests de persona."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(bind=test_engine)
    session = test_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def _make_mock_result(use_case: str) -> GatewayResult:
    """Retourne une reponse provider minimale pour un use case de test."""
    return GatewayResult(
        use_case=use_case,
        request_id="req",
        trace_id="trace",
        raw_output="ok",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )


def _install_fallback_config(
    monkeypatch: pytest.MonkeyPatch,
    use_case: str,
    *,
    persona_strategy: str = "optional",
) -> None:
    """Installe un contrat fallback minimal avec la strategie persona voulue."""

    def _resolver(requested_use_case: str) -> UseCaseConfig | None:
        if requested_use_case != use_case:
            return None
        return UseCaseConfig(
            model="gpt-4o-mini",
            developer_prompt="Hello {{locale}}",
            prompt_version_id=use_case,
            interaction_mode="structured",
            user_question_policy="none",
            persona_strategy=persona_strategy,
        )

    monkeypatch.setattr(gateway_module, "build_fallback_use_case_config", _resolver)


@pytest.mark.asyncio
async def test_persona_injection_success(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Injecte le premier persona autorise actif dans les messages provider."""
    persona = LlmPersonaModel(
        id=uuid.uuid4(),
        name="Luna",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        enabled=True,
    )
    db_session.add(persona)
    db_session.add(
        LlmUseCaseConfigModel(key="test_use_case", display_name="Test", description="Test")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="test_use_case",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Hello {{name}} {{locale}}",
            created_by="admin",
        )
    )
    db_session.commit()
    _install_fallback_config(monkeypatch, "test_use_case")

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("test_use_case"))
    gateway = LLMGateway(responses_client=mock_client)

    result = await gateway.execute(
        use_case="test_use_case",
        user_input={"name": "Cyril"},
        context={
            "locale": "fr",
            "use_case": "test_use_case",
            "allowed_persona_ids": [str(persona.id)],
        },
        request_id="req-1",
        trace_id="trace-1",
        db=db_session,
    )

    messages = mock_client.execute.call_args[1]["messages"]
    assert len(messages) >= 3
    assert messages[2]["role"] == "developer"
    assert "## Directives de persona : Luna" in messages[2]["content"]
    assert result.meta.persona_id == str(persona.id)


@pytest.mark.asyncio
async def test_persona_injection_disabled(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """N injecte pas un persona desactive meme s il est autorise."""
    persona = LlmPersonaModel(
        id=uuid.uuid4(),
        name="Luna",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        enabled=False,
    )
    db_session.add(persona)
    db_session.add(
        LlmUseCaseConfigModel(
            key="test_use_case_disabled",
            display_name="Test",
            description="Test",
        )
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="test_use_case_disabled",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Hello {{locale}}",
            created_by="admin",
        )
    )
    db_session.commit()
    _install_fallback_config(
        monkeypatch,
        "test_use_case_disabled",
        persona_strategy="optional",
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_mock_result("test_use_case_disabled"))
    gateway = LLMGateway(responses_client=mock_client)

    result = await gateway.execute(
        use_case="test_use_case_disabled",
        user_input={},
        context={
            "locale": "en",
            "use_case": "test_use_case_disabled",
            "allowed_persona_ids": [str(persona.id)],
        },
        request_id="req-2",
        trace_id="trace-2",
        db=db_session,
    )

    messages = mock_client.execute.call_args[1]["messages"]
    assert len(messages) == 3
    assert [message["role"] for message in messages] == ["system", "developer", "user"]
    assert result.meta.persona_id is None


@pytest.mark.asyncio
async def test_persona_required_but_missing(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Echoue explicitement si la strategie persona est required sans persona actif."""
    from app.domain.llm.runtime.contracts import GatewayConfigError

    db_session.add(
        LlmUseCaseConfigModel(key="req_use_case", display_name="Required", description="Test")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="req_use_case",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Hello {{locale}}",
            created_by="admin",
        )
    )
    db_session.commit()
    _install_fallback_config(monkeypatch, "req_use_case", persona_strategy="required")

    gateway = LLMGateway()
    config = UseCaseConfig(
        model="gpt-4o-mini",
        developer_prompt="Hello {{locale}}",
        persona_strategy="required",
    )
    with pytest.raises(GatewayConfigError) as exc_info:
        await gateway._resolve_persona(
            db_session,
            config,
            {"locale": "fr", "use_case": "req_use_case", "allowed_persona_ids": []},
            "req_use_case",
        )

    assert "No active persona available for required use case 'req_use_case'" in str(
        exc_info.value
    )
