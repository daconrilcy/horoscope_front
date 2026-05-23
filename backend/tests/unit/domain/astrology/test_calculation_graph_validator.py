# Tests du validator declaratif des graphes de calcul runtime.
"""Verifie les erreurs et l'ordre topologique du graphe CS-225."""

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationInputDefinition,
    CalculationNodeDefinition,
)
from app.domain.astrology.runtime.calculation_graph_validator import (
    validate_calculation_graph_definition,
)


def test_minimal_graph_is_valid() -> None:
    """Un graphe minimal expose inputs, node et ordre topologique."""
    graph = CalculationGraphDefinition(
        graph_code="natal_chart_v1",
        version="1",
        required_inputs=(
            CalculationInputDefinition(key="julian_day", value_type="float"),
            CalculationInputDefinition(key="coordinates", value_type="Coordinates"),
            CalculationInputDefinition(key="house_system", value_type="str"),
        ),
        nodes=(
            CalculationNodeDefinition(
                code="houses",
                output_key="houses_runtime",
                depends_on=("julian_day", "coordinates", "house_system"),
                calculator="houses_runtime_builder",
            ),
        ),
    )

    result = validate_calculation_graph_definition(graph)

    assert result.is_valid is True
    assert result.errors == ()
    assert result.topological_order == ("houses",)


def test_node_without_code_is_rejected() -> None:
    """Un node sans code produit une erreur explicite."""
    result = validate_calculation_graph_definition(
        CalculationGraphDefinition(
            graph_code="natal_chart_v1",
            version="1",
            nodes=(
                CalculationNodeDefinition(
                    code="",
                    output_key="houses_runtime",
                    depends_on=(),
                    calculator="houses_runtime_builder",
                ),
            ),
        )
    )

    assert result.is_valid is False
    assert "declares a node without code" in result.errors[0].message


def test_duplicate_output_key_is_rejected() -> None:
    """Deux nodes ne peuvent pas produire la meme sortie."""
    result = validate_calculation_graph_definition(
        CalculationGraphDefinition(
            graph_code="natal_chart_v1",
            version="1",
            nodes=(
                _node("houses", "chart_objects"),
                _node("points", "chart_objects"),
            ),
        )
    )

    assert result.is_valid is False
    assert (
        "Calculation graph 'natal_chart_v1' declares duplicate output_key 'chart_objects'."
    ) in _messages(result)


def test_duplicate_node_code_is_rejected() -> None:
    """Deux nodes ne peuvent pas partager le meme code stable."""
    result = validate_calculation_graph_definition(
        CalculationGraphDefinition(
            graph_code="natal_chart_v1",
            version="1",
            nodes=(
                _node("houses", "houses_runtime"),
                _node("houses", "whole_sign_houses_runtime"),
            ),
        )
    )

    assert result.is_valid is False
    assert (
        "Calculation graph 'natal_chart_v1' declares duplicate node code 'houses'."
    ) in _messages(result)


def test_duplicate_input_key_is_rejected() -> None:
    """Deux inputs ne peuvent pas declarer la meme cle."""
    result = validate_calculation_graph_definition(
        CalculationGraphDefinition(
            graph_code="natal_chart_v1",
            version="1",
            required_inputs=(
                CalculationInputDefinition(key="julian_day", value_type="float"),
                CalculationInputDefinition(key="julian_day", value_type="Decimal"),
            ),
            nodes=(),
        )
    )

    assert result.is_valid is False
    assert (
        "Calculation graph 'natal_chart_v1' declares duplicate input key 'julian_day'."
    ) in _messages(result)


def test_unknown_required_dependency_is_rejected() -> None:
    """Une dependance obligatoire doit venir des inputs ou sorties declares."""
    result = validate_calculation_graph_definition(
        CalculationGraphDefinition(
            graph_code="natal_chart_v1",
            version="1",
            nodes=(
                CalculationNodeDefinition(
                    code="house_rulers",
                    output_key="house_rulerships_runtime",
                    depends_on=("houses",),
                    calculator="house_ruler_resolver",
                ),
            ),
        )
    )

    assert result.is_valid is False
    assert ("Calculation node 'house_rulers' depends on unknown key 'houses'.") in _messages(result)


