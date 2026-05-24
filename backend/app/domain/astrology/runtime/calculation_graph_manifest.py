# Contrat interne de manifeste des graphes de calcul astrologiques.
"""Modelise un manifeste inspectable pour les graphes de calcul runtime."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationInputDefinition,
    CalculationNodeDefinition,
)


class GraphCompatibilityPolicy(StrEnum):
    """Politiques de compatibilite autorisees pour comparer deux manifestes."""

    COMPATIBLE = "compatible"
    BREAKING = "breaking"


class GraphManifestDeltaKind(StrEnum):
    """Types de deltas contractuels exposes aux tests et audits internes."""

    GRAPH_IDENTITY_CHANGED = "graph_identity_changed"
    GRAPH_VERSION_CHANGED = "graph_version_changed"
    FAMILY_CHANGED = "family_changed"
    REQUIRED_INPUT_ADDED = "required_input_added"
    REQUIRED_INPUT_REMOVED = "required_input_removed"
    REQUIRED_INPUT_TYPE_CHANGED = "required_input_type_changed"
    REQUIRED_INPUT_REQUIREDNESS_CHANGED = "required_input_requiredness_changed"
    NODE_ADDED = "node_added"
    NODE_REMOVED = "node_removed"
    NODE_INPUT_ADDED = "node_input_added"
    NODE_INPUT_REMOVED = "node_input_removed"
    NODE_INPUT_TYPE_CHANGED = "node_input_type_changed"
    NODE_INPUT_REQUIREDNESS_CHANGED = "node_input_requiredness_changed"
    NODE_OPTIONAL_INPUT_ADDED = "node_optional_input_added"
    NODE_OPTIONAL_INPUT_REMOVED = "node_optional_input_removed"
    NODE_OUTPUT_CHANGED = "node_output_changed"
    NODE_OUTPUT_TYPE_CHANGED = "node_output_type_changed"
    NODE_OUTPUT_REQUIREDNESS_CHANGED = "node_output_requiredness_changed"


@dataclass(frozen=True, slots=True)
class GraphTypeDescriptor:
    """Decrit une cle de contrat et son type runtime stable."""

    key: str
    value_type: str
    required: bool = True


@dataclass(frozen=True, slots=True)
class NodeIOSchema:
    """Declare les entrees et la sortie produite par un node de calcul."""

    code: str
    input_schema: tuple[GraphTypeDescriptor, ...]
    output_schema: GraphTypeDescriptor
    depends_on: tuple[str, ...]
    optional_depends_on: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CalculationGraphManifest:
    """Contrat complet et comparable d'un graphe de calcul astrologique."""

    graph_code: str
    graph_version: str
    family_code: str
    required_inputs: tuple[GraphTypeDescriptor, ...]
    nodes: tuple[NodeIOSchema, ...]
    compatibility_policy: GraphCompatibilityPolicy


@dataclass(frozen=True, slots=True)
class GraphManifestDelta:
    """Delta deterministe entre deux manifestes."""

    kind: GraphManifestDeltaKind
    key: str
    before: str | None
    after: str | None
    classification: GraphCompatibilityPolicy


@dataclass(frozen=True, slots=True)
class GraphManifestComparison:
    """Resultat stable d'une comparaison de manifestes."""

    before_graph_code: str
    after_graph_code: str
    classification: GraphCompatibilityPolicy
    deltas: tuple[GraphManifestDelta, ...]


def build_graph_manifest_from_definition(
    graph: CalculationGraphDefinition,
    *,
    family_code: str,
    compatibility_policy: GraphCompatibilityPolicy = GraphCompatibilityPolicy.COMPATIBLE,
) -> CalculationGraphManifest:
    """Construit un manifeste depuis la definition executable du graphe."""
    required_inputs = tuple(
        _input_descriptor(input_definition) for input_definition in graph.required_inputs
    )
    known_descriptors: dict[str, GraphTypeDescriptor] = {
        descriptor.key: descriptor for descriptor in required_inputs
    }
    known_descriptors.update(
        {node.output_key: _node_output_descriptor(node) for node in graph.nodes}
    )
    nodes: list[NodeIOSchema] = []

    for node in graph.nodes:
        input_schema = tuple(
            known_descriptors.get(dependency, _unknown_dependency_descriptor(dependency))
            for dependency in node.depends_on
        )
        output_schema = known_descriptors[node.output_key]
        nodes.append(
            NodeIOSchema(
                code=node.code,
                input_schema=input_schema,
                output_schema=output_schema,
                depends_on=node.depends_on,
                optional_depends_on=node.optional_depends_on,
            )
        )

    return CalculationGraphManifest(
        graph_code=graph.graph_code,
        graph_version=graph.version,
        family_code=family_code,
        required_inputs=required_inputs,
        nodes=tuple(nodes),
        compatibility_policy=compatibility_policy,
    )


