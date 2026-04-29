# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/stabilize-transit-performance-benchmark/00-story.md`
- Status reviewed: `ready-for-review`
- Primary implementation file: `backend/app/tests/unit/test_transit_performance.py`

## Inputs reviewed

- Story contract and AC1-AC5.
- Capsule artifacts: acceptance traceability, validation plan, No Legacy / DRY guardrails, final evidence, before/after benchmark evidence.
- Shared guardrails: `_condamad/stories/regression-guardrails.md`, especially `RG-010` and `RG-014`.
- Repository diff for `backend/app/tests/unit/test_transit_performance.py`.
- Relevant builder budget constants in `backend/app/prediction`.

## Diff summary

- `backend/app/tests/unit/test_transit_performance.py` now keeps diagnostic assertions in the standard path.
- Strict wall-clock assertions for `dur_t` and `dur_a` are gated behind `RUN_PERF_BENCHMARKS=1`.
- A local AST guard test blocks strict `< TARGET_BUDGET_MS` assertions outside the opt-in guard.
- No builder budget constant was changed.
- The worktree also contains unrelated pre-existing dirty/untracked story and audit files; they were not reviewed as part of this single target.

## Review layers

- Diff integrity: PASS for the story-owned tracked diff and capsule files.
- Acceptance audit: PASS for AC1-AC5.
- Validation audit: PASS with reviewer reruns.
- DRY / No Legacy audit: PASS; no duplicate benchmark framework, no unconditional skip, no `pass`/`assert True` replacement, no budget raise.
- Regression guardrail audit: PASS for `RG-010` and `RG-014`.
- Security/data audit: no applicable runtime, API, auth, secret, DB, or frontend surface changed.

## Findings

No actionable findings.

## Acceptance audit

- AC1: PASS. Standard path no longer asserts raw wall-clock budgets; strict assertions are only inside `if _run_perf_benchmarks()`.
- AC2: PASS. Standard test still asserts `budget_target_ms` and `sample_count` for transit and activation.
- AC3: PASS. `RUN_PERF_BENCHMARKS=1` executes the strict benchmark path.
- AC4: PASS. `TARGET_BUDGET_MS` remains `100.0` for transit and `50.0` for activation.
- AC5: PASS. No-op guard, collection, lint, and full pytest passed.

## Validation audit

Reviewer commands run from repo root unless noted otherwise:

| Command | Result |
|---|---|
| `git diff --check` | PASS, CRLF warnings only |
| `rg -n "assert dur_.*< .*TARGET_BUDGET_MS\|TARGET_BUDGET_MS = \|RUN_PERF_BENCHMARKS\|pytest\.skip\|assert True\|pass$" backend/app/tests/unit/test_transit_performance.py backend/app/prediction` | PASS, story hits classified |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .` | PASS |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff check .` | PASS |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q app/tests/unit/test_transit_performance.py` | PASS, `2 passed` |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; $env:RUN_PERF_BENCHMARKS='1'; pytest -q app/tests/unit/test_transit_performance.py; Remove-Item Env:RUN_PERF_BENCHMARKS` | PASS, `2 passed` |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q app/tests/unit/test_backend_noop_tests.py` | PASS, `3 passed` |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest --collect-only -q --ignore=.tmp-pytest` | PASS, `3491 tests collected` |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q` | PASS, `3479 passed, 12 skipped in 571.09s` |

All Python commands were run after activating `.venv`.

## DRY / No Legacy audit

- No duplicate performance test file was introduced.
- No new dependency or benchmark framework was introduced.
- The opt-in exception is exact: `RUN_PERF_BENCHMARKS=1`.
- The AST guard is local and deterministic for the forbidden assertion shape in this story.
- No compatibility wrapper, alias, fallback, or re-export was introduced.

## Residual risks

- The strict wall-clock benchmark can still fail under local load when explicitly requested. That behavior is intentional and documented as the opt-in performance signal.
- The unrelated dirty file `backend/app/tests/unit/test_backend_test_topology.py` and unrelated untracked CONDAMAD folders remain outside this review target.

## Verdict

CLEAN
