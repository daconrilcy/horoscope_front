# Tests unitaires de reparation et fallback du gateway LLM.
"""Verifie la sequence de reparation puis le fallback canonique hors assembly."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.llm.runtime import gateway as gateway_module
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo, UseCaseConfig
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
    """Construit une base SQLite memoire pour les sequences de validation."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(bind=test_engine)
    session = test_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def _make_mock_result(use_case: str, raw_output: str) -> GatewayResult:
    """Fabrique une reponse provider courte pour piloter les sequences de test."""
    return GatewayResult(
        use_case=use_case,
        request_id="req",
        trace_id="trace",
        raw_output=raw_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )


def _install_fallback_configs(
    monkeypatch: pytest.MonkeyPatch,
    *configs: UseCaseConfig,
) -> None:
    """Installe un mini registre fallback borne aux use cases du test."""
    registry = {config.prompt_version_id: config for config in configs}

    def _resolver(use_case: str) -> UseCaseConfig | None:
        return registry.get(use_case)

    monkeypatch.setattr(gateway_module, "build_fallback_use_case_config", _resolver)


@pytest.mark.asyncio
async def test_gateway_repair_sequence(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Relance le provider en mode repair quand la premiere sortie ne valide pas le schema."""
    schema_dict = {
        "type": "object",
        "required": ["message"],
        "properties": {"message": {"type": "string"}},
    }
    output_schema = LlmOutputSchemaModel(name="test_schema", json_schema=schema_dict)
    db_session.add(output_schema)
    db_session.flush()
    db_session.add(
        LlmUseCaseConfigModel(key="test_repair", display_name="Test", description="Test")
    )
    db_session.add(
        LlmPromptVersionModel(
            use_case_key="test_repair",
            status=PromptStatus.PUBLISHED,
            developer_prompt="Hello {{locale}}",
            created_by="admin",
        )
    )
    db_session.commit()
    _install_fallback_configs(
        monkeypatch,
        UseCaseConfig(
            model="gpt-4o-mini",
            developer_prompt="Hello {{locale}}",
            prompt_version_id="test_repair",
            output_schema_id=str(output_schema.id),
        ),
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        side_effect=[
            _make_mock_result("test_repair", "INVALID JSON"),
            _make_mock_result("test_repair", '{"message": "fixed"}'),
        ]
    )
    gateway = LLMGateway(responses_client=mock_client)

    result = await gateway.execute(
        use_case="test_repair",
        user_input={},
        context={"locale": "fr", "use_case": "test_repair"},
        request_id="req-repair",
        trace_id="trace-repair",
        user_id=1,
        db=db_session,
    )

    assert result.structured_output["message"] == "fixed"
    assert result.meta.repair_attempted is True
    assert mock_client.execute.call_count == 2


@pytest.mark.asyncio
async def test_gateway_fallback_sequence(
    db_session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bascule sur le fallback cible apres echec nominal puis echec repair."""
    schema_dict = {"type": "object", "required": ["msg"]}
    output_schema = LlmOutputSchemaModel(name="test_schema", json_schema=schema_dict)
    db_session.add(output_schema)
    db_session.flush()

    db_session.add(LlmUseCaseConfigModel(key="primary", display_name="Primary", description="Test"))
    db_session.add(
        LlmUseCaseConfigModel(
            key="fallback_uc",
            display_name="Fallback",
            description="Test",
        )
    )
    db_session.add_all(
        [
            LlmPromptVersionModel(
                use_case_key="primary",
                status=PromptStatus.PUBLISHED,
                developer_prompt="P {{locale}}",
                created_by="a",
            ),
            LlmPromptVersionModel(
                use_case_key="fallback_uc",
                status=PromptStatus.PUBLISHED,
                developer_prompt="F {{locale}}",
                created_by="a",
            ),
        ]
    )
    db_session.commit()
    _install_fallback_configs(
        monkeypatch,
        UseCaseConfig(
            model="gpt-4o-mini",
            developer_prompt="P {{locale}}",
            prompt_version_id="primary",
            output_schema_id=str(output_schema.id),
            fallback_target_use_case="fallback_uc",
        ),
        UseCaseConfig(
            model="gpt-4o-mini",
            developer_prompt="F {{locale}}",
            prompt_version_id="fallback_uc",
        ),
    )

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        side_effect=[
            _make_mock_result("primary", "FAIL"),
            _make_mock_result("primary", "FAIL"),
            _make_mock_result("fallback_uc", "Fallback Success"),
        ]
    )
    gateway = LLMGateway(responses_client=mock_client)

    result = await gateway.execute(
        use_case="primary",
        user_input={},
        context={"locale": "fr", "use_case": "primary"},
        request_id="req-fallback",
        trace_id="trace-fallback",
        user_id=1,
        db=db_session,
    )

    assert result.raw_output == "Fallback Success"
    assert result.meta.fallback_triggered is True
    assert mock_client.execute.call_count == 3
