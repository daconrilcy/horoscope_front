from __future__ import annotations

import logging
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.rate_limit import reset_rate_limits
from app.infra.db.base import Base
from app.infra.db.session import engine
from app.main import app

# Keep reference-data seed integration flows deterministic without manual shell exports.
os.environ.setdefault("REFERENCE_SEED_ADMIN_TOKEN", "test-seed-token")
os.environ.setdefault("ENABLE_REFERENCE_SEED_ADMIN_FALLBACK", "1")


@pytest.fixture(autouse=True, scope="session")
def _ensure_db_schema() -> None:
    # Guarantee all SQLAlchemy tables exist at session start.
    # Individual tests may call drop_all+create_all for isolation, but tests that
    # only DELETE rows (e.g. test_daily_prediction_qa) assume the schema is present.
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def _reset_in_memory_rate_limits() -> None:
    # Integration tests share the same process-wide in-memory limiter.
    # Reset between tests to avoid cross-test 429 leakage.
    reset_rate_limits()


@pytest.fixture(autouse=True)
def _reset_global_logging_disable() -> None:
    # Some unit suites disable logging globally; restore it for integration suites.
    logging.disable(logging.NOTSET)


@pytest.fixture(autouse=True)
def _reset_dependency_overrides() -> None:
    # Integration tests share a single FastAPI app instance.
    app.dependency_overrides.clear()
    try:
        yield
    finally:
        app.dependency_overrides.clear()


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
