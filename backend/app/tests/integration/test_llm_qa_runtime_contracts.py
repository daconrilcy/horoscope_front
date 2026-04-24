from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    UsageInfo,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel, PersonaTone, PersonaVerbosity
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
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
        required_prompt_placeholders=["locale", "chart_json"],
    )
    db_session.add(use_case)

    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key=use_case_key,
        status=PromptStatus.PUBLISHED,
        developer_prompt="Locale={{locale}}\nChart={{chart_json}}",
        created_by="qa",
    )
    db_session.add(prompt)
    db_session.flush()

    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="qa-runtime-profile",
        provider="openai",
        model="gpt-5",
        reasoning_profile="medium",
        verbosity_profile="balanced",
        output_mode="structured_json",
        tool_mode="none",
        timeout_seconds=30,
        feature="natal",
        subfeature="interpretation",
        plan="premium",
        status=PromptStatus.PUBLISHED,
        created_by="qa",
    )
    db_session.add(profile)
    db_session.flush()

    db_session.add(
        PromptAssemblyConfigModel(
            id=uuid.uuid4(),
            feature="natal",
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=prompt.id,
            persona_ref=persona.id,
            execution_profile_ref=profile.id,
            output_schema_id=schema.id,
            status=PromptStatus.PUBLISHED,
            created_by="qa",
        )
    )
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=_make_gateway_result(
            use_case_key,
            raw_output='{"message": "runtime-ok"}',
        )
    )

    gateway = LLMGateway(responses_client=mock_client)

    with patch(
        "app.domain.llm.runtime.gateway.CommonContextBuilder.build",
        side_effect=RuntimeError,
    ):
        result = await gateway.execute_request(
            LLMExecutionRequest(
                user_input=ExecutionUserInput(
                    use_case=use_case_key,
                    feature="natal",
                    subfeature="interpretation",
                    plan="premium",
                    locale="fr-FR",
                ),
                context=ExecutionContext(chart_json='{"sun":"taurus"}'),
                request_id="req-qa-runtime",
                trace_id="trace-qa-runtime",
                user_id=1,
            ),
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
