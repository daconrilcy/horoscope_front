# Contrat interne de trace des executions de graphes de calcul astrologiques.
"""Construit une trace redigee depuis les resultats du runner runtime."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
)

if TYPE_CHECKING:
    from app.domain.astrology.runtime.calculation_graph_runner import (
        CalculationGraphExecutionError,
        CalculationGraphExecutionResult,
        CalculationNodeResult,
    )

EXECUTION_TRACE_VERSION = "1"
TRACE_REDACTION_POLICY = "keys-and-provenance-refs-v1"


class CalculationTraceCacheStatus(StrEnum):
    """Statut de cache expose par la trace sans valeur cachee."""

    HIT = "hit"
    MISS = "miss"


class CalculationTraceErrorKind(StrEnum):
    """Categories techniques normalisees sans objet cause brut."""

    VALIDATION_ERROR = "validation_error"
    MISSING_INPUT = "missing_input"
    UNKNOWN_CALCULATOR = "unknown_calculator"
    CALCULATOR_FAILURE = "calculator_failure"


@dataclass(frozen=True, slots=True)
class CalculationGraphNodeTrace:
    """Trace redigee d'un node execute, echoue ou servi par cache."""

    code: str
    status: str
    cache_status: CalculationTraceCacheStatus
    duration_ms: float | None
    input_keys: tuple[str, ...]
    output_keys: tuple[str, ...]
    error_kind: CalculationTraceErrorKind | None = None
    provenance_ref: str | None = None


@dataclass(frozen=True, slots=True)
class CalculationGraphExecutionTrace:
    """Contrat versionne de trace distinct de la provenance et du replay."""

    version: str
    graph_code: str
    graph_version: str
    run_id: str | None
    nodes: tuple[CalculationGraphNodeTrace, ...]
    redaction_policy: str
    provenance_refs: tuple[str, ...]


def build_execution_trace(
    graph: CalculationGraphDefinition,
    result: CalculationGraphExecutionResult,
    *,
    run_id: str | None = None,
) -> CalculationGraphExecutionTrace:
    """Construit une trace interne sans recopier les inputs, outputs ou causes."""
    nodes = tuple(_node_trace(node_result) for node_result in result.node_results)
    return CalculationGraphExecutionTrace(
        version=EXECUTION_TRACE_VERSION,
        graph_code=graph.graph_code,
        graph_version=graph.version,
        run_id=run_id,
        nodes=nodes,
        redaction_policy=TRACE_REDACTION_POLICY,
        provenance_refs=tuple(
            node.provenance_ref for node in nodes if node.provenance_ref is not None
        ),
    )


def execution_trace_to_dict(trace: CalculationGraphExecutionTrace) -> dict[str, object]:
    """Serialise la trace pour les preuves internes sans creer de contrat public."""
    return {
        "version": trace.version,
        "graph_code": trace.graph_code,
        "graph_version": trace.graph_version,
        "run_id": trace.run_id,
        "nodes": [
            {
                "code": node.code,
                "status": node.status,
                "cache_status": node.cache_status.value,
                "duration_ms": node.duration_ms,
                "input_keys": list(node.input_keys),
                "output_keys": list(node.output_keys),
                "error_kind": node.error_kind.value if node.error_kind is not None else None,
                "provenance_ref": node.provenance_ref,
            }
            for node in trace.nodes
        ],
        "redaction_policy": trace.redaction_policy,
        "provenance_refs": list(trace.provenance_refs),
        "contract_note": {
            "trace": "ordered redacted execution facts",
            "provenance": "source references owned by runner results",
            "replay_snapshot": "not implemented by this contract",
        },
    }


def _node_trace(node_result: CalculationNodeResult) -> CalculationGraphNodeTrace:
    """Reduit un resultat de node aux cles et references non sensibles."""
    return CalculationGraphNodeTrace(
        code=node_result.node_code,
        status=node_result.status.value,
        cache_status=(
            CalculationTraceCacheStatus.HIT
            if node_result.cache_hit
            else CalculationTraceCacheStatus.MISS
        ),
        duration_ms=node_result.duration_ms,
        input_keys=node_result.input_keys,
        output_keys=(node_result.output_key,),
        error_kind=_error_kind(node_result.error),
        provenance_ref=(
            f"provenance:{node_result.node_code}" if node_result.error is None else None
        ),
    )


def _error_kind(
    error: CalculationGraphExecutionError | None,
) -> CalculationTraceErrorKind | None:
    """Normalise l'erreur runtime sans exposer l'exception cause."""
    if error is None:
        return None
    if error.key is not None:
        return CalculationTraceErrorKind.MISSING_INPUT
    if error.cause is not None:
        return CalculationTraceErrorKind.CALCULATOR_FAILURE
    if "unknown calculator" in error.message:
        return CalculationTraceErrorKind.UNKNOWN_CALCULATOR
    return CalculationTraceErrorKind.VALIDATION_ERROR
