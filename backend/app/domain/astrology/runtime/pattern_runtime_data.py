"""Contrats preparatoires des patterns astrologiques.

Les patterns referencent les runtime existants et preparent un futur graphe
astrologique sans calculer les detectors complexes dans cette story.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.astrology.runtime.aspect_modifiers import AspectModifierRuntimeData
from app.domain.astrology.runtime.aspect_runtime_data import AspectRuntimeData
from app.domain.astrology.runtime.astrological_graph_contracts import (
    AstrologicalGraphEdgeType,
    AstrologicalGraphNodeType,
)
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData


class PatternType(StrEnum):
    """Types de patterns supportables par le runtime canonique."""

    T_SQUARE = "t_square"
    GRAND_TRINE = "grand_trine"
    YOD = "yod"
    KITE = "kite"
    MYSTIC_RECTANGLE = "mystic_rectangle"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class PatternGraphNode:
    """Noeud minimal pour la readiness graphe."""

    node_type: str
    node_id: str

    def __post_init__(self) -> None:
        """Valide le type canonique et l'identifiant du noeud."""
        if self.node_type not in {node_type.value for node_type in AstrologicalGraphNodeType}:
            raise ValueError("pattern graph node_type is not canonical")
        if not self.node_id.strip():
            raise ValueError("pattern graph node_id is required")


@dataclass(frozen=True, slots=True)
class PatternGraphEdge:
    """Arete minimale pour la readiness graphe."""

    source: str
    target: str
    relation: str

    def __post_init__(self) -> None:
        """Valide la relation canonique et les extremites de l'arete."""
        if self.relation not in {edge_type.value for edge_type in AstrologicalGraphEdgeType}:
            raise ValueError("pattern graph edge relation is not canonical")
        if not self.source.strip() or not self.target.strip():
            raise ValueError("pattern graph edge requires source and target")


@dataclass(frozen=True, slots=True)
class PatternRuntimeData:
    """Contrat d'agregation pattern base sur les runtime existants."""

    pattern_type: PatternType
    participants: tuple[str, ...]
    aspects: tuple[AspectRuntimeData, ...]
    confidence: float
    houses: tuple[HouseRuntimeData, ...] = ()
    signs: tuple[str, ...] = ()
    modifiers: tuple[AspectModifierRuntimeData, ...] = ()
    graph_nodes: tuple[PatternGraphNode, ...] = field(default_factory=tuple)
    graph_edges: tuple[PatternGraphEdge, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Valide les bornes et references minimales du pattern."""
        if not self.participants or not self.aspects:
            raise ValueError("pattern runtime requires participants and aspects")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("pattern confidence must be between 0 and 1")
