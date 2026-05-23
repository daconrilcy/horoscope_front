# Validation pure des graphes de calcul astrologiques declaratifs.
"""Valide les contrats de graphe sans importer ni executer de calculateur."""

from __future__ import annotations

from collections import Counter

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationGraphValidationError,
    CalculationGraphValidationResult,
    CalculationNodeDefinition,
)


def validate_calculation_graph_definition(
    graph: CalculationGraphDefinition,
) -> CalculationGraphValidationResult:
    """Valide un graphe et retourne ses erreurs ainsi qu'un ordre theorique."""
    errors: list[CalculationGraphValidationError] = []
    errors.extend(_validate_non_empty_fields(graph))
    errors.extend(_validate_duplicates(graph))

    if errors:
        return CalculationGraphValidationResult(
            graph_code=graph.graph_code,
            is_valid=False,
            errors=tuple(errors),
        )

    known_input_keys = {input_definition.key for input_definition in graph.required_inputs}
    output_to_node = {node.output_key: node for node in graph.nodes}
    errors.extend(_validate_required_dependencies(graph, known_input_keys, output_to_node))

    cycle_errors, topological_order = _topological_order(graph, output_to_node)
    errors.extend(cycle_errors)

    return CalculationGraphValidationResult(
        graph_code=graph.graph_code,
        is_valid=not errors,
        errors=tuple(errors),
        topological_order=() if errors else topological_order,
    )


def _validate_non_empty_fields(
    graph: CalculationGraphDefinition,
) -> tuple[CalculationGraphValidationError, ...]:
    """Controle les identifiants obligatoires du contrat."""
    errors: list[CalculationGraphValidationError] = []
    if not graph.graph_code.strip():
        errors.append(CalculationGraphValidationError("Calculation graph requires a graph_code."))
    if not graph.version.strip():
        errors.append(
            CalculationGraphValidationError(
                f"Calculation graph '{graph.graph_code}' requires a version."
            )
        )
    for input_definition in graph.required_inputs:
        if not input_definition.key.strip():
            errors.append(
                CalculationGraphValidationError(
                    f"Calculation graph '{graph.graph_code}' declares an input without key."
                )
            )
        if not input_definition.value_type.strip():
            errors.append(
                CalculationGraphValidationError(
                    f"Calculation input '{input_definition.key}' requires a value_type.",
                    key=input_definition.key,
                )
            )
    for node in graph.nodes:
        errors.extend(_validate_node_non_empty_fields(graph, node))
    return tuple(errors)


def _validate_node_non_empty_fields(
    graph: CalculationGraphDefinition,
    node: CalculationNodeDefinition,
) -> tuple[CalculationGraphValidationError, ...]:
    """Controle les champs obligatoires d'un node."""
    errors: list[CalculationGraphValidationError] = []
    if not node.code.strip():
        errors.append(
            CalculationGraphValidationError(
                f"Calculation graph '{graph.graph_code}' declares a node without code."
            )
        )
    if not node.output_key.strip():
        errors.append(
            CalculationGraphValidationError(
                f"Calculation node '{node.code}' requires an output_key.",
                node_code=node.code,
            )
        )
    if not node.calculator.strip():
        errors.append(
            CalculationGraphValidationError(
                f"Calculation node '{node.code}' requires a calculator.",
                node_code=node.code,
            )
        )
    for dependency in node.depends_on:
        if not dependency.strip():
            errors.append(
                CalculationGraphValidationError(
                    f"Calculation node '{node.code}' declares an empty dependency.",
                    node_code=node.code,
                )
            )
    for dependency in node.optional_depends_on:
        if not dependency.strip():
            errors.append(
                CalculationGraphValidationError(
                    f"Calculation node '{node.code}' declares an empty optional dependency.",
                    node_code=node.code,
                )
            )
    return tuple(errors)


