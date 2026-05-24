# Execution pure des graphes de calcul astrologiques declaratifs.
"""Execute un graphe valide avec registry explicite, cache local et provenance."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from time import perf_counter
from types import MappingProxyType

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationGraphValidationError,
    CalculationNodeDefinition,
    CalculationNodeStatus,
)
from app.domain.astrology.runtime.calculation_graph_execution_trace import (
    CalculationGraphExecutionTrace,
    build_execution_trace,
)
from app.domain.astrology.runtime.calculation_graph_validator import (
    validate_calculation_graph_definition,
)

CalculationNodeCallable = Callable[["CalculationGraphContext"], object]


@dataclass(frozen=True, slots=True)
class CalculationGraphExecutionError:
    """Erreur runtime stable exposee par le runner de graphe."""

    message: str
    node_code: str | None = None
    key: str | None = None
    cause: Exception | None = None


@dataclass(frozen=True, slots=True)
class CalculationGraphContext:
    """Contexte immuable des valeurs disponibles pendant une execution."""

    values: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Isole les valeurs pour proteger le contexte fourni par l'appelant."""
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))

    def get_required(self, key: str) -> object:
        """Retourne une valeur obligatoire ou signale une dependance absente."""
        if key not in self.values:
            raise KeyError(f"Missing required input '{key}'.")
        return self.values[key]


@dataclass(frozen=True, slots=True)
class CalculationNodeResult:
    """Resultat observable d'un node execute ou servi depuis le cache local."""

    node_code: str
    output_key: str
    status: CalculationNodeStatus
    input_keys: tuple[str, ...]
    calculator: str
    cache_hit: bool
    duration_ms: float | None = None
    error: CalculationGraphExecutionError | None = None


@dataclass(frozen=True, slots=True)
class CalculationGraphExecutionResult:
    """Resultat global d'une execution de graphe de calcul."""

    graph_code: str
    success: bool
    outputs: Mapping[str, object]
    node_results: tuple[CalculationNodeResult, ...]
    execution_order: tuple[str, ...]
    cache_hits: tuple[str, ...]
    provenance: Mapping[str, Mapping[str, object]]
    errors: tuple[CalculationGraphExecutionError, ...] = ()
    execution_trace: CalculationGraphExecutionTrace | None = None

    def __post_init__(self) -> None:
        """Fige les surfaces de sortie pour eviter les mutations apres execution."""
        object.__setattr__(self, "outputs", MappingProxyType(dict(self.outputs)))
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType(
                {
                    node_code: MappingProxyType(dict(provenance))
                    for node_code, provenance in self.provenance.items()
                }
            ),
        )


class CalculationNodeRegistry:
    """Registry explicite des calculateurs autorises pour un graphe."""

    def __init__(self, calculators: Mapping[str, CalculationNodeCallable] | None = None) -> None:
        """Construit un registry a partir de calculateurs nommes explicitement."""
        self._calculators = dict(calculators or {})

    def get(self, calculator: str) -> CalculationNodeCallable | None:
        """Retourne le calculateur enregistre ou aucun si le code est inconnu."""
        return self._calculators.get(calculator)


class CalculationGraphRunner:
    """Execute des graphes declaratifs valides dans un ordre topologique."""

    def __init__(self, registry: CalculationNodeRegistry) -> None:
        """Associe le runner a son registry explicite de calculateurs."""
        self._registry = registry

    def run(
        self,
        definition: CalculationGraphDefinition,
        initial_context: CalculationGraphContext,
        *,
        run_id: str | None = None,
    ) -> CalculationGraphExecutionResult:
        """Valide puis execute le graphe avec un cache limite a cet appel."""
        validation = validate_calculation_graph_definition(definition)
        if not validation.is_valid:
            result = _validation_failure(definition, validation.errors)
            return _with_execution_trace(definition, result, run_id)

        values = dict(initial_context.values)
        node_by_code = {node.code: node for node in definition.nodes}
        node_results: list[CalculationNodeResult] = []
        execution_order: list[str] = []
        cache_hits: list[str] = []
        provenance: dict[str, Mapping[str, object]] = {}

        for node_code in validation.topological_order:
            node = node_by_code[node_code]
            input_keys = _consumed_input_keys(node, values)
            if node.output_key in values:
                cache_hits.append(node.code)
                node_results.append(_node_result(node, input_keys, cache_hit=True, duration_ms=0.0))
                execution_order.append(node.code)
                provenance[node.code] = _provenance(node, input_keys, values[node.output_key])
                continue

            missing_key = _missing_required_key(node, values)
            if missing_key is not None:
                result = _execution_failure(
                    definition,
                    node_results,
                    execution_order,
                    cache_hits,
                    provenance,
                    node,
                    input_keys,
                    CalculationGraphExecutionError(
                        f"Calculation node '{node.code}' missing required input '{missing_key}'.",
                        node_code=node.code,
                        key=missing_key,
                    ),
                )
                return _with_execution_trace(definition, result, run_id)

            calculator = self._registry.get(node.calculator)
            if calculator is None:
                result = _execution_failure(
                    definition,
                    node_results,
                    execution_order,
                    cache_hits,
                    provenance,
                    node,
                    input_keys,
                    CalculationGraphExecutionError(
                        f"Calculation node '{node.code}' uses unknown calculator "
                        f"'{node.calculator}'.",
                        node_code=node.code,
                    ),
                )
                return _with_execution_trace(definition, result, run_id)

            started_at = perf_counter()
            try:
                output = calculator(CalculationGraphContext(values))
            except Exception as exc:
                result = _execution_failure(
                    definition,
                    node_results,
                    execution_order,
                    cache_hits,
                    provenance,
                    node,
                    input_keys,
                    CalculationGraphExecutionError(
                        f"Calculation node '{node.code}' calculator '{node.calculator}' failed: "
                        f"{exc}.",
                        node_code=node.code,
                        cause=exc,
                    ),
                    duration_ms=_elapsed_ms(started_at),
                )
                return _with_execution_trace(definition, result, run_id)

            values[node.output_key] = output
            execution_order.append(node.code)
            node_results.append(
                _node_result(
                    node,
                    input_keys,
                    cache_hit=False,
                    duration_ms=_elapsed_ms(started_at),
                )
            )
            provenance[node.code] = _provenance(node, input_keys, output)

        result = CalculationGraphExecutionResult(
            graph_code=definition.graph_code,
            success=True,
            outputs={node.output_key: values[node.output_key] for node in definition.nodes},
            node_results=tuple(node_results),
            execution_order=tuple(execution_order),
            cache_hits=tuple(cache_hits),
            provenance=provenance,
        )
        return _with_execution_trace(definition, result, run_id)


