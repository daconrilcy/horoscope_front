# Tests des contrats de manifeste de graphes de calcul astrologiques.
"""Verifie validation et comparaison des schemas IO de manifestes."""

from dataclasses import replace

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationInputDefinition,
    CalculationNodeDefinition,
)
from app.domain.astrology.runtime.calculation_graph_manifest import (
    CalculationGraphManifest,
    GraphCompatibilityPolicy,
    GraphManifestDeltaKind,
    GraphTypeDescriptor,
    NodeIOSchema,
    build_graph_manifest_from_definition,
    compare_graph_manifests,
)
from app.domain.astrology.runtime.calculation_graph_manifest_validator import (
    validate_graph_manifest,
)


def test_manifest_from_graph_definition_declares_node_io_schemas() -> None:
    """Le manifeste derive du graphe sans dupliquer la declaration des nodes."""
    manifest = _valid_manifest()

    assert manifest.graph_code == "natal_chart_v1"
    assert manifest.graph_version == "1"
    assert manifest.family_code == "natal_chart_v1"
    assert manifest.compatibility_policy is GraphCompatibilityPolicy.COMPATIBLE
    assert manifest.required_inputs == (
        GraphTypeDescriptor(key="julian_day", value_type="float"),
        GraphTypeDescriptor(key="coordinates", value_type="Coordinates"),
    )
    assert manifest.nodes[0].input_schema == manifest.required_inputs
    assert manifest.nodes[0].output_schema == GraphTypeDescriptor(
        key="houses_runtime",
        value_type="houses.output",
    )


def test_valid_manifest_passes_validation() -> None:
    """Un manifeste complet est accepte par le validator dedie."""
    result = validate_graph_manifest(_valid_manifest())

    assert result.is_valid is True
    assert result.errors == ()


def test_duplicate_output_key_is_rejected() -> None:
    """Deux nodes de manifeste ne peuvent pas produire la meme sortie."""
    node = _node_schema("houses", "houses_runtime", ("julian_day",))
    manifest = _manifest(
        nodes=(node, _node_schema("houses_again", "houses_runtime", ("julian_day",)))
    )

    result = validate_graph_manifest(manifest)

    assert result.is_valid is False
    assert "duplicate output 'houses_runtime'" in _messages(result)[0]


def test_unknown_required_input_is_rejected() -> None:
    """Une dependance obligatoire doit exister dans les inputs ou outputs."""
    manifest = _manifest(nodes=(_node_schema("houses", "houses_runtime", ("unknown_key",)),))

    result = validate_graph_manifest(manifest)

    assert result.is_valid is False
    assert "Node 'houses' depends on unknown key 'unknown_key'." in _messages(result)


def test_unknown_optional_input_is_rejected() -> None:
    """Une dependance optionnelle doit aussi pointer vers une cle connue."""
    node = _node_schema("houses", "houses_runtime", ("julian_day",))
    manifest = _manifest(nodes=(replace(node, optional_depends_on=("unknown_optional",)),))

    result = validate_graph_manifest(manifest)

    assert result.is_valid is False
    assert "Node 'houses' optionally depends on unknown key 'unknown_optional'." in _messages(
        result
    )


def test_missing_node_input_schema_is_rejected() -> None:
    """Un node sans schema d'entree explicite est invalide."""
    manifest = _manifest(
        nodes=(
            NodeIOSchema(
                code="houses",
                input_schema=(),
                output_schema=GraphTypeDescriptor(key="houses_runtime", value_type="houses.output"),
                depends_on=("julian_day",),
            ),
        )
    )

    result = validate_graph_manifest(manifest)

    assert result.is_valid is False
    assert "Node 'houses' requires a non-empty input_schema." in _messages(result)


def test_missing_node_output_schema_is_rejected() -> None:
    """Un node sans sortie typee explicite est invalide."""
    manifest = _manifest(
        nodes=(
            NodeIOSchema(
                code="houses",
                input_schema=(GraphTypeDescriptor(key="julian_day", value_type="float"),),
                output_schema=GraphTypeDescriptor(key="houses_runtime", value_type=""),
                depends_on=("julian_day",),
            ),
        )
    )

    result = validate_graph_manifest(manifest)

    assert result.is_valid is False
    assert "requires a complete output_schema" in _messages(result)[0]


def test_manifest_comparison_classifies_version_input_output_and_type_deltas() -> None:
    """Les deltas contractuels importants sont classes comme breaking."""
    before = _valid_manifest()
    after = replace(
        before,
        graph_version="2",
        required_inputs=(GraphTypeDescriptor(key="julian_day", value_type="Decimal"),),
        nodes=(
            NodeIOSchema(
                code="houses",
                input_schema=(GraphTypeDescriptor(key="julian_day", value_type="Decimal"),),
                output_schema=GraphTypeDescriptor(
                    key="houses_payload",
                    value_type="houses.payload",
                ),
                depends_on=("julian_day",),
            ),
        ),
    )

    comparison = compare_graph_manifests(before, after)
    kinds = {delta.kind for delta in comparison.deltas}

    assert comparison.classification is GraphCompatibilityPolicy.BREAKING
    assert GraphManifestDeltaKind.GRAPH_VERSION_CHANGED in kinds
    assert GraphManifestDeltaKind.REQUIRED_INPUT_REMOVED in kinds
    assert GraphManifestDeltaKind.REQUIRED_INPUT_TYPE_CHANGED in kinds
    assert GraphManifestDeltaKind.NODE_INPUT_REMOVED in kinds
    assert GraphManifestDeltaKind.NODE_OUTPUT_CHANGED in kinds
    assert GraphManifestDeltaKind.NODE_OUTPUT_TYPE_CHANGED in kinds


