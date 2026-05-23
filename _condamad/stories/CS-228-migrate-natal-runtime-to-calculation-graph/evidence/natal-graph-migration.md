# CS-228 Natal Graph Migration Proof

## Runtime Path

- Facade: `backend/app/domain/astrology/natal_calculation.py::build_natal_result`.
- Graph definition: `backend/app/domain/astrology/runtime/natal_calculation_graph.py::build_natal_calculation_graph_definition`.
- Runner: `backend/app/domain/astrology/runtime/calculation_graph_runner.py::CalculationGraphRunner`.
- Registry: `backend/app/domain/astrology/runtime/natal_calculation_registry.py::build_natal_calculation_node_registry`.
- Adapters: `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`.
- Assembler: `backend/app/domain/astrology/runtime/natal_result_assembler.py::NatalResultAssembler`.

## Compatibility

- `chart_objects` remains internal and excluded from public JSON/schema.
- Historical projections (`planet_positions`, `houses`, `aspects`, `dignities`, `advanced_conditions`) remain available on `NatalResult`.
- Node failure propagation includes the failing node code through `NatalCalculationError.details["node_code"]`.
- Existing monkeypatch test seams for natal calculators are preserved as controlled module aliases, while the runtime path uses graph adapters.

## Guardrails

- No new external dependency.
- No frontend change.
- No DB or migration change.
- No public route/OpenAPI change.
- No legacy projection is consumed as a graph calculation source.
