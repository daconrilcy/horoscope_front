from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.base import Base
from app.infra.db.models import (
    LlmOutputSchemaModel,
    LlmPersonaModel,
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
)
from app.infra.db.models.llm_persona import PersonaTone, PersonaVerbosity
from app.infra.db.models.llm_prompt import PromptStatus


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


def _make_gateway_result(use_case: str, raw_output: str) -> GatewayResult:
    return GatewayResult(
        use_case=use_case,
        request_id="req-qa-runtime",
        trace_id="trace-qa-runtime",
        raw_output=raw_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="gpt-5"),
    )


@pytest.mark.asyncio
async def test_llm_qa_runtime_contract_proves_prompt_persona_and_output_validation(db_session):
    use_case_key = "natal_interpretation"

    schema = LlmOutputSchemaModel(
        name="qa_runtime_schema",
        version=1,
        json_schema={
            "type": "object",
            "required": ["message"],
            "properties": {"message": {"type": "string"}},
        },
    )
    db_session.add(schema)
    db_session.flush()

    persona = LlmPersonaModel(
        id=uuid.uuid4(),
        name="Luna QA",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        enabled=True,
    )
    db_session.add(persona)

    use_case = LlmUseCaseConfigModel(
        key=use_case_key,
        display_name="QA Runtime Contract",
        description="Verifies canonical QA runtime proofs",
        output_schema_id=str(schema.id),
        allowed_persona_ids=[str(persona.id)],
        required_prompt_placeholders=["locale", "chart_json"],
    )
    db_session.add(use_case)

    prompt = LlmPromptVersionModel(
        use_case_key=use_case_key,
        status=PromptStatus.PUBLISHED,
        developer_prompt="Locale={{locale}}\nChart={{chart_json}}",
        model="gpt-5",
        created_by="qa",
    )
    db_session.add(prompt)
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=_make_gateway_result(
            use_case_key,
            raw_output='{"message": "runtime-ok"}',
        )
    )

    gateway = LLMGateway(responses_client=mock_client)

    with patch("app.domain.llm.runtime.gateway.get_canonical_use_case_contract", return_value=None):
        result = await gateway.execute(
            use_case=use_case_key,
            user_input={},
            context={
                "locale": "fr-FR",
                "use_case": use_case_key,
                "chart_json": '{"sun":"taurus"}',
            },
            request_id="req-qa-runtime",
            trace_id="trace-qa-runtime",
            user_id=1,
            db=db_session,
        )

    _, kwargs = mock_client.execute.call_args
    messages = kwargs["messages"]
    developer_messages = [message for message in messages if message["role"] == "developer"]

    assert any("Locale=fr-FR" in message["content"] for message in developer_messages)
    assert any('Chart={"sun":"taurus"}' in message["content"] for message in developer_messages)
    assert any(
        "## Directives de persona : Luna QA" in message["content"] for message in developer_messages
    )
    assert result.structured_output == {"message": "runtime-ok"}
    assert result.meta.validation_status == "valid"
    assert result.meta.persona_id == str(persona.id)
