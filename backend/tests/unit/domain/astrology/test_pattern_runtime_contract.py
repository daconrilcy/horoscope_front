"""Tests des contrats pattern runtime et readiness graphe."""

import pytest

from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.runtime.astrological_graph_contracts import (
    AstrologicalGraphEdgeType,
    AstrologicalGraphNodeType,
)
from app.domain.astrology.runtime.pattern_runtime_data import (
    PatternGraphEdge,
    PatternGraphNode,
    PatternRuntimeData,
    PatternType,
)

ASPECT_META = {
    "family": "major",
    "is_major": True,
    "is_minor": False,
    "default_valence": "positive",
    "interpretive_valence": "harmonious",
    "energy_type": "harmonious_flow",
}


def test_pattern_runtime_references_existing_aspect_runtime() -> None:
    """Le pattern reference les runtime existants au lieu de les copier."""
    runtime = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=0.3,
        orb_used=0.3,
        orb_max=6.0,
        **ASPECT_META,
    ).aspect_runtime
    assert runtime is not None

    pattern = PatternRuntimeData(
        pattern_type=PatternType.GRAND_TRINE,
        participants=("sun", "moon"),
        aspects=(runtime,),
        confidence=0.72,
        graph_nodes=(PatternGraphNode(node_type="aspect", node_id="sun_moon_trine"),),
        graph_edges=(
            PatternGraphEdge(source="sun", target="sun_moon_trine", relation="participates_in"),
        ),
    )

    assert pattern.aspects[0] is runtime
    assert pattern.pattern_type is PatternType.GRAND_TRINE
    assert pattern.graph_nodes[0].node_type == AstrologicalGraphNodeType.ASPECT.value
    assert pattern.graph_edges[0].relation == AstrologicalGraphEdgeType.PARTICIPATES_IN.value


def test_pattern_runtime_validates_confidence() -> None:
    """La confiance pattern reste bornee."""
    runtime = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=0.3,
        orb_used=0.3,
        orb_max=6.0,
        **ASPECT_META,
    ).aspect_runtime
    assert runtime is not None

    with pytest.raises(ValueError, match="confidence"):
        PatternRuntimeData(
            pattern_type=PatternType.CUSTOM,
            participants=("sun", "moon"),
            aspects=(runtime,),
            confidence=1.4,
        )


def test_pattern_graph_contract_rejects_non_canonical_values() -> None:
    """Les noeuds et aretes readiness restent alignes sur les enums graphe."""
    with pytest.raises(ValueError, match="node_type"):
        PatternGraphNode(node_type="free_text", node_id="node-1")
    with pytest.raises(ValueError, match="relation"):
        PatternGraphEdge(source="sun", target="pattern-1", relation="free_text")
