from __future__ import annotations

import logging

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.domain.llm.configuration.assembly_registry import AssemblyRegistry
from app.domain.llm.configuration.execution_profile_registry import ExecutionProfileRegistry
from app.infra.db.base import Base
from app.infrastructure.providers.llm.circuit_breaker import reset_circuit_breakers
from app.main import app


@pytest.fixture(autouse=True)
def _reset_global_logging_disable() -> None:
    # Some tests may globally disable logging; restore default behavior.
    logging.disable(logging.NOTSET)


@pytest.fixture(autouse=True)
def _reset_dependency_overrides() -> None:
    app.dependency_overrides.clear()
    try:
        yield
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _reset_llm_runtime_state() -> None:
    reset_circuit_breakers()
    AssemblyRegistry.invalidate_cache()
    ExecutionProfileRegistry.invalidate_cache()


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
