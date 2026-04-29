# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial dirty state included pre-existing tracked modification in `backend/app/tests/unit/test_backend_test_topology.py` and several untracked `_condamad` story/audit directories.
- `AGENTS.md` and `_condamad/stories/regression-guardrails.md` were read.
- Applicable guardrails: `RG-010`, `RG-014`.

## Baseline

- Targeted current benchmark passed in isolation: `1 passed in 0.38s`.
- Scan confirmed direct standard-path wall-clock assertions before implementation.

## Implementation

- Standard test path now asserts diagnostics and sample counts only.
- Strict budget assertions are gated by `RUN_PERF_BENCHMARKS=1`.
- Added AST guard test to prevent strict budget assertions outside the opt-in block.

## Validation Notes

- First run of the AST guard failed because it also matched deterministic equality assertions for `budget_target_ms`.
- The guard was narrowed to strict `< TARGET_BUDGET_MS` comparisons, matching the story risk.