def _validation_failure(
    definition: CalculationGraphDefinition,
    validation_errors: tuple[CalculationGraphValidationError, ...],
) -> CalculationGraphExecutionResult:
    """Convertit les erreurs declaratives en resultat runtime stable."""
    return CalculationGraphExecutionResult(
        graph_code=definition.graph_code,
        success=False,
        outputs={},
        node_results=(),
        execution_order=(),
        cache_hits=(),
        provenance={},
        errors=tuple(
            CalculationGraphExecutionError(
                error.message,
                node_code=error.node_code,
                key=error.key,
            )
            for error in validation_errors
        ),
    )


def _execution_failure(
    definition: CalculationGraphDefinition,
    node_results: list[CalculationNodeResult],
    execution_order: list[str],
    cache_hits: list[str],
    provenance: dict[str, Mapping[str, object]],
    node: CalculationNodeDefinition,
    input_keys: tuple[str, ...],
    error: CalculationGraphExecutionError,
    duration_ms: float | None = 0.0,
) -> CalculationGraphExecutionResult:
    """Construit un resultat d'echec sans poursuivre les nodes suivants."""
    failed_results = (
        *node_results,
        CalculationNodeResult(
            node_code=node.code,
            output_key=node.output_key,
            status=CalculationNodeStatus.FAILED,
            input_keys=input_keys,
            calculator=node.calculator,
            cache_hit=False,
            duration_ms=duration_ms,
            error=error,
        ),
    )
    return CalculationGraphExecutionResult(
        graph_code=definition.graph_code,
        success=False,
        outputs={
            result.output_key: provenance[result.node_code]["output"] for result in node_results
        },
        node_results=failed_results,
        execution_order=tuple(execution_order),
        cache_hits=tuple(cache_hits),
        provenance=provenance,
        errors=(error,),
    )


def _node_result(
    node: CalculationNodeDefinition,
    input_keys: tuple[str, ...],
    *,
    cache_hit: bool,
    duration_ms: float | None,
) -> CalculationNodeResult:
    """Cree le resultat nominal d'un node execute ou cache."""
    return CalculationNodeResult(
        node_code=node.code,
        output_key=node.output_key,
        status=CalculationNodeStatus.EXECUTED,
        input_keys=input_keys,
        calculator=node.calculator,
        cache_hit=cache_hit,
        duration_ms=duration_ms,
    )


def _consumed_input_keys(
    node: CalculationNodeDefinition,
    values: Mapping[str, object],
) -> tuple[str, ...]:
    """Liste les inputs obligatoires et optionnels reellement disponibles."""
    optional_keys = tuple(key for key in node.optional_depends_on if key in values)
    return (*node.depends_on, *optional_keys)


def _missing_required_key(
    node: CalculationNodeDefinition,
    values: Mapping[str, object],
) -> str | None:
    """Retourne la premiere dependance obligatoire absente."""
    return next((key for key in node.depends_on if key not in values), None)


def _provenance(
    node: CalculationNodeDefinition,
    input_keys: tuple[str, ...],
    output: object,
) -> Mapping[str, object]:
    """Expose la provenance minimale attendue pour un node."""
    return {
        "node_code": node.code,
        "input_keys": input_keys,
        "output_key": node.output_key,
        "output": output,
        "calculator": node.calculator,
    }


def _with_execution_trace(
    definition: CalculationGraphDefinition,
    result: CalculationGraphExecutionResult,
    run_id: str | None,
) -> CalculationGraphExecutionResult:
    """Attache la trace interne redigee au resultat du runner."""
    return CalculationGraphExecutionResult(
        graph_code=result.graph_code,
        success=result.success,
        outputs=result.outputs,
        node_results=result.node_results,
        execution_order=result.execution_order,
        cache_hits=result.cache_hits,
        provenance=result.provenance,
        errors=result.errors,
        execution_trace=build_execution_trace(definition, result, run_id=run_id),
    )


def _elapsed_ms(started_at: float) -> float:
    """Retourne une duree technique arrondie sans information metier sensible."""
    return round((perf_counter() - started_at) * 1000, 3)
