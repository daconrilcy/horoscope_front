from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infra.db.base import Base
from app.infra.db.models import LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway


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


from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo


def _make_mock_result(model: str) -> GatewayResult:
    """Helper : crée un GatewayResult mock minimal."""
    return GatewayResult(
        use_case="test",
        request_id="test",
        trace_id="test",
        raw_output="{}",
        structured_output={},
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model=model),
    )


@pytest.mark.asyncio
async def test_gateway_transmits_gpt5_params_from_db(db_session: Session):
    """Vérifie que le Gateway extrait reasoning/verbosity de la DB et les passe au client."""
    use_case = "test_gpt5_params"

    uc = LlmUseCaseConfigModel(
        key=use_case,
        display_name="Test GPT-5",
        description="Test",
        required_prompt_placeholders=["locale", "use_case"],
    )
    db_session.add(uc)

    prompt = LlmPromptVersionModel(
        use_case_key=use_case,
        status=PromptStatus.PUBLISHED,
        model="gpt-5",
        developer_prompt="Test GPT-5",
        reasoning_effort="low",
        verbosity="high",
        created_by="test",
    )
    db_session.add(prompt)
    db_session.commit()

    mock_client = AsyncMock()
    mock_client.execute.return_value = _make_mock_result("gpt-5")

    gateway = LLMGateway(responses_client=mock_client)

    try:
        await gateway.execute(
            use_case=use_case,
            user_input={},
            context={"locale": "fr", "use_case": use_case},
            request_id="test-req",
            trace_id="test-trace",
            user_id=1,
            db=db_session,
        )

        _, kwargs = mock_client.execute.call_args
        assert kwargs["model"] == "gpt-5"
        assert kwargs["reasoning_effort"] == "low"
        assert kwargs["verbosity"] == "high"

    finally:
        db_session.delete(prompt)
        db_session.delete(uc)
        db_session.commit()


@pytest.mark.asyncio
async def test_gateway_does_not_pass_reasoning_for_gpt4o(db_session: Session):
    """Un use case gpt-4o-mini sans reasoning_effort/verbosity transmet None au client."""
    use_case = "test_gpt4o_no_reasoning"

    uc = LlmUseCaseConfigModel(
        key=use_case,
        display_name="Test GPT-4o-mini",
        description="Test",
        required_prompt_placeholders=["locale", "use_case"],
    )
    db_session.add(uc)

    prompt = LlmPromptVersionModel(
        use_case_key=use_case,
        status=PromptStatus.PUBLISHED,
        model="gpt-4o-mini",
        developer_prompt="Test gpt-4o-mini",
        reasoning_effort=None,  # Pas de reasoning pour gpt-4o-mini
        verbosity=None,
        created_by="test",
    )
    db_session.add(prompt)
    db_session.commit()

    mock_client = AsyncMock()
    mock_client.execute.return_value = _make_mock_result("gpt-4o-mini")

    gateway = LLMGateway(responses_client=mock_client)

    try:
        await gateway.execute(
            use_case=use_case,
            user_input={},
            context={"locale": "fr", "use_case": use_case},
            request_id="test-req-4o",
            trace_id="test-trace-4o",
            user_id=1,
            db=db_session,
        )

        _, kwargs = mock_client.execute.call_args
        assert kwargs["model"] == "gpt-4o-mini"
        assert kwargs.get("reasoning_effort") is None
        assert kwargs.get("verbosity") is None

    finally:
        db_session.delete(prompt)
        db_session.delete(uc)
        db_session.commit()
