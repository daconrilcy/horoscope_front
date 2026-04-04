from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    GatewayConfigError,
    GatewayMeta,
    GatewayResult,
    InputValidationError,
    UsageInfo,
)
from app.prompts.catalog import NATAL_FREE_SHORT_SCHEMA


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


def create_mock_result(use_case, raw_output, structured_output=None):
    return GatewayResult(
        use_case=use_case,
        request_id="req",
        trace_id="trace",
        raw_output=raw_output,
        structured_output=structured_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="gpt-4o-mini"),
    )


@pytest.mark.asyncio
async def test_structured_mode_no_question(db_session):
    """Test interaction_mode=structured, user_question_policy=none."""
    uc = LlmUseCaseConfigModel(
        key="test_none",
        display_name="T",
        description="D",
        interaction_mode="structured",
        user_question_policy="none",
    )
    p = LlmPromptVersionModel(
        use_case_key="test_none",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="Dev",
        created_by="a",
    )
    db_session.add_all([uc, p])
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=create_mock_result("test_none", "Result"))

    gateway = LLMGateway(responses_client=mock_client)
    await gateway.execute(
        "test_none",
        {"question": "Ignored?"},
        {"locale": "fr", "use_case": "test_none"},
        "r",
        "t",
        user_id=1,
        db=db_session,
    )

    args = mock_client.execute.call_args.kwargs
    messages = args["messages"]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert "Ignored?" not in user_msg["content"]
    # L2-fix: fallback message is now locale-aware (locale="fr" → French)
    assert "Interpr" in user_msg["content"]  # "Interprète les données astrologiques fournies."


@pytest.mark.asyncio
async def test_structured_mode_optional_question(db_session):
    """Test interaction_mode=structured, user_question_policy=optional."""
    uc = LlmUseCaseConfigModel(
        key="test_opt",
        display_name="T",
        description="D",
        interaction_mode="structured",
        user_question_policy="optional",
    )
    p = LlmPromptVersionModel(
        use_case_key="test_opt",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="Dev",
        created_by="a",
    )
    db_session.add_all([uc, p])
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=create_mock_result("test_opt", "Result"))

    gateway = LLMGateway(responses_client=mock_client)

    # With question
    await gateway.execute(
        "test_opt",
        {"question": "How am I?"},
        {"locale": "fr", "use_case": "test_opt"},
        "r1",
        "t",
        user_id=1,
        db=db_session,
    )
    user_msg = next(
        m for m in mock_client.execute.call_args.kwargs["messages"] if m["role"] == "user"
    )
    assert "How am I?" in user_msg["content"]

    # Without question
    await gateway.execute(
        "test_opt",
        {},
        {"locale": "fr", "use_case": "test_opt"},
        "r2",
        "t",
        user_id=1,
        db=db_session,
    )
    user_msg = next(
        m for m in mock_client.execute.call_args.kwargs["messages"] if m["role"] == "user"
    )
    # L2-fix: fallback is locale-aware (locale="fr" → French fallback)
    assert "Interpr" in user_msg["content"]  # "Interprète les données astrologiques fournies."


@pytest.mark.asyncio
async def test_structured_mode_required_question(db_session, monkeypatch):
    """Test interaction_mode=structured, user_question_policy=required."""
    uc = LlmUseCaseConfigModel(
        key="test_req",
        display_name="T",
        description="D",
        interaction_mode="structured",
        user_question_policy="required",
    )
    p = LlmPromptVersionModel(
        use_case_key="test_req",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="Dev",
        created_by="a",
    )
    db_session.add_all([uc, p])
    db_session.commit()

    gateway = LLMGateway(responses_client=MagicMock())

    # Missing question
    with pytest.raises(InputValidationError) as exc:
        await gateway.execute(
            "test_req",
            {},
            {"locale": "fr", "use_case": "test_req"},
            "r",
            "t",
            user_id=1,
            db=db_session,
        )
    assert "User question is required" in str(exc.value)


