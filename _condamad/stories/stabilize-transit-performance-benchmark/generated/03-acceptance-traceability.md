# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Standard pytest is not gated by raw wall-clock assertions. | Move strict duration assertions behind `RUN_PERF_BENCHMARKS=1`; add AST guard. | `pytest -q app/tests/unit/test_transit_performance.py`; budget assertion scan classified. | PASS |
| AC2 | Standard test still validates V3 performance diagnostics. | Keep `budget_target_ms` and `sample_count` assertions in the standard path. | Targeted pytest passes without `RUN_PERF_BENCHMARKS`. | PASS |
| AC3 | Strict wall-clock benchmark remains opt-in. | Add explicit env-gated strict assertions. | `$env:RUN_PERF_BENCHMARKS='1'; pytest -q app/tests/unit/test_transit_performance.py`. | PASS |
| AC4 | Performance budgets are not raised or hidden to pass tests. | Leave builder budget constants unchanged. | `rg -n "TARGET_BUDGET_MS = " app/prediction`. | PASS |
| AC5 | Backend regression guardrails remain intact. | No topology or no-op guard behavior changed; new test is non-trivial. | `pytest -q app/tests/unit/test_backend_noop_tests.py`, collect-only, `ruff check .`. | PASS |
