# Tests du contrat interne de trace des graphes de calcul astrologiques.
"""Verifie la trace CS-248, sa redaction et sa separation du replay."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationInputDefinition,
    CalculationNodeDefinition,
)
from app.domain.astrology.runtime.calculation_graph_execution_trace import (
    EXECUTION_TRACE_VERSION,
    TRACE_REDACTION_POLICY,
    CalculationTraceCacheStatus,
    CalculationTraceErrorKind,
    execution_trace_to_dict,
)
from app.domain.astrology.runtime.calculation_graph_runner import (
    CalculationGraphContext,
    CalculationGraphRunner,
    CalculationNodeRegistry,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
TRACE_MODULE = REPO_ROOT / "app/domain/astrology/runtime/calculation_graph_execution_trace.py"


def test_successful_graph_run_produces_ordered_redacted_execution_trace() -> None:
    """Un run nominal expose l'ordre, les cles et les references sans payload brut."""
    graph = _graph(
        _node("double", "double_value", ("seed",), "double"),
        _node("label", "label", ("double_value",), "label"),
    )
    runner = CalculationGraphRunner(
        CalculationNodeRegistry(
            {
                "double": lambda context: {"secret": context.get_required("seed") * 2},
                "label": lambda context: f"value={context.get_required('double_value')}",
            }
        )
    )

    result = runner.run(graph, CalculationGraphContext({"seed": "sensitive"}), run_id="run-1")
    trace = result.execution_trace

    assert trace is not None
    assert trace.version == EXECUTION_TRACE_VERSION
    assert trace.graph_code == "fake_graph"
    assert trace.graph_version == "2026.05"
    assert trace.run_id == "run-1"
    assert trace.redaction_policy == TRACE_REDACTION_POLICY
    assert tuple(node.code for node in trace.nodes) == ("double", "label")
    assert trace.nodes[0].input_keys == ("seed",)
    assert trace.nodes[0].output_keys == ("double_value",)
    assert trace.nodes[0].duration_ms is not None
    assert trace.nodes[0].provenance_ref == "provenance:double"
    assert trace.provenance_refs == ("provenance:double", "provenance:label")

    trace_payload = execution_trace_to_dict(trace)
    assert "sensitive" not in str(trace_payload)
    assert "secret" not in str(trace_payload)


def test_failed_node_trace_exposes_normalized_error_kind_without_cause_object() -> None:
    """Un echec de calculateur reste exploitable sans exposer l'exception brute."""

    def fail(_context: CalculationGraphContext) -> object:
        """Declenche une erreur factice contenant un secret."""
        raise RuntimeError("secret-cause")

    graph = _graph(_node("explode", "value", ("seed",), "explode"))
    runner = CalculationGraphRunner(CalculationNodeRegistry({"explode": fail}))

    result = runner.run(graph, CalculationGraphContext({"seed": "raw-seed"}))
    trace = result.execution_trace

    assert trace is not None
    assert result.success is False
    assert trace.nodes[0].code == "explode"
    assert trace.nodes[0].error_kind == CalculationTraceErrorKind.CALCULATOR_FAILURE
    assert trace.nodes[0].provenance_ref is None
    assert "secret-cause" not in str(execution_trace_to_dict(trace))
    assert "raw-seed" not in str(execution_trace_to_dict(trace))


def test_cache_hit_trace_exposes_hit_state_without_cached_value() -> None:
    """Un cache hit signale l'etat du cache sans recopier la valeur servie."""
    graph = _graph(_node("double", "double_value", ("seed",), "double"))
    runner = CalculationGraphRunner(
        CalculationNodeRegistry({"double": lambda context: context.get_required("seed") * 2})
    )

    result = runner.run(
        graph,
        CalculationGraphContext({"seed": 4, "double_value": "cached-secret"}),
    )
    trace = result.execution_trace

    assert trace is not None
    assert trace.nodes[0].cache_status == CalculationTraceCacheStatus.HIT
    assert trace.nodes[0].output_keys == ("double_value",)
    assert "cached-secret" not in str(execution_trace_to_dict(trace))


def test_missing_input_trace_uses_input_key_not_payload_value() -> None:
    """Une dependance runtime absente est normalisee avec la cle fautive."""
    graph = CalculationGraphDefinition(
        graph_code="missing_graph",
        version="1",
        required_inputs=(CalculationInputDefinition("seed", "int"),),
        nodes=(_node("double", "double_value", ("seed",), "double"),),
    )
    runner = CalculationGraphRunner(
        CalculationNodeRegistry({"double": lambda context: context.get_required("seed")})
    )

    result = runner.run(graph, CalculationGraphContext({}))
    trace = result.execution_trace

    assert trace is not None
    assert trace.nodes[0].error_kind == CalculationTraceErrorKind.MISSING_INPUT
    assert trace.nodes[0].input_keys == ("seed",)
    assert trace.nodes[0].output_keys == ("double_value",)


def test_trace_contract_keeps_trace_provenance_and_replay_terms_distinct() -> None:
    """Le module nomme explicitement les contrats sans fournir de replay snapshot."""
    graph = _graph(_node("double", "double_value", ("seed",), "double"))
    runner = CalculationGraphRunner(
        CalculationNodeRegistry({"double": lambda context: context.get_required("seed") * 2})
    )

    result = runner.run(graph, CalculationGraphContext({"seed": 2}))
    trace = result.execution_trace

    assert trace is not None
    payload = execution_trace_to_dict(trace)
    assert set(payload["contract_note"]) == {"trace", "provenance", "replay_snapshot"}
    assert "replay_values" not in payload
    assert not hasattr(trace, "replay_snapshot")


def test_trace_module_does_not_define_raw_payload_or_replay_surfaces() -> None:
    """La source de trace ne reintroduit pas de champs de payload ou replay actif."""
    source = TRACE_MODULE.read_text(encoding="utf-8")
    trace = (
        CalculationGraphRunner(
            CalculationNodeRegistry({"double": lambda context: context.get_required("seed") * 2})
        )
        .run(
            _graph(_node("double", "double_value", ("seed",), "double")),
            CalculationGraphContext({"seed": 1}),
        )
        .execution_trace
    )

    assert trace is not None
    assert "raw_input" not in source
    assert "raw_output" not in source
    assert "replay_values" not in source
    assert "cause" not in str(asdict(trace))


def _graph(*nodes: CalculationNodeDefinition) -> CalculationGraphDefinition:
    """Cree un graphe de test avec identite stable."""
    return CalculationGraphDefinition(
        graph_code="fake_graph",
        version="2026.05",
        required_inputs=(CalculationInputDefinition("seed", "object"),),
        nodes=nodes,
    )


def _node(
    code: str,
    output_key: str,
    depends_on: tuple[str, ...],
    calculator: str,
) -> CalculationNodeDefinition:
    """Cree un node factice pour verifier la trace."""
    return CalculationNodeDefinition(
        code=code,
        output_key=output_key,
        depends_on=depends_on,
        calculator=calculator,
    )