@pytest.mark.asyncio
async def test_chat_mode_with_history(db_session, monkeypatch):
    """Test interaction_mode=chat with history injection."""
    uc = LlmUseCaseConfigModel(
        key="test_chat",
        display_name="T",
        description="D",
        interaction_mode="chat",
        user_question_policy="optional",
    )
    p = LlmPromptVersionModel(
        use_case_key="test_chat",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="Dev",
        created_by="a",
    )
    db_session.add_all([uc, p])
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=create_mock_result("test_chat", "Reply"))

    gateway = LLMGateway(responses_client=mock_client)

    history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there"}]

    await gateway.execute(
        "test_chat",
        {"question": "How are you?"},
        {"locale": "fr", "use_case": "test_chat", "history": history},
        "r",
        "t",
        user_id=1,
        db=db_session,
    )

    args = mock_client.execute.call_args.kwargs
    messages = args["messages"]

    # system, developer, persona (skipped here), user, assistant, user
    assert len(messages) == 5  # system, dev, user (hello), assistant (hi), user (how are you)
    assert messages[2]["content"] == "Hello"
    assert messages[3]["content"] == "Hi there"
    assert messages[4]["content"] == "How are you?"


@pytest.mark.asyncio
async def test_schema_blocking_paid_use_case(db_session, monkeypatch):
    """Point 0.2: Rendre schema_dict absent bloquant pour natal_interpretation."""
    uc = LlmUseCaseConfigModel(
        key="natal_interpretation",
        display_name="N",
        description="D",
        output_schema_id=None,  # Missing schema
    )
    p = LlmPromptVersionModel(
        use_case_key="natal_interpretation",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="Dev",
        created_by="a",
    )
    db_session.add_all([uc, p])
    db_session.commit()

    gateway = LLMGateway(responses_client=MagicMock())

    with pytest.raises(GatewayConfigError) as exc:
        await gateway.execute(
            "natal_interpretation",
            {},
            {"locale": "fr", "use_case": "natal_interpretation"},
            "r",
            "t",
            user_id=1,
            db=db_session,
        )
    assert "Mandatory output schema missing" in str(exc.value)


@pytest.mark.asyncio
async def test_schema_name_in_payload(db_session, monkeypatch):
    """Point 0.1: Correct schema.name in payload."""
    schema = LlmOutputSchemaModel(name="AstroResponse_v2", json_schema={"type": "object"})
    db_session.add(schema)
    db_session.flush()

    uc = LlmUseCaseConfigModel(
        key="test_schema", display_name="T", description="D", output_schema_id=str(schema.id)
    )
    p = LlmPromptVersionModel(
        use_case_key="test_schema",
        status=PromptStatus.PUBLISHED,
        model="m",
        developer_prompt="Dev",
        created_by="a",
    )
    db_session.add_all([uc, p])
    db_session.commit()

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=create_mock_result("test_schema", "{}"))

    gateway = LLMGateway(responses_client=mock_client)
    await gateway.execute(
        "test_schema",
        {},
        {"locale": "fr", "use_case": "test_schema"},
        "r",
        "t",
        user_id=1,
        db=db_session,
    )

    args = mock_client.execute.call_args.kwargs
    resp_format = args["response_format"]
    assert resp_format["json_schema"]["name"] == "astroresponse_v2"


@pytest.mark.asyncio
async def test_catalog_schema_is_used_for_free_natal_fallback(db_session):
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=create_mock_result(
            "natal_long_free",
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
    await gateway.execute(
        "natal_long_free",
        {},
        {
            "locale": "fr-FR",
            "use_case": "natal_long_free",
            "chart_json": {"meta": {"birth_date": "2017-03-14"}},
        },
        "r",
        "t",
        user_id=1,
        db=db_session,
    )

    args = mock_client.execute.call_args.kwargs
    resp_format = args["response_format"]
    assert resp_format is not None
    assert resp_format["json_schema"]["name"] == "natal-long-free-v1"
    assert resp_format["json_schema"]["schema"]["required"] == [
        "title",
        "summary",
        "accordion_titles",
    ]


def test_catalog_free_natal_schema_is_openai_responses_compatible():
    assert NATAL_FREE_SHORT_SCHEMA["additionalProperties"] is False