def compare_graph_manifests(
    before: CalculationGraphManifest,
    after: CalculationGraphManifest,
) -> GraphManifestComparison:
    """Compare deux manifestes et classe les deltas contractuels."""
    deltas = [
        *_compare_identity(before, after),
        *_compare_required_inputs(before, after),
        *_compare_nodes(before, after),
    ]
    classification = (
        GraphCompatibilityPolicy.BREAKING
        if any(delta.classification == GraphCompatibilityPolicy.BREAKING for delta in deltas)
        else GraphCompatibilityPolicy.COMPATIBLE
    )
    return GraphManifestComparison(
        before_graph_code=before.graph_code,
        after_graph_code=after.graph_code,
        classification=classification,
        deltas=tuple(deltas),
    )


def manifest_to_dict(manifest: CalculationGraphManifest) -> dict[str, object]:
    """Expose un dictionnaire stable pour les preuves JSON internes."""
    return {
        "graph_code": manifest.graph_code,
        "graph_version": manifest.graph_version,
        "family_code": manifest.family_code,
        "required_inputs": [
            _descriptor_to_dict(descriptor) for descriptor in manifest.required_inputs
        ],
        "nodes": [
            {
                "code": node.code,
                "input_schema": [
                    _descriptor_to_dict(descriptor) for descriptor in node.input_schema
                ],
                "output_schema": _descriptor_to_dict(node.output_schema),
                "depends_on": list(node.depends_on),
                "optional_depends_on": list(node.optional_depends_on),
            }
            for node in manifest.nodes
        ],
        "compatibility_policy": manifest.compatibility_policy.value,
    }


def _input_descriptor(input_definition: CalculationInputDefinition) -> GraphTypeDescriptor:
    """Convertit une entree de graphe en type descriptor de manifeste."""
    return GraphTypeDescriptor(
        key=input_definition.key,
        value_type=input_definition.value_type,
        required=input_definition.required,
    )


def _unknown_dependency_descriptor(key: str) -> GraphTypeDescriptor:
    """Marque une dependance non resolue pour que le validator l'echec explicitement."""
    return GraphTypeDescriptor(key=key, value_type="", required=True)


def _node_output_descriptor(node: CalculationNodeDefinition) -> GraphTypeDescriptor:
    """Produit un type descriptor stable derive du node proprietaire."""
    return GraphTypeDescriptor(
        key=node.output_key,
        value_type=f"{node.code}.output",
        required=True,
    )


def _compare_identity(
    before: CalculationGraphManifest,
    after: CalculationGraphManifest,
) -> tuple[GraphManifestDelta, ...]:
    """Compare les champs d'identite globale du manifeste."""
    deltas: list[GraphManifestDelta] = []
    if before.graph_code != after.graph_code:
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.GRAPH_IDENTITY_CHANGED,
                "graph_code",
                before.graph_code,
                after.graph_code,
            )
        )
    if before.graph_version != after.graph_version:
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.GRAPH_VERSION_CHANGED,
                "graph_version",
                before.graph_version,
                after.graph_version,
            )
        )
    if before.family_code != after.family_code:
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.FAMILY_CHANGED,
                "family_code",
                before.family_code,
                after.family_code,
            )
        )
    return tuple(deltas)


def _compare_required_inputs(
    before: CalculationGraphManifest,
    after: CalculationGraphManifest,
) -> tuple[GraphManifestDelta, ...]:
    """Compare les entrees globales obligatoires."""
    before_inputs = _descriptors_by_key(before.required_inputs)
    after_inputs = _descriptors_by_key(after.required_inputs)
    deltas: list[GraphManifestDelta] = []

    for key in sorted(set(before_inputs) - set(after_inputs)):
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.REQUIRED_INPUT_REMOVED,
                key,
                before_inputs[key].value_type,
                None,
            )
        )
    for key in sorted(set(after_inputs) - set(before_inputs)):
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.REQUIRED_INPUT_ADDED,
                key,
                None,
                after_inputs[key].value_type,
            )
        )
    for key in sorted(set(before_inputs) & set(after_inputs)):
        if before_inputs[key].value_type != after_inputs[key].value_type:
            deltas.append(
                _breaking_delta(
                    GraphManifestDeltaKind.REQUIRED_INPUT_TYPE_CHANGED,
                    key,
                    before_inputs[key].value_type,
                    after_inputs[key].value_type,
                )
            )
        if before_inputs[key].required != after_inputs[key].required:
            deltas.append(
                _breaking_delta(
                    GraphManifestDeltaKind.REQUIRED_INPUT_REQUIREDNESS_CHANGED,
                    key,
                    str(before_inputs[key].required),
                    str(after_inputs[key].required),
                )
            )
    return tuple(deltas)