def _validate_duplicates(
    graph: CalculationGraphDefinition,
) -> tuple[CalculationGraphValidationError, ...]:
    """Detecte les doublons de codes, sorties et entrees."""
    errors: list[CalculationGraphValidationError] = []
    for code, count in _duplicates(node.code for node in graph.nodes):
        if count > 1:
            errors.append(
                CalculationGraphValidationError(
                    f"Calculation graph '{graph.graph_code}' declares duplicate node code '{code}'."
                )
            )
    for output_key, count in _duplicates(node.output_key for node in graph.nodes):
        if count > 1:
            errors.append(
                CalculationGraphValidationError(
                    f"Calculation graph '{graph.graph_code}' declares duplicate output_key "
                    f"'{output_key}'."
                )
            )
    for input_key, count in _duplicates(
        input_definition.key for input_definition in graph.required_inputs
    ):
        if count > 1:
            errors.append(
                CalculationGraphValidationError(
                    f"Calculation graph '{graph.graph_code}' declares duplicate input key "
                    f"'{input_key}'."
                )
            )
    return tuple(errors)


def _duplicates(values: object) -> tuple[tuple[str, int], ...]:
    """Retourne les valeurs non vides comptees de maniere stable."""
    counter = Counter(value for value in values if isinstance(value, str) and value.strip())
    return tuple((value, counter[value]) for value in sorted(counter))


def _validate_required_dependencies(
    graph: CalculationGraphDefinition,
    known_input_keys: set[str],
    output_to_node: dict[str, CalculationNodeDefinition],
) -> tuple[CalculationGraphValidationError, ...]:
    """Rejette les dependances obligatoires inconnues."""
    known_keys = known_input_keys | set(output_to_node)
    errors: list[CalculationGraphValidationError] = []
    for node in graph.nodes:
        for dependency in node.depends_on:
            if dependency not in known_keys:
                errors.append(
                    CalculationGraphValidationError(
                        f"Calculation node '{node.code}' depends on unknown key '{dependency}'.",
                        node_code=node.code,
                        key=dependency,
                    )
                )
    return tuple(errors)


def _topological_order(
    graph: CalculationGraphDefinition,
    output_to_node: dict[str, CalculationNodeDefinition],
) -> tuple[tuple[CalculationGraphValidationError, ...], tuple[str, ...]]:
    """Produit un ordre topologique stable ou une erreur de cycle."""
    node_by_code = {node.code: node for node in graph.nodes}
    dependencies_by_code = {
        node.code: tuple(
            output_to_node[dependency].code
            for dependency in (*node.depends_on, *node.optional_depends_on)
            if dependency in output_to_node
        )
        for node in graph.nodes
    }
    permanent: set[str] = set()
    temporary: set[str] = set()
    ordered: list[str] = []

    for node in graph.nodes:
        cycle = _visit_node(
            node.code,
            graph,
            dependencies_by_code,
            node_by_code,
            permanent,
            temporary,
            ordered,
            (),
        )
        if cycle is not None:
            return (cycle,), ()

    return (), tuple(ordered)


def _visit_node(
    node_code: str,
    graph: CalculationGraphDefinition,
    dependencies_by_code: dict[str, tuple[str, ...]],
    node_by_code: dict[str, CalculationNodeDefinition],
    permanent: set[str],
    temporary: set[str],
    ordered: list[str],
    stack: tuple[str, ...],
) -> CalculationGraphValidationError | None:
    """Parcourt les dependances d'un node en detectant les cycles."""
    if node_code in permanent:
        return None
    if node_code in temporary:
        cycle_path = (*stack[stack.index(node_code) :], node_code)
        return CalculationGraphValidationError(
            f"Calculation graph '{graph.graph_code}' contains a cycle: {' -> '.join(cycle_path)}.",
            node_code=node_code,
        )

    temporary.add(node_code)
    next_stack = (*stack, node_code)
    for dependency_code in dependencies_by_code[node_code]:
        cycle = _visit_node(
            dependency_code,
            graph,
            dependencies_by_code,
            node_by_code,
            permanent,
            temporary,
            ordered,
            next_stack,
        )
        if cycle is not None:
            return cycle

    temporary.remove(node_code)
    permanent.add(node_code)
    ordered.append(node_by_code[node_code].code)
    return None
