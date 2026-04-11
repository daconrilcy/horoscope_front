from __future__ import annotations

import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2

# In-memory SQLite for tests
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        # Invalidate cache before each test to ensure isolation
        from app.llm_orchestration.services.prompt_registry_v2 import _prompt_cache

        _prompt_cache.clear()

        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_get_active_prompt_none(db):
    prompt = PromptRegistryV2.get_active_prompt(db, "unknown")
    assert prompt is None


def test_publish_and_get_active(db):
    # Setup
    uc = LlmUseCaseConfigModel(key="test_uc", display_name="Test", description="Test")
    db.add(uc)
    db.commit()

    v1 = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="test_uc",
        status=PromptStatus.DRAFT,
        developer_prompt="Prompt V1 {{locale}} {{use_case}}",
        model="gpt-4",
        created_by="test-user",
    )
    db.add(v1)
    db.commit()

    # Act
    published = PromptRegistryV2.publish_prompt(db, v1.id)

    # Assert
    assert published.status == PromptStatus.PUBLISHED
    active = PromptRegistryV2.get_active_prompt(db, "test_uc")
    assert active.id == v1.id


def test_publish_archives_previous(db):
    # Setup
    uc = LlmUseCaseConfigModel(key="test_uc", display_name="Test", description="Test")
    db.add(uc)
    db.commit()

    v1 = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="test_uc",
        status=PromptStatus.PUBLISHED,
        developer_prompt="P1",
        model="m",
        created_by="u",
    )
    v2 = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="test_uc",
        status=PromptStatus.DRAFT,
        developer_prompt="P2",
        model="m",
        created_by="u",
    )
    db.add_all([v1, v2])
    db.commit()

    # Act
    PromptRegistryV2.publish_prompt(db, v2.id)
    db.refresh(v1)

    # Assert
    assert v1.status == PromptStatus.ARCHIVED
    assert v2.status == PromptStatus.PUBLISHED
    active = PromptRegistryV2.get_active_prompt(db, "test_uc")
    assert active.id == v2.id


def test_rollback(db):
    # Setup
    uc = LlmUseCaseConfigModel(key="test_uc", display_name="Test", description="Test")
    db.add(uc)
    db.commit()

    v1 = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="test_uc",
        status=PromptStatus.ARCHIVED,
        developer_prompt="P1",
        model="m",
        created_by="u",
        published_at=datetime.now(),
    )
    v2 = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="test_uc",
        status=PromptStatus.PUBLISHED,
        developer_prompt="P2",
        model="m",
        created_by="u",
        published_at=datetime.now(),
    )
    db.add_all([v1, v2])
    db.commit()

    # Act
    rolled_back = PromptRegistryV2.rollback_prompt(db, "test_uc")
    db.refresh(v2)

    # Assert
    assert rolled_back.id == v1.id
    assert rolled_back.status == PromptStatus.PUBLISHED
    assert v2.status == PromptStatus.ARCHIVED


def test_cache_ttl(db):
    # Setup
    uc = LlmUseCaseConfigModel(key="test_uc", display_name="Test", description="Test")
    db.add(uc)
    v1 = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="test_uc",
        status=PromptStatus.PUBLISHED,
        developer_prompt="P1",
        model="m",
        created_by="u",
    )
    db.add(v1)
    db.commit()

    # Act - first call populates cache
    p1 = PromptRegistryV2.get_active_prompt(db, "test_uc")
    assert p1.developer_prompt == "P1"

    # Modify DB directly without registry (bypass cache invalidation)
    db.execute(
        update(LlmPromptVersionModel)
        .where(LlmPromptVersionModel.id == v1.id)
        .values(developer_prompt="P1-MODIFIED")
    )
    db.commit()

    # Second call should still return P1 from cache
    p2 = PromptRegistryV2.get_active_prompt(db, "test_uc")
    assert p2.developer_prompt == "P1"

    # After explicit invalidation, it should get from DB
    PromptRegistryV2.invalidate_cache("test_uc")
    p3 = PromptRegistryV2.get_active_prompt(db, "test_uc")
    assert p3.developer_prompt == "P1-MODIFIED"


def test_publish_prompt_forbidden_for_legacy_daily_prediction(db):
    uc = LlmUseCaseConfigModel(
        key="daily_prediction",
        display_name="Legacy Daily",
        description="Legacy daily narrator alias",
    )
    db.add(uc)
    db.commit()

    version = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="daily_prediction",
        status=PromptStatus.DRAFT,
        developer_prompt="Legacy daily prompt",
        model="gpt-4o-mini",
        created_by="test-user",
    )
    db.add(version)
    db.commit()

    with pytest.raises(ValueError, match="forbidden for nominal use"):
        PromptRegistryV2.publish_prompt(db, version.id)


def test_rollback_prompt_forbidden_for_legacy_daily_prediction(db):
    uc = LlmUseCaseConfigModel(
        key="daily_prediction",
        display_name="Legacy Daily",
        description="Legacy daily narrator alias",
    )
    db.add(uc)
    db.commit()

    archived = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="daily_prediction",
        status=PromptStatus.ARCHIVED,
        developer_prompt="Legacy daily prompt",
        model="gpt-4o-mini",
        created_by="test-user",
        published_at=datetime.now(),
    )
    db.add(archived)
    db.commit()

    with pytest.raises(ValueError, match="forbidden for nominal use"):
        PromptRegistryV2.rollback_prompt(db, "daily_prediction")
