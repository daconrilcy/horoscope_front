from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base

# Setup in-memory DB for validation
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    from app.llm_orchestration.services.assembly_registry import AssemblyRegistry

    # Invalidate cache before and after to ensure clean state
    AssemblyRegistry(None).invalidate_cache()
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    # Ensure v2 is enabled for these tests
    with patch("app.domain.llm.runtime.gateway.settings") as mock_settings:
        mock_settings.app_env = "dev"
        mock_settings.llm_replay_encryption_key = "test-key-test-key-test-key-test-key="
        yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    AssemblyRegistry(None).invalidate_cache()
