# Tests des lectures filtrees des projections persistées.
"""Verifie que les lectures imposent type, version et scope."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.repositories.projection_repository import (
    ProjectionAccessScope,
    ProjectionRepository,
)


def test_projection_reads_are_filtered_by_type_version_and_owner_scope() -> None:
    """Un owner ne relit que sa projection du type et de la version demandes."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        repository = ProjectionRepository(session)
        owner_row = repository.create(
            chart_id="chart-owner",
            user_id=10,
            projection_type="ai_narrative_input",
            projection_version="ai_narrative_input.v1",
            projection_hash="a" * 64,
            payload={"contract_version": "ai_narrative_input.v1"},
            source_versions={"runtime_contract": "chart_object_runtime_data.v1"},
            source="test",
        )
        repository.create(
            chart_id="chart-other",
            user_id=11,
            projection_type="ai_narrative_input",
            projection_version="ai_narrative_input.v1",
            projection_hash="b" * 64,
            payload={"contract_version": "ai_narrative_input.v1"},
            source_versions={"runtime_contract": "chart_object_runtime_data.v1"},
            source="test",
        )
        repository.create(
            chart_id="chart-other-type",
            user_id=10,
            projection_type="other_projection",
            projection_version="v1",
            projection_hash="c" * 64,
            payload={"contract_version": "v1"},
            source_versions={"runtime_contract": "other.v1"},
            source="test",
        )

        result = repository.get_latest_for_scope(
            projection_type="ai_narrative_input",
            projection_version="ai_narrative_input.v1",
            access_scope=ProjectionAccessScope(role="owner", user_id=10),
        )

        assert result is not None
        assert result.id == owner_row.id


def test_owner_scope_requires_user_id() -> None:
    """Un scope owner incomplet est refuse explicitement."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        repository = ProjectionRepository(session)
        try:
            repository.get_latest_for_scope(
                projection_type="ai_narrative_input",
                projection_version="ai_narrative_input.v1",
                access_scope=ProjectionAccessScope(role="owner"),
            )
        except ValueError as error:
            assert "user_id" in str(error)
        else:
            raise AssertionError("owner scope without user_id should fail")
