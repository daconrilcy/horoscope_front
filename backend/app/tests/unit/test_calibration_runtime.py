from __future__ import annotations

from pathlib import Path
from tempfile import mkdtemp

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.jobs.calibration.runtime import resolve_calibration_runtime, resolve_project_root
from app.tests.regression.helpers import create_session


@pytest.fixture
def db_session():
    session = create_session()
    try:
        yield session
    finally:
        if "engine" in session.info:
            session.info["engine"].dispose()


def test_runtime_raises_on_reference_ruleset_mismatch(db_session: Session):
    with pytest.raises(ValueError, match="Calibration runtime mismatch"):
        resolve_calibration_runtime(
            db_session,
            requested_reference_version="1.0.0",
            requested_ruleset_version="1.0.0",
        )


def test_runtime_accepts_aligned_reference_ruleset_versions(db_session: Session):
    runtime = resolve_calibration_runtime(
        db_session,
        requested_reference_version="2.0.0",
        requested_ruleset_version="2.0.0",
    )

    assert runtime.reference_version == "2.0.0"
    assert runtime.ruleset_version == "2.0.0"


def test_runtime_raises_actionable_error_when_reference_missing(db_session: Session):
    with pytest.raises(ValueError, match="Calibration reference version '9.9.9' not found"):
        resolve_calibration_runtime(
            db_session,
            requested_reference_version="9.9.9",
            requested_ruleset_version="2.0.0",
        )


def test_runtime_raises_actionable_error_when_ruleset_missing():
    temp_dir = Path(mkdtemp(prefix="prediction-runtime-"))
    db_path = temp_dir / "runtime.db"
    engine = create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)

    try:
        with pytest.raises(ValueError, match="seed_31_prediction_reference_v2.py"):
            resolve_calibration_runtime(
                session,
                requested_reference_version="1.0.0",
                requested_ruleset_version="1.0.0",
            )
    finally:
        session.close()
        engine.dispose()


def test_resolve_project_root_points_to_repo_root():
    assert resolve_project_root() == Path(__file__).resolve().parents[4]