def test_manifest_comparison_classifies_optional_dependency_deltas() -> None:
    """Les dependances optionnelles sont incluses dans le contrat comparable."""
    before = _manifest(
        nodes=(
            replace(
                _node_schema("houses", "houses_runtime", ("julian_day",)),
                optional_depends_on=("coordinates",),
            ),
        )
    )
    after = _manifest(
        nodes=(
            replace(
                _node_schema("houses", "houses_runtime", ("julian_day",)),
                optional_depends_on=("locale",),
            ),
        )
    )

    comparison = compare_graph_manifests(before, after)
    deltas_by_kind = {delta.kind: delta for delta in comparison.deltas}

    assert comparison.classification is GraphCompatibilityPolicy.BREAKING
    assert (
        deltas_by_kind[GraphManifestDeltaKind.NODE_OPTIONAL_INPUT_REMOVED].classification
        is GraphCompatibilityPolicy.BREAKING
    )
    assert (
        deltas_by_kind[GraphManifestDeltaKind.NODE_OPTIONAL_INPUT_ADDED].classification
        is GraphCompatibilityPolicy.COMPATIBLE
    )


def test_manifest_comparison_classifies_requiredness_deltas() -> None:
    """La comparaison couvre tout le descripteur de type expose."""
    before = _valid_manifest()
    after = replace(
        before,
        required_inputs=(
            GraphTypeDescriptor(key="julian_day", value_type="float", required=False),
            GraphTypeDescriptor(key="coordinates", value_type="Coordinates"),
        ),
        nodes=(
            NodeIOSchema(
                code="houses",
                input_schema=(
                    GraphTypeDescriptor(key="julian_day", value_type="float", required=False),
                    GraphTypeDescriptor(key="coordinates", value_type="Coordinates"),
                ),
                output_schema=GraphTypeDescriptor(
                    key="houses_runtime",
                    value_type="houses.output",
                    required=False,
                ),
                depends_on=("julian_day", "coordinates"),
            ),
        ),
    )

    comparison = compare_graph_manifests(before, after)
    kinds = {delta.kind for delta in comparison.deltas}

    assert comparison.classification is GraphCompatibilityPolicy.BREAKING
    assert GraphManifestDeltaKind.REQUIRED_INPUT_REQUIREDNESS_CHANGED in kinds
    assert GraphManifestDeltaKind.NODE_INPUT_REQUIREDNESS_CHANGED in kinds
    assert GraphManifestDeltaKind.NODE_OUTPUT_REQUIREDNESS_CHANGED in kinds


def _valid_manifest() -> CalculationGraphManifest:
    """Construit un manifeste minimal depuis un graphe executable."""
    graph = CalculationGraphDefinition(
        graph_code="natal_chart_v1",
        version="1",
        required_inputs=(
            CalculationInputDefinition(key="julian_day", value_type="float"),
            CalculationInputDefinition(key="coordinates", value_type="Coordinates"),
        ),
        nodes=(
            CalculationNodeDefinition(
                code="houses",
                output_key="houses_runtime",
                depends_on=("julian_day", "coordinates"),
                calculator="calculate_houses",
            ),
        ),
    )
    return build_graph_manifest_from_definition(graph, family_code="natal_chart_v1")


def _manifest(nodes: tuple[NodeIOSchema, ...]) -> CalculationGraphManifest:
    """Cree un manifeste test avec des inputs globaux constants."""
    return CalculationGraphManifest(
        graph_code="natal_chart_v1",
        graph_version="1",
        family_code="natal_chart_v1",
        required_inputs=(
            GraphTypeDescriptor(key="julian_day", value_type="float"),
            GraphTypeDescriptor(key="coordinates", value_type="Coordinates"),
            GraphTypeDescriptor(key="locale", value_type="str"),
        ),
        nodes=nodes,
        compatibility_policy=GraphCompatibilityPolicy.COMPATIBLE,
    )


def _node_schema(code: str, output_key: str, depends_on: tuple[str, ...]) -> NodeIOSchema:
    """Cree un schema de node complet pour les tests invalides."""
    return NodeIOSchema(
        code=code,
        input_schema=tuple(
            GraphTypeDescriptor(key=dependency, value_type="float") for dependency in depends_on
        ),
        output_schema=GraphTypeDescriptor(key=output_key, value_type=f"{code}.output"),
        depends_on=depends_on,
    )


def _messages(result: object) -> tuple[str, ...]:
    """Expose les messages d'erreur pour assertions lisibles."""
    return tuple(error.message for error in result.errors)
