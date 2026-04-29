# No Legacy / DRY Guardrails

## Forbidden

- Raising `TransitSignalBuilder.TARGET_BUDGET_MS` or `IntradayActivationBuilder.TARGET_BUDGET_MS`.
- Replacing the benchmark with `pass`, `assert True`, or unconditional `pytest.skip`.
- Adding a duplicate performance test file or benchmark framework.
- Introducing fallback behavior that silently disables the strict benchmark when explicitly requested.
- Adding compatibility shims, aliases, re-exports, or new active paths.

## Allowed Exception

| Exception | Reason | Guard |
|---|---|---|
| `RUN_PERF_BENCHMARKS=1` | Explicit opt-in for strict wall-clock benchmark. | Targeted pytest with env var plus AST guard. |

## Required Evidence

- Targeted pytest passes without env var.
- Targeted pytest passes with `RUN_PERF_BENCHMARKS=1`.
- AST guard proves strict budget assertions are under `_run_perf_benchmarks()`.
- Scan classifies any `assert dur_.*< .*TARGET_BUDGET_MS` hits.
- Budget constants scan proves budgets were not raised.
