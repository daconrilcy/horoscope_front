# Validation interne des manifestes de graphes de calcul astrologiques.
"""Valide les schemas IO declares par les manifestes runtime."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from app.domain.astrology.runtime.calculation_graph_manifest import (
    CalculationGraphManifest,
    GraphTypeDescriptor,
    NodeIOSchema,
)


@dataclass(frozen=True, slots=True)
class GraphManifestValidationError:
    """Erreur deterministe produite par la validation d'un manifeste."""

    message: str
    node_code: str | None = None
    key: str | None = None


@dataclass(frozen=True, slots=True)
class GraphManifestValidationResult:
    """Resultat structure de validation du manifeste."""

    graph_code: str
    is_valid: bool
    errors: tuple[GraphManifestValidationError, ...]


def validate_graph_manifest(manifest: CalculationGraphManifest) -> GraphManifestValidationResult:
    """Valide un manifeste sans executer de calculateur ni exposer l'API."""
    errors: list[GraphManifestValidationError] = []
    errors.extend(_validate_manifest_identity(manifest))
    errors.extend(_validate_required_inputs(manifest.required_inputs))
    errors.extend(_validate_nodes_have_schemas(manifest.nodes))
    errors.extend(_validate_duplicate_output_keys(manifest))

    if not errors:
        known_keys = {descriptor.key for descriptor in manifest.required_inputs}
        output_keys = {node.output_schema.key for node in manifest.nodes}
        errors.extend(_validate_node_dependencies(manifest.nodes, known_keys | output_keys))

    return GraphManifestValidationResult(
        graph_code=manifest.graph_code,
        is_valid=not errors,
        errors=tuple(errors),
    )


def _validate_manifest_identity(
    manifest: CalculationGraphManifest,
) -> tuple[GraphManifestValidationError, ...]:
    """Controle les champs obligatoires du manifeste."""
    errors: list[GraphManifestValidationError] = []
    if not manifest.graph_code.strip():
        errors.append(GraphManifestValidationError("Graph manifest requires a graph_code."))
    if not manifest.graph_version.strip():
        errors.append(
            GraphManifestValidationError(
                f"Graph manifest '{manifest.graph_code}' requires a graph_version."
            )
        )
    if not manifest.family_code.strip():
        errors.append(
            GraphManifestValidationError(
                f"Graph manifest '{manifest.graph_code}' requires a family_code."
            )
        )
    return tuple(errors)


def _validate_required_inputs(
    descriptors: tuple[GraphTypeDescriptor, ...],
) -> tuple[GraphManifestValidationError, ...]:
    """Controle les descriptors d'entrees globales."""
    errors: list[GraphManifestValidationError] = []
    for descriptor in descriptors:
        errors.extend(_validate_descriptor(descriptor))
    for key, count in _duplicates(descriptor.key for descriptor in descriptors):
        if count > 1:
            errors.append(
                GraphManifestValidationError(f"Duplicate required input '{key}'.", key=key)
            )
    return tuple(errors)


def _validate_nodes_have_schemas(
    nodes: tuple[NodeIOSchema, ...],
) -> tuple[GraphManifestValidationError, ...]:
    """Rejette les nodes sans schema d'entree ou de sortie."""
    errors: list[GraphManifestValidationError] = []
    for node in nodes:
        if not node.code.strip():
            errors.append(
                GraphManifestValidationError("Graph manifest declares a node without code.")
            )
        if not node.input_schema:
            errors.append(
                GraphManifestValidationError(
                    f"Node '{node.code}' requires a non-empty input_schema.",
                    node_code=node.code,
                )
            )
        if not node.output_schema.key.strip() or not node.output_schema.value_type.strip():
            errors.append(
                GraphManifestValidationError(
                    f"Node '{node.code}' requires a complete output_schema.",
                    node_code=node.code,
                    key=node.output_schema.key,
                )
            )
        for descriptor in node.input_schema:
            for descriptor_error in _validate_descriptor(descriptor):
                errors.append(
                    GraphManifestValidationError(
                        descriptor_error.message,
                        node_code=node.code,
                        key=descriptor_error.key,
                    )
                )
    return tuple(errors)


def _validate_duplicate_output_keys(
    manifest: CalculationGraphManifest,
) -> tuple[GraphManifestValidationError, ...]:
    """Detecte les sorties dupliquees dans le manifeste."""
    errors: list[GraphManifestValidationError] = []
    for output_key, count in _duplicates(node.output_schema.key for node in manifest.nodes):
        if count > 1:
            errors.append(
                GraphManifestValidationError(
                    f"Graph manifest '{manifest.graph_code}' declares duplicate output "
                    f"'{output_key}'.",
                    key=output_key,
                )
            )
    return tuple(errors)


def _validate_node_dependencies(
    nodes: tuple[NodeIOSchema, ...],
    known_keys: set[str],
) -> tuple[GraphManifestValidationError, ...]:
    """Rejette les dependances absentes du manifeste."""
    errors: list[GraphManifestValidationError] = []
    for node in nodes:
        input_keys = {descriptor.key for descriptor in node.input_schema}
        for dependency in node.depends_on:
            if dependency not in known_keys:
                errors.append(
                    GraphManifestValidationError(
                        f"Node '{node.code}' depends on unknown key '{dependency}'.",
                        node_code=node.code,
                        key=dependency,
                    )
                )
            if dependency not in input_keys:
                errors.append(
                    GraphManifestValidationError(
                        f"Node '{node.code}' dependency '{dependency}' is absent from "
                        "input_schema.",
                        node_code=node.code,
                        key=dependency,
                    )
                )
        for dependency in node.optional_depends_on:
            if dependency not in known_keys:
                errors.append(
                    GraphManifestValidationError(
                        f"Node '{node.code}' optionally depends on unknown key '{dependency}'.",
                        node_code=node.code,
                        key=dependency,
                    )
                )
    return tuple(errors)


def _validate_descriptor(
    descriptor: GraphTypeDescriptor,
) -> tuple[GraphManifestValidationError, ...]:
    """Controle une cle typee de schema IO."""
    errors: list[GraphManifestValidationError] = []
    if not descriptor.key.strip():
        errors.append(GraphManifestValidationError("Schema descriptor requires a key."))
    if not descriptor.value_type.strip():
        errors.append(
            GraphManifestValidationError(
                f"Schema descriptor '{descriptor.key}' requires a value_type.",
                key=descriptor.key,
            )
        )
    return tuple(errors)


def _duplicates(values: object) -> tuple[tuple[str, int], ...]:
    """Retourne les valeurs dupliquees dans un ordre stable."""
    counter = Counter(value for value in values if isinstance(value, str) and value.strip())
    return tuple((value, counter[value]) for value in sorted(counter))
