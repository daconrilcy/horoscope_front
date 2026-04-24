import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.application.llm.ai_engine_adapter import set_test_chat_generator
from app.infra.db.base import Base
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.user import UserModel
from app.services.llm_generation.chat_guidance_service import ChatGuidanceService

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def mock_llm():
    async def mock_generator(*args, **kwargs):
        return "mocked response"

    set_test_chat_generator(mock_generator)
    yield
    from app.application.llm.ai_engine_adapter import reset_test_generators

    reset_test_generators()


def test_chat_message_idempotence_hit(db: Session):
    # Setup: Create a user and a persona
    user = UserModel(email="test@example.com", password_hash="hashed_password", role="user")
    db.add(user)
    db.flush()

    persona = LlmPersonaModel(
        id=uuid.uuid4(), name="Astrologue Standard", description="Standard", enabled=True
    )
    db.add(persona)
    db.flush()

    # 1. Send first message with client_message_id
    client_message_id = str(uuid.uuid4())
    message_content = "Hello, what is my fate?"

    response1 = ChatGuidanceService.send_message(
        db,
        user_id=user.id,
        message=message_content,
        persona_id=str(persona.id),
        client_message_id=client_message_id,
    )

    # 2. Resend same message with same client_message_id
    response2 = ChatGuidanceService.send_message(
        db,
        user_id=user.id,
        message=message_content,
        persona_id=str(persona.id),
        client_message_id=client_message_id,
    )

    # Verify both responses are the same (idempotency hit)
    assert response1.user_message.message_id == response2.user_message.message_id
    assert response1.assistant_message.message_id == response2.assistant_message.message_id
    assert response1.assistant_message.content == response2.assistant_message.content


def test_chat_message_idempotence_race_condition(db: Session):
    # Setup: Create a user and a persona
    user = UserModel(email="test2@example.com", password_hash="hashed_password", role="user")
    db.add(user)
    db.flush()

    persona = LlmPersonaModel(
        id=uuid.uuid4(), name="Astrologue Standard", description="Standard", enabled=True
    )
    db.add(persona)
    db.flush()

    # Simulate a partial creation: User message exists but assistant does not.
    client_message_id = str(uuid.uuid4())
    conversation = ChatConversationModel(user_id=user.id, persona_id=persona.id, status="active")
    db.add(conversation)
    db.flush()

    user_message = ChatMessageModel(
        conversation_id=conversation.id,
        role="user",
        content="Hello race condition",
        client_message_id=client_message_id,
    )
    db.add(user_message)
    db.flush()
    db.commit()

    # Now call send_message with same client_message_id.
    # It should pick up the existing user message and generate a new assistant response.
    response = ChatGuidanceService.send_message(
        db,
        user_id=user.id,
        message="Hello race condition",
        persona_id=str(persona.id),
        client_message_id=client_message_id,
    )

    assert response.user_message.message_id == user_message.id
    assert response.assistant_message.role == "assistant"

    # Verify assistant message is linked to the client_message_id
    assistant_msg = db.get(ChatMessageModel, response.assistant_message.message_id)
    assert assistant_msg.reply_to_client_message_id == client_message_id
