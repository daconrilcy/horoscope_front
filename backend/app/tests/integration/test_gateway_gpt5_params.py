"""Tests d integration des parametres runtime GPT via les profils d execution canoniques."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

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
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


@pytest.fixture
def db_session():
    """Construit une base SQLite en memoire pour verifier le chemin runtime canonique."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def _make_mock_result(model: str) -> GatewayResult:
    """Fabrique une reponse gateway minimale pour les assertions de transport."""
    return GatewayResult(
        use_case="test",
        request_id="test",
        trace_id="test",
        raw_output="{}",
        structured_output={},
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model=model),
    )


def _seed_runtime_artifacts(
    db_session: Session,
    *,
    use_case_key: str,
    feature: str,
    subfeature: str | None,
    plan: str,
    model: str,
    reasoning_profile: str,
    verbosity_profile: str,
) -> None:
    """Prepare un prompt publie, un profil d execution et une assembly canonique."""
    schema = LlmOutputSchemaModel(
        id=uuid.uuid4(),
        name="AstroResponse_v1",
        version=1,
        json_schema={"type": "object", "properties": {"title": {"type": "string"}}},
    )
    db_session.add(schema)

    db_session.add(
        LlmUseCaseConfigModel(
            key=use_case_key,
            display_name=use_case_key,
            description="Test runtime canonique",
            required_prompt_placeholders=["chart_json"],
        )
    )

    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key=use_case_key,
        status=PromptStatus.PUBLISHED,
        developer_prompt="Analyse {{chart_json}}",
        created_by="test",
    )
    db_session.add(prompt)
    db_session.flush()

    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name=f"profile-{use_case_key}",
        provider="openai",
        model=model,
        reasoning_profile=reasoning_profile,
        verbosity_profile=verbosity_profile,
        output_mode="structured_json",
        tool_mode="none",
        timeout_seconds=30,
        feature=feature,
        subfeature=subfeature,
        plan=plan,
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db_session.add(profile)
    db_session.flush()

    db_session.add(
        PromptAssemblyConfigModel(
            id=uuid.uuid4(),
            feature=feature,
            subfeature=subfeature,
            plan=plan,
            locale="fr-FR",
            feature_template_ref=prompt.id,
            execution_profile_ref=profile.id,
            output_schema_id=schema.id,
            status=PromptStatus.PUBLISHED,
            created_by="test",
        )
    )
    db_session.commit()


@pytest.mark.asyncio
async def test_gateway_transmits_gpt5_params_from_execution_profile(db_session: Session):
    """Verifie que le gateway transmet les parametres GPT-5 portes par le profil canonique."""
    use_case = "natal_interpretation_short"
    _seed_runtime_artifacts(
        db_session,
        use_case_key=use_case,
        feature="natal",
        subfeature="interpretation",
        plan="free",
        model="gpt-5",
        reasoning_profile="medium",
        verbosity_profile="detailed",
    )

    mock_client = AsyncMock()
    mock_client.execute.return_value = _make_mock_result("gpt-5")

    gateway = LLMGateway(responses_client=mock_client)

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case=use_case,
            feature="natal",
            subfeature="interpretation",
            plan="free",
            locale="fr-FR",
        ),
        context=ExecutionContext(chart_json='{"sun":"aries"}'),
        request_id="test-req",
        trace_id="test-trace",
        user_id=1,
    )

    await gateway.execute_request(request, db=db_session)

    _, kwargs = mock_client.execute.call_args
    assert kwargs["model"] == "gpt-5"
    assert kwargs["reasoning_effort"] == "medium"
    assert kwargs["verbosity"] == "verbose"


@pytest.mark.asyncio
async def test_gateway_transmits_gpt4o_without_reasoning_effort(db_session: Session):
    """Verifie qu un profil non reasoning ne transmet pas de reasoning_effort."""
    use_case = "natal_interpretation_short"
    _seed_runtime_artifacts(
        db_session,
        use_case_key=use_case,
        feature="natal",
        subfeature="interpretation",
        plan="free",
        model="gpt-4o-mini",
        reasoning_profile="off",
        verbosity_profile="balanced",
    )

    mock_client = AsyncMock()
    mock_client.execute.return_value = _make_mock_result("gpt-4o-mini")

    gateway = LLMGateway(responses_client=mock_client)

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case=use_case,
            feature="natal",
            subfeature="interpretation",
            plan="free",
            locale="fr-FR",
        ),
        context=ExecutionContext(chart_json='{"sun":"aries"}'),
        request_id="test-req-4o",
        trace_id="test-trace-4o",
        user_id=1,
    )

    await gateway.execute_request(request, db=db_session)

    _, kwargs = mock_client.execute.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs.get("reasoning_effort") is None
    assert kwargs["verbosity"] == "normal"
