import pytest
import yaml
from pathlib import Path

def pytest_configure(config):
    config.addinivalue_line("markers", "evaluation: marks tests as part of the evaluation matrix")

from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infra.db.base import Base

# Setup in-memory DB for validation
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    # Ensure v2 is enabled for these tests
    with patch("app.llm_orchestration.gateway.settings") as mock_settings:
        mock_settings.app_env = "dev"
        mock_settings.llm_replay_encryption_key = "test-key-test-key-test-key-test-key="
        yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def evaluation_matrix():
    path = Path(__file__).parent / "evaluation_matrix.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["matrix"]

@pytest.fixture
def mock_context_by_quality():
    return {
        "full": {
            "locale": "fr-FR",
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "birth_place": "Paris",
            "last_user_msg": "Hello",
            "natal_data": {"planets": {"sun": "aries"}},
            "chart_json": '{"planets": {}}',
            "situation": "recherche d'emploi",
            "objective": "comprendre mon avenir"
        },
        "partial": {
            "locale": "fr-FR",
            "birth_date": "1990-01-01",
            "last_user_msg": "Hello",
            "situation": "recherche d'emploi"
        },
        "minimal": {
            "locale": "fr-FR"
        }
    }

@pytest.fixture
def mock_personas():
    return {
        "synthetique": {
            "name": "Synthetique",
            "tone": "direct et concis",
            "style_markers": ["réponses ultra-courtes", "pas de fioritures"],
            "boundaries": ["maximum 3 phrases"]
        },
        "ample": {
            "name": "Ample",
            "tone": "poétique et détaillé",
            "style_markers": ["réponses longues et riches", "métaphores complexes"],
            "boundaries": ["minimum 10 phrases"]
        }
    }
