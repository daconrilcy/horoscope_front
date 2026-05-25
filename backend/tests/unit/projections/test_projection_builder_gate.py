# Tests du blocage en absence de builder de projection.
"""Garantit qu'aucun payload synthétique n'est persiste sans builder reel."""

from __future__ import annotations

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.models.projection_persistence import PersistedProjectionModel
from app.infra.db.repositories.projection_repository import ProjectionRepository
from app.services.projection_persistence_service import (
    ProjectionBuilderUnavailableError,
    ProjectionPersistenceService,
)


def test_builder_absence_blocks_before_persistence() -> None:
    """L'absence de builder reel bloque avant insertion en base."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        service = ProjectionPersistenceService(ProjectionRepository(session))
        try:
            service.persist_from_builder(
                builder=None,
                projection_type="ai_narrative_input",
                projection_version="ai_narrative_input.v1",
                chart_id="chart-264",
                user_id=42,
                source_versions={"runtime_contract": "chart_object_runtime_data.v1"},
                source="missing",
            )
        except ProjectionBuilderUnavailableError:
            pass
        else:
            raise AssertionError("builder absence should block persistence")

        assert session.scalars(select(PersistedProjectionModel)).all() == []