def _compare_nodes(
    before: CalculationGraphManifest,
    after: CalculationGraphManifest,
) -> tuple[GraphManifestDelta, ...]:
    """Compare les nodes et leurs schemas IO."""
    before_nodes = {node.code: node for node in before.nodes}
    after_nodes = {node.code: node for node in after.nodes}
    deltas: list[GraphManifestDelta] = []

    for code in sorted(set(before_nodes) - set(after_nodes)):
        deltas.append(_breaking_delta(GraphManifestDeltaKind.NODE_REMOVED, code, code, None))
    for code in sorted(set(after_nodes) - set(before_nodes)):
        deltas.append(
            GraphManifestDelta(
                kind=GraphManifestDeltaKind.NODE_ADDED,
                key=code,
                before=None,
                after=code,
                classification=GraphCompatibilityPolicy.COMPATIBLE,
            )
        )
    for code in sorted(set(before_nodes) & set(after_nodes)):
        deltas.extend(_compare_node_io(before_nodes[code], after_nodes[code]))
    return tuple(deltas)


def _compare_node_io(before: NodeIOSchema, after: NodeIOSchema) -> tuple[GraphManifestDelta, ...]:
    """Compare le schema d'un node conserve."""
    deltas: list[GraphManifestDelta] = []
    if before.output_schema.key != after.output_schema.key:
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.NODE_OUTPUT_CHANGED,
                before.code,
                before.output_schema.key,
                after.output_schema.key,
            )
        )
    if before.output_schema.value_type != after.output_schema.value_type:
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.NODE_OUTPUT_TYPE_CHANGED,
                before.output_schema.key,
                before.output_schema.value_type,
                after.output_schema.value_type,
            )
        )
    if before.output_schema.required != after.output_schema.required:
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.NODE_OUTPUT_REQUIREDNESS_CHANGED,
                before.output_schema.key,
                str(before.output_schema.required),
                str(after.output_schema.required),
            )
        )
    deltas.extend(_compare_node_inputs(before, after))
    deltas.extend(_compare_node_optional_inputs(before, after))
    return tuple(deltas)


def _compare_node_inputs(
    before: NodeIOSchema, after: NodeIOSchema
) -> tuple[GraphManifestDelta, ...]:
    """Compare les entrees declarees d'un node."""
    before_inputs = _descriptors_by_key(before.input_schema)
    after_inputs = _descriptors_by_key(after.input_schema)
    deltas: list[GraphManifestDelta] = []

    for key in sorted(set(before_inputs) - set(after_inputs)):
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.NODE_INPUT_REMOVED,
                f"{before.code}:{key}",
                before_inputs[key].value_type,
                None,
            )
        )
    for key in sorted(set(after_inputs) - set(before_inputs)):
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.NODE_INPUT_ADDED,
                f"{after.code}:{key}",
                None,
                after_inputs[key].value_type,
            )
        )
    for key in sorted(set(before_inputs) & set(after_inputs)):
        if before_inputs[key].value_type != after_inputs[key].value_type:
            deltas.append(
                _breaking_delta(
                    GraphManifestDeltaKind.NODE_INPUT_TYPE_CHANGED,
                    f"{after.code}:{key}",
                    before_inputs[key].value_type,
                    after_inputs[key].value_type,
                )
            )
        if before_inputs[key].required != after_inputs[key].required:
            deltas.append(
                _breaking_delta(
                    GraphManifestDeltaKind.NODE_INPUT_REQUIREDNESS_CHANGED,
                    f"{after.code}:{key}",
                    str(before_inputs[key].required),
                    str(after_inputs[key].required),
                )
            )
    return tuple(deltas)


def _compare_node_optional_inputs(
    before: NodeIOSchema, after: NodeIOSchema
) -> tuple[GraphManifestDelta, ...]:
    """Compare les dependances optionnelles declarees par un node."""
    deltas: list[GraphManifestDelta] = []
    before_optional = set(before.optional_depends_on)
    after_optional = set(after.optional_depends_on)

    for key in sorted(before_optional - after_optional):
        deltas.append(
            _breaking_delta(
                GraphManifestDeltaKind.NODE_OPTIONAL_INPUT_REMOVED,
                f"{before.code}:{key}",
                key,
                None,
            )
        )
    for key in sorted(after_optional - before_optional):
        deltas.append(
            GraphManifestDelta(
                kind=GraphManifestDeltaKind.NODE_OPTIONAL_INPUT_ADDED,
                key=f"{after.code}:{key}",
                before=None,
                after=key,
                classification=GraphCompatibilityPolicy.COMPATIBLE,
            )
        )
    return tuple(deltas)


def _descriptors_by_key(
    descriptors: tuple[GraphTypeDescriptor, ...],
) -> dict[str, GraphTypeDescriptor]:
    """Indexe des descriptors par cle pour comparaison deterministe."""
    return {descriptor.key: descriptor for descriptor in descriptors}


def _breaking_delta(
    kind: GraphManifestDeltaKind,
    key: str,
    before: str | None,
    after: str | None,
) -> GraphManifestDelta:
    """Cree un delta classe comme rupture de contrat."""
    return GraphManifestDelta(
        kind=kind,
        key=key,
        before=before,
        after=after,
        classification=GraphCompatibilityPolicy.BREAKING,
    )


def _descriptor_to_dict(descriptor: GraphTypeDescriptor) -> dict[str, object]:
    """Serialise un descriptor sans exposer de modele public."""
    return {
        "key": descriptor.key,
        "value_type": descriptor.value_type,
        "required": descriptor.required,
    }
