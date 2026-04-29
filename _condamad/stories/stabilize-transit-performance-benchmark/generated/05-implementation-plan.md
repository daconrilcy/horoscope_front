# Implementation Plan

## Findings

- The standard test path asserted `dur_t` and `dur_a` directly against production budgets.
- Prior evidence shows the full suite once failed at `104.02ms` for a `100ms` transit budget, while isolated rerun passed.
- Budgets are product diagnostics and must remain unchanged.

## Changes

1. Add a French module docstring and small env helper in `test_transit_performance.py`.
2. Keep timing measurement and deterministic diagnostics assertions in the standard path.
3. Gate strict duration assertions with `RUN_PERF_BENCHMARKS=1`.
4. Add an AST guard test that detects strict `< TARGET_BUDGET_MS` assertions outside the opt-in block.
5. Persist before/after benchmark evidence and final CONDAMAD traceability.

## No Legacy Stance

- No compatibility shim, fallback, alias, duplicate benchmark file, or dependency is introduced.
- The only allowed exception is the exact opt-in env var from the story: `RUN_PERF_BENCHMARKS=1`.

## Rollback

- Revert `backend/app/tests/unit/test_transit_performance.py` and the story evidence files if validation shows the opt-in guard conflicts with existing pytest behavior.
