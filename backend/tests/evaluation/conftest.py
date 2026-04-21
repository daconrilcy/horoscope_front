from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.llm_orchestration.providers.circuit_breaker import reset_circuit_breakers
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.execution_profile_registry import ExecutionProfileRegistry


def pytest_configure(config):
    config.addinivalue_line("markers", "evaluation: marks tests as part of the evaluation matrix")


# Setup in-memory DB for validation
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    reset_circuit_breakers()
    AssemblyRegistry.invalidate_cache()
    ExecutionProfileRegistry.invalidate_cache()
    # Ensure v2 is enabled for these tests
    with patch("app.domain.llm.runtime.gateway.settings") as mock_settings:
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
            "chart_json": '{"planets": {"sun": {"sign": "aries"}}}',
            "situation": "recherche d'emploi",
            "objective": "comprendre mon avenir",
            "today_date": "2026-04-11",
            "astro_context": {"transit": "Jupiter conjunct Sun"},
            "natal_interpretation": "Un profil dynamique et entreprenant.",
        },
        "partial": {
            "locale": "fr-FR",
            "birth_date": "1990-01-01",
            "last_user_msg": "Hello",
            "situation": "recherche d'emploi",
            "today_date": "2026-04-11",
            "chart_json": '{"planets": {"sun": {"sign": "aries"}}}',
        },
        "minimal": {
            "locale": "fr-FR",
            "today_date": "2026-04-11",
        },
    }


@pytest.fixture
def mock_personas():
    return {
        "synthetique": {
            "name": "Synthetique",
            "tone": "direct et concis",
            "style_markers": ["réponses ultra-courtes", "pas de fioritures"],
            "boundaries": ["maximum 3 phrases"],
        },
        "ample": {
            "name": "Ample",
            "tone": "poétique et détaillé",
            "style_markers": ["réponses longues et riches", "métaphores complexes"],
            "boundaries": ["minimum 10 phrases"],
        },
    }
