import pytest
from sqlalchemy.exc import IntegrityError

from app.infra.db.base import Base
from app.infra.db.models.llm_persona import LlmPersonaModel, PersonaTone, PersonaVerbosity
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService


def _cleanup_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _create_user(db, email):
    auth = AuthService.register(db, email=email, password="password123")
    db.commit()
    return auth.user.id


def _create_persona(db, name):
    persona = LlmPersonaModel(
        name=name,
        tone=PersonaTone.DIRECT,
        verbosity=PersonaVerbosity.MEDIUM,
        style_markers=[],
        boundaries=[],
        allowed_topics=[],
        disallowed_topics=[],
        formatting={},
    )
    db.add(persona)
    db.commit()
    return persona.id


def test_chat_multi_persona_isolation():
    _cleanup_tables()
    with SessionLocal() as db:
        user_id = _create_user(db, "user1@example.com")
        persona_a_id = _create_persona(db, "Persona A")
        persona_b_id = _create_persona(db, "Persona B")

        repo = ChatRepository(db)

        conv_a = repo.create_conversation(user_id=user_id, persona_id=persona_a_id)
        conv_b = repo.create_conversation(user_id=user_id, persona_id=persona_b_id)

        assert conv_a.id != conv_b.id
        assert conv_a.persona_id == persona_a_id
        assert conv_b.persona_id == persona_b_id


def test_chat_anti_doublon_invariant():
    _cleanup_tables()
    with SessionLocal() as db:
        user_id = _create_user(db, "user2@example.com")
        persona_id = _create_persona(db, "Persona A")

        repo = ChatRepository(db)

        # Create first active conversation
        repo.create_conversation(user_id=user_id, persona_id=persona_id)

        # Should fail with IntegrityError when trying to create
        # second active conversation for same user/persona
        # Note: In SQLite, the unique index with WHERE is supported since 3.8.0.
        with pytest.raises(IntegrityError):
            repo.create_conversation(user_id=user_id, persona_id=persona_id)
            db.commit()


def test_get_or_create_active_conversation_concurrency():
    """
    Test that multiple concurrent calls to get_or_create_active_conversation
    only create one conversation and don't crash with IntegrityError.
    """
    _cleanup_tables()

    import concurrent.futures

    with SessionLocal() as db:
        user_id = _create_user(db, "concurrent@example.com")
        persona_id = _create_persona(db, "Persona Concurrent")
        db.commit()

    def _get_or_create():
        # Each thread needs its own session
        with SessionLocal() as db:
            repo = ChatRepository(db)
            conv = repo.get_or_create_active_conversation(user_id=user_id, persona_id=persona_id)
            db.commit()
            return conv.id

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Launch 5 simultaneous requests
        futures = [executor.submit(_get_or_create) for _ in range(5)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All should have returned the SAME conversation ID
    assert len(set(results)) == 1

    # Verify in DB that only one exists
    with SessionLocal() as db:
        from sqlalchemy import func, select

        from app.infra.db.models.chat_conversation import ChatConversationModel

        count = db.scalar(
            select(func.count(ChatConversationModel.id)).where(
                ChatConversationModel.user_id == user_id,
                ChatConversationModel.persona_id == persona_id,
                ChatConversationModel.status == "active",
            )
        )
        assert count == 1
