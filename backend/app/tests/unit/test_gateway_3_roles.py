from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infra.db.base import Base
from app.infra.db.models import LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo


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


def _make_result(use_case: str) -> GatewayResult:
    return GatewayResult(
        use_case=use_case,
        request_id="req",
        trace_id="trace",
        raw_output="{}",
        structured_output=None,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="gpt-5"),
    )


@pytest.mark.asyncio
async def test_chart_json_in_user_message_not_developer(db_session: Session):
    """
    Vérifie que chart_json est placé dans le message user si absent de required_prompt_placeholders.
    """
    use_case = "test_3_roles"

    # Config WITHOUT chart_json in placeholders
    uc = LlmUseCaseConfigModel(
        key=use_case,
        display_name="Test 3-Roles",
        description="Test",
        required_prompt_placeholders=["locale", "use_case"],
    )
    db_session.add(uc)

    prompt = LlmPromptVersionModel(
        use_case_key=use_case,
        status=PromptStatus.PUBLISHED,
        model="gpt-5",
        developer_prompt="Instructions: locale={{locale}}, use_case={{use_case}}",
        created_by="test",
    )
    db_session.add(prompt)
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_result(use_case))

    gateway = LLMGateway(responses_client=mock_client)

    chart_data = '{"planets": "test"}'
    await gateway.execute(
        use_case=use_case,
        user_input={},
        context={"locale": "fr", "use_case": use_case, "chart_json": chart_data},
        request_id="test-req",
        trace_id="test-trace",
        db=db_session,
    )

    _, kwargs = mock_client.execute.call_args
    messages = kwargs["messages"]

    # Role developer should NOT contain chart_data
    developer_msg = next(m for m in messages if m["role"] == "developer")
    assert chart_data not in developer_msg["content"]

    # Role user SHOULD contain chart_data (in Technical Data)
    user_msg = next(m for m in messages if m["role"] == "user")
    assert chart_data in user_msg["content"]
    assert "Technical Data:" in user_msg["content"]


@pytest.mark.asyncio
async def test_chart_json_still_in_user_when_placeholder_required_but_absent_in_prompt(
    db_session: Session
):
    """
    Régression: si chart_json est dans required_prompt_placeholders
    mais absent du template developer_prompt, il doit rester dans le message user.
    """
    use_case = "test_chart_json_required_but_not_rendered"

    uc = LlmUseCaseConfigModel(
        key=use_case,
        display_name="Test chart_json fallback",
        description="Test",
        required_prompt_placeholders=["locale", "use_case", "chart_json"],
    )
    db_session.add(uc)

    prompt = LlmPromptVersionModel(
        use_case_key=use_case,
        status=PromptStatus.PUBLISHED,
        model="gpt-5",
        developer_prompt="Instructions: locale={{locale}}, use_case={{use_case}}",
        created_by="test",
    )
    db_session.add(prompt)
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=_make_result(use_case))

    gateway = LLMGateway(responses_client=mock_client)

    chart_data = '{"planets": "test"}'
    await gateway.execute(
        use_case=use_case,
        user_input={},
        context={"locale": "fr", "use_case": use_case, "chart_json": chart_data},
        request_id="test-req",
        trace_id="test-trace",
        db=db_session,
    )

    _, kwargs = mock_client.execute.call_args
    messages = kwargs["messages"]

    developer_msg = next(m for m in messages if m["role"] == "developer")
    assert chart_data not in developer_msg["content"]

    user_msg = next(m for m in messages if m["role"] == "user")
    assert chart_data in user_msg["content"]
    assert "Technical Data:" in user_msg["content"]
