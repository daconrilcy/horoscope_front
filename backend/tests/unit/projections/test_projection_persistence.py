# Tests de persistance des projections produites par un builder reel.
"""Couvre le stockage du hash, du payload et des versions source."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.domain.astrology.interpretation.ai_narrative_input_builder import AINarrativeInputBuilder
from app.domain.astrology.interpretation.ai_narrative_input_contracts import (
    AINarrativeSourceVersions,
)
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    ChartInterpretationInputRuntimeData,
    ChartInterpretationMetadataRuntimeData,
)
from app.infra.db.base import Base
from app.infra.db.repositories.projection_repository import ProjectionRepository
from app.services.projection_persistence_service import ProjectionPersistenceService


class _AINarrativeProjectionBuilder:
    """Adapte le builder narratif reel au protocole de persistance."""

    def __init__(self) -> None:
        """Initialise le builder canonique existant."""
        self._builder = AINarrativeInputBuilder()

    def build(self, interpretation_input: ChartInterpretationInputRuntimeData) -> object:
        """Produit un contrat IA depuis l'input interpretatif existant."""
        return self._builder.from_interpretation_input(interpretation_input)


def test_persisted_projection_stores_hash_and_source_versions() -> None:
    """La ligne persiste hash, payload canonique et versions de source."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    source_versions = AINarrativeSourceVersions(
        runtime_contract="chart_object_runtime_data.v1",
        interpretation_input="chart_interpretation_input.v1",
        public_projection="official_product_primitives.v1",
    )

    with Session(engine) as session:
        service = ProjectionPersistenceService(ProjectionRepository(session))
        row = service.persist_from_builder(
            builder=_AINarrativeProjectionBuilder(),
            projection_type="ai_narrative_input",
            projection_version="ai_narrative_input.v1",
            chart_id="chart-264",
            user_id=42,
            source_versions=source_versions,
            source="AINarrativeInputBuilder.from_interpretation_input",
            builder_args=(_minimal_interpretation_input(),),
        )

        assert len(row.projection_hash) == 64
        assert row.payload["contract_version"] == "ai_narrative_input.v1"
        assert row.source_versions == {
            "graph_trace": None,
            "interpretation_input": "chart_interpretation_input.v1",
            "public_projection": "official_product_primitives.v1",
            "reference_versions": [],
            "rule_governance": None,
            "runtime_contract": "chart_object_runtime_data.v1",
        }
        assert row.source == "AINarrativeInputBuilder.from_interpretation_input"
        assert row.generated_at is not None


def _minimal_interpretation_input() -> ChartInterpretationInputRuntimeData:
    """Construit l'input minimal accepte par le builder narratif reel."""
    return ChartInterpretationInputRuntimeData(
        chart_id="chart-264",
        chart_type="natal",
        locale="fr-FR",
        objects=(),
        aspects=(),
        dignities=(),
        house_positions=(),
        rulerships=(),
        dominance=(),
        fixed_star_contacts=(),
        metadata=ChartInterpretationMetadataRuntimeData(
            source_codes=("chart_interpretation_input.test",),
            object_count=0,
            aspect_count=0,
        ),
    )