def test_direct_cycle_is_rejected() -> None:
    """Un node ne peut pas dependre de sa propre sortie."""
    result = validate_calculation_graph_definition(
        CalculationGraphDefinition(
            graph_code="natal_chart_v1",
            version="1",
            nodes=(
                CalculationNodeDefinition(
                    code="houses",
                    output_key="houses_runtime",
                    depends_on=("houses_runtime",),
                    calculator="houses_runtime_builder",
                ),
            ),
        )
    )

    assert result.is_valid is False
    assert ("Calculation graph 'natal_chart_v1' contains a cycle: houses -> houses.") in _messages(
        result
    )


def test_indirect_cycle_is_rejected() -> None:
    """Un cycle indirect retourne un chemin deterministe."""
    result = validate_calculation_graph_definition(
        CalculationGraphDefinition(
            graph_code="natal_chart_v1",
            version="1",
            nodes=(
                CalculationNodeDefinition(
                    code="houses",
                    output_key="houses_runtime",
                    depends_on=("signature_runtime",),
                    calculator="houses_runtime_builder",
                ),
                CalculationNodeDefinition(
                    code="signature",
                    output_key="signature_runtime",
                    depends_on=("houses_runtime",),
                    calculator="chart_signature_builder",
                ),
            ),
        )
    )

    assert result.is_valid is False
    assert (
        "Calculation graph 'natal_chart_v1' contains a cycle: houses -> signature -> houses."
    ) in _messages(result)


def test_unknown_optional_dependency_does_not_block_validation() -> None:
    """Une dependance optionnelle inconnue reste inspectable sans erreur."""
    result = validate_calculation_graph_definition(
        CalculationGraphDefinition(
            graph_code="natal_chart_v1",
            version="1",
            nodes=(
                CalculationNodeDefinition(
                    code="signature",
                    output_key="signature_runtime",
                    depends_on=(),
                    optional_depends_on=("houses_runtime",),
                    calculator="chart_signature_builder",
                ),
            ),
        )
    )

    assert result.is_valid is True
    assert result.errors == ()
    assert result.topological_order == ("signature",)


def test_topological_order_is_deterministic() -> None:
    """L'ordre respecte les sorties consommees par les nodes declares."""
    graph = CalculationGraphDefinition(
        graph_code="natal_chart_v1",
        version="1",
        required_inputs=(
            CalculationInputDefinition(key="julian_day", value_type="float"),
            CalculationInputDefinition(key="coordinates", value_type="Coordinates"),
            CalculationInputDefinition(key="house_system", value_type="str"),
        ),
        nodes=(
            CalculationNodeDefinition(
                code="signature",
                output_key="signature_runtime",
                depends_on=("houses_runtime", "house_rulerships_runtime"),
                calculator="chart_signature_builder",
            ),
            CalculationNodeDefinition(
                code="house_rulers",
                output_key="house_rulerships_runtime",
                depends_on=("houses_runtime",),
                calculator="house_ruler_resolver",
            ),
            CalculationNodeDefinition(
                code="houses",
                output_key="houses_runtime",
                depends_on=("julian_day", "coordinates", "house_system"),
                calculator="houses_runtime_builder",
            ),
        ),
    )

    result = validate_calculation_graph_definition(graph)

    assert result.is_valid is True
    assert result.topological_order == ("houses", "house_rulers", "signature")


def _node(code: str, output_key: str) -> CalculationNodeDefinition:
    """Cree un node minimal pour les tests de validation."""
    return CalculationNodeDefinition(
        code=code,
        output_key=output_key,
        depends_on=(),
        calculator=f"{code}_calculator",
    )


def _messages(result: object) -> tuple[str, ...]:
    """Expose les messages d'erreur pour des assertions lisibles."""
    return tuple(error.message for error in result.errors)
