# Execution Brief

## Story

- Story key: `stabilize-transit-performance-benchmark`
- Source: `_condamad/stories/stabilize-transit-performance-benchmark/00-story.md`
- Objective: stabiliser `test_v3_layers_performance_benchmark` sans supprimer le benchmark strict.

## Boundaries

- Modify only the V3 transit performance test and CONDAMAD evidence unless validation discovers a story-related blocker.
- Do not change `TARGET_BUDGET_MS` constants.
- Do not change V3 prediction business behavior.
- Do not add benchmark dependencies or a new framework.

## Done Conditions

- Standard pytest path is not gated by raw wall-clock assertions.
- Diagnostics and sample counts remain asserted in standard pytest.
- Strict benchmark remains opt-in via `RUN_PERF_BENCHMARKS=1`.
- Reintroduction guard and scan evidence are recorded.
- Required backend checks pass with the venv active.
