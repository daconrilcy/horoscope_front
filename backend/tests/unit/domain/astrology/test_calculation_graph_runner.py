# Tests du runner des graphes de calcul astrologiques runtime.
"""Verifie execution, cache, provenance et garde-fous du runner CS-227."""

from __future__ import annotations

from pathlib import Path

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationInputDefinition,
    CalculationNodeDefinition,
    CalculationNodeStatus,
)
from app.domain.astrology.runtime.calculation_graph_runner import (
    CalculationGraphContext,
    CalculationGraphRunner,
    CalculationNodeRegistry,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
RUNNER_MODULE = REPO_ROOT / "app/domain/astrology/runtime/calculation_graph_runner.py"


def test_linear_graph_executes_in_topological_order_and_collects_outputs() -> None:
    """Un graphe lineaire valide s'execute dans l'ordre topologique."""
    calls: list[str] = []
    graph = _graph(
        _node("double", "double_value", ("seed",), "double"),
        _node("label", "label", ("double_value",), "label"),
    )
    runner = CalculationGraphRunner(
        CalculationNodeRegistry(
            {
                "double": lambda context: _record(
                    calls,
                    "double",
                    context.get_required("seed") * 2,
                ),
                "label": lambda context: _record(
                    calls,
                    "label",
                    f"value={context.get_required('double_value')}",
                ),
            }
        )
    )

    result = runner.run(graph, CalculationGraphContext({"seed": 21}))

    assert result.success is True
    assert calls == ["double", "label"]
    assert result.execution_order == ("double", "label")
    assert result.outputs == {"double_value": 42, "label": "value=42"}
    assert result.execution_trace is not None
    assert tuple(node.code for node in result.execution_trace.nodes) == ("double", "label")
    assert tuple(node.status for node in result.node_results) == (
        CalculationNodeStatus.EXECUTED,
        CalculationNodeStatus.EXECUTED,
    )


def test_convergent_graph_reuses_upstream_outputs() -> None:
    """Un graphe convergent consomme les sorties amont declarees."""
    graph = _graph(
        _node("left", "left_value", ("seed",), "left"),
        _node("right", "right_value", ("seed",), "right"),
        _node("merge", "merged", ("left_value", "right_value"), "merge"),
    )
    runner = CalculationGraphRunner(
        CalculationNodeRegistry(
            {
                "left": lambda context: context.get_required("seed") + 1,
                "right": lambda context: context.get_required("seed") + 2,
                "merge": lambda context: (
                    context.get_required("left_value"),
                    context.get_required("right_value"),
                ),
            }
        )
    )

    result = runner.run(graph, CalculationGraphContext({"seed": 10}))

    assert result.success is True
    assert result.execution_order == ("left", "right", "merge")
    assert result.outputs["merged"] == (11, 12)


def test_invalid_graph_is_validated_before_any_calculator_runs() -> None:
    """Un graphe invalide retourne les erreurs sans appeler de calculateur."""
    calls: list[str] = []
    graph = CalculationGraphDefinition(
        graph_code="invalid",
        version="1",
        nodes=(_node("broken", "broken_output", ("unknown_input",), "broken"),),
    )
    runner = CalculationGraphRunner(
        CalculationNodeRegistry({"broken": lambda context: _record(calls, "broken", None)})
    )

    result = runner.run(graph, CalculationGraphContext({}))

    assert result.success is False
    assert calls == []
    assert result.execution_order == ()
    assert "depends on unknown key 'unknown_input'" in result.errors[0].message


def test_missing_required_runtime_input_has_stable_error() -> None:
    """Une entree declaree mais absente du contexte produit un message stable."""
    graph = CalculationGraphDefinition(
        graph_code="runtime_missing",
        version="1",
        required_inputs=(CalculationInputDefinition("seed", "int"),),
        nodes=(_node("double", "double_value", ("seed",), "double"),),
    )
    runner = CalculationGraphRunner(
        CalculationNodeRegistry({"double": lambda context: context.get_required("seed")})
    )

    result = runner.run(graph, CalculationGraphContext({}))

    assert result.success is False
    assert result.errors[0].message == "Calculation node 'double' missing required input 'seed'."
    assert result.node_results[0].status == CalculationNodeStatus.FAILED


def test_unknown_calculator_has_stable_error() -> None:
    """Un calculateur absent du registry est signale sans resolution magique."""
    graph = _graph(_node("double", "double_value", ("seed",), "missing_calculator"))
    runner = CalculationGraphRunner(CalculationNodeRegistry({}))

    result = runner.run(graph, CalculationGraphContext({"seed": 3}))

    assert result.success is False
    assert (
        result.errors[0].message
        == "Calculation node 'double' uses unknown calculator 'missing_calculator'."
    )


def test_failing_calculator_has_stable_error() -> None:
    """Une exception de calculateur reste encapsulee dans le resultat runtime."""

    def fail(_context: CalculationGraphContext) -> object:
        """Declenche une erreur factice de calcul."""
        raise ValueError("boom")

    graph = _graph(_node("explode", "value", ("seed",), "explode"))
    runner = CalculationGraphRunner(CalculationNodeRegistry({"explode": fail}))

    result = runner.run(graph, CalculationGraphContext({"seed": 1}))

    assert result.success is False
    assert (
        result.errors[0].message == "Calculation node 'explode' calculator 'explode' failed: boom."
    )
    assert result.node_results[0].error == result.errors[0]


def test_cache_is_local_to_one_run_and_initial_context_is_not_mutated() -> None:
    """Un output deja present evite le recalcul sans polluer l'appel suivant."""
    calls: list[str] = []
    graph = _graph(_node("double", "double_value", ("seed",), "double"))
    runner = CalculationGraphRunner(
        CalculationNodeRegistry(
            {"double": lambda context: _record(calls, "double", context.get_required("seed") * 2)}
        )
    )
    initial_values = {"seed": 4, "double_value": 99}

    cached = runner.run(graph, CalculationGraphContext(initial_values))
    fresh = runner.run(graph, CalculationGraphContext({"seed": 4}))

    assert cached.success is True
    assert cached.cache_hits == ("double",)
    assert cached.node_results[0].cache_hit is True
    assert cached.outputs["double_value"] == 99
    assert fresh.outputs["double_value"] == 8
    assert calls == ["double"]
    assert initial_values == {"seed": 4, "double_value": 99}


def test_provenance_exposes_node_inputs_output_and_calculator() -> None:
    """La provenance minimale est disponible par code de node."""
    graph = _graph(_node("double", "double_value", ("seed",), "double"))
    runner = CalculationGraphRunner(
        CalculationNodeRegistry({"double": lambda context: context.get_required("seed") * 2})
    )

    result = runner.run(graph, CalculationGraphContext({"seed": 5}))

    assert result.provenance["double"] == {
        "node_code": "double",
        "input_keys": ("seed",),
        "output_key": "double_value",
        "output": 10,
        "calculator": "double",
    }


def test_runner_source_rejects_dynamic_lookup_and_global_cache_tokens() -> None:
    """Le runner ne contient ni import dynamique ni cache global persistant."""
    source = RUNNER_MODULE.read_text(encoding="utf-8")

    forbidden_tokens = (
        "import" + "lib",
        "eval" + "(",
        "globals" + "(",
        "network" + "x",
        "i" + "graph",
        "graph" + "lib",
        "cel" + "ery",
        "pre" + "fect",
        "air" + "flow",
        "global" + "_cache",
        "persistent" + "_cache",
    )
    assert not any(token in source for token in forbidden_tokens)


def _graph(*nodes: CalculationNodeDefinition) -> CalculationGraphDefinition:
    """Cree un graphe de test avec une entree seed declaree."""
    return CalculationGraphDefinition(
        graph_code="fake_graph",
        version="1",
        required_inputs=(CalculationInputDefinition("seed", "int"),),
        nodes=nodes,
    )


def _node(
    code: str,
    output_key: str,
    depends_on: tuple[str, ...],
    calculator: str,
) -> CalculationNodeDefinition:
    """Cree un node factice pour les tests du runner."""
    return CalculationNodeDefinition(
        code=code,
        output_key=output_key,
        depends_on=depends_on,
        calculator=calculator,
    )


def _record(calls: list[str], name: str, value: object) -> object:
    """Enregistre un appel de calculateur factice puis retourne sa valeur."""
    calls.append(name)
    return value
