from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    with patch("app.domain.llm.runtime.gateway.settings") as mock_settings:
        mock_settings.app_env = "dev"
        mock_settings.llm_replay_encryption_key = "test-key-test-key-test-key-test-key="
        yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
