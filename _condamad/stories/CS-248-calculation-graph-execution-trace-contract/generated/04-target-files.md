# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Search evidence

- Story and brief source read.
- Runner, graph contracts, natal graph, runner tests and API neutrality tests read.
- Scoped guardrails resolved from story IDs: RG-002, RG-003, RG-010.

## Modified files

- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/**`
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/generated/**`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `frontend/src/**`: not modified.
- `backend/app/api/**`: not modified.
- `backend/migrations/**`: not modified.
- DB models and persistence adapters: not modified.
