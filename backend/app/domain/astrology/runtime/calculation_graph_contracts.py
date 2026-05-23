# Contrats declaratifs du graphe de calcul astrologique runtime.
"""Contrats types pour decrire un graphe de calcul sans l'executer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CalculationNodeStatus(StrEnum):
    """Statuts observables d'un node dans un futur runner de graphe."""

    DECLARED = "declared"
    READY = "ready"
    EXECUTED = "executed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class CalculationInputDefinition:
    """Definition d'une entree disponible pour les nodes du graphe."""

    key: str
    value_type: str
    required: bool = True


@dataclass(frozen=True, slots=True)
class CalculationNodeDefinition:
    """Contrat stable d'un calcul declaratif et de ses dependances."""

    code: str
    output_key: str
    depends_on: tuple[str, ...]
    calculator: str
    optional_depends_on: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CalculationGraphDefinition:
    """Definition inspectable d'un graphe de calcul astrologique."""

    graph_code: str
    version: str
    nodes: tuple[CalculationNodeDefinition, ...]
    required_inputs: tuple[CalculationInputDefinition, ...] = ()


@dataclass(frozen=True, slots=True)
class CalculationGraphValidationError:
    """Erreur deterministe produite par la validation du graphe."""

    message: str
    node_code: str | None = None
    key: str | None = None


@dataclass(frozen=True, slots=True)
class CalculationGraphValidationResult:
    """Resultat structure d'une validation declarative de graphe."""

    graph_code: str
    is_valid: bool
    errors: tuple[CalculationGraphValidationError, ...]
    topological_order: tuple[str, ...] = ()
