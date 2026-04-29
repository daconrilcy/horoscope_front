# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `stabilize-transit-performance-benchmark`
- Source story: `_condamad/stories/stabilize-transit-performance-benchmark/00-story.md`
- Capsule path: `_condamad/stories/stabilize-transit-performance-benchmark`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing `M backend/app/tests/unit/test_backend_test_topology.py`; untracked `_condamad` audit/story directories including this story.
- Pre-existing dirty files left untouched: `backend/app/tests/unit/test_backend_test_topology.py`, `_condamad/audits/backend-tests/2026-04-29-1510/`, `_condamad/stories/classify-backend-ops-quality-tests/`, `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/`, `_condamad/stories/guard-backend-pytest-test-roots/`, `_condamad/stories/replace-deprecated-llm-narrator-tests/`.
- AGENTS.md files considered: `AGENTS.md`.
- Regression guardrails considered: `RG-010`, `RG-014`.
- Capsule generated: yes; the helper produced a title-derived duplicate first, then story-specific generated files were created in the requested capsule and the duplicate was removed.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present and task/status metadata updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 covered. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and searches listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Required commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `test_v3_layers_performance_benchmark` gates strict duration assertions behind `if _run_perf_benchmarks()`; `test_v3_performance_wall_clock_budget_assertions_are_opt_in` scans AST for strict `< TARGET_BUDGET_MS` assertions outside that guard. | `pytest -q app/tests/unit/test_transit_performance.py` PASS; scan hits at lines 138-139 classified as opt-in only. | PASS | Standard pytest no longer fails on raw wall-clock budget comparisons. |
| AC2 | Standard path still asserts `budget_target_ms` and `sample_count` for transit and activation; aggregation duration remains measured without a budget gate. | `pytest -q app/tests/unit/test_transit_performance.py` PASS without `RUN_PERF_BENCHMARKS`. | PASS | Diagnostics remain deterministic. |
| AC3 | Added exact opt-in environment switch `RUN_PERF_BENCHMARKS=1`; no unconditional skip. | `$env:RUN_PERF_BENCHMARKS='1'; pytest -q app/tests/unit/test_transit_performance.py; Remove-Item Env:RUN_PERF_BENCHMARKS` PASS. | PASS | Strict benchmark remains executable voluntarily. |
| AC4 | No builder budget constants changed. | `rg -n "TARGET_BUDGET_MS = " app/prediction` shows transit `100.0`, activation `50.0`, impulse `50.0`. | PASS | No budget was raised or hidden. |
| AC5 | New guard test is non-trivial and collected; no topology config touched. | `pytest -q app/tests/unit/test_backend_noop_tests.py` PASS; `pytest --collect-only -q --ignore=.tmp-pytest` PASS; `ruff check .` PASS; full `pytest -q` PASS. | PASS | `RG-010` and `RG-014` evidence satisfied. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/tests/unit/test_transit_performance.py` | modified | Gate strict wall-clock assertions behind `RUN_PERF_BENCHMARKS=1`, keep diagnostics assertions, add AST reintroduction guard. | AC1-AC3, AC5 |
| `_condamad/stories/stabilize-transit-performance-benchmark/00-story.md` | modified | Mark story status/tasks ready for review. | AC1-AC5 |
| `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-before.md` | added | Persist baseline test structure, budget constants, and isolated benchmark result. | AC1, AC3, AC4 |
| `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-after.md` | added | Persist final targeted validation and scan classification. | AC1-AC4 |
| `_condamad/stories/stabilize-transit-performance-benchmark/generated/*.md` | added | CONDAMAD execution brief, traceability, validation plan, guardrails, dev log, and final evidence. | AC1-AC5 |

Pre-existing dirty file not changed by this story: `backend/app/tests/unit/test_backend_test_topology.py`.

## Files deleted

None.

## Tests added or updated

- Updated `backend/app/tests/unit/test_transit_performance.py`.
- Added test: `test_v3_performance_wall_clock_budget_assertions_are_opt_in`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial dirty state captured; Git warned on unreadable pytest temp folders. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\stabilize-transit-performance-benchmark\00-story.md` | repo root, venv active | PASS | 0 | Helper generated a duplicate title-derived capsule; replaced with story-specific generated files in requested capsule. |
| `pytest -q app/tests/unit/test_transit_performance.py::test_v3_layers_performance_benchmark` | `backend/`, venv active | PASS | 0 | Baseline isolated benchmark passed: `1 passed in 0.38s`. |
| `rg -n "assert dur_.*< .*TARGET_BUDGET_MS\|TARGET_BUDGET_MS = " backend\app\tests\unit\test_transit_performance.py backend\app\prediction` | repo root | PASS | 0 | Baseline scan showed standard-path strict assertions and unchanged budgets. |
| `pytest -q app/tests/unit/test_transit_performance.py` | `backend/`, venv active | FAIL | 1 | First guard attempt overmatched deterministic `budget_target_ms` equality assertions; implementation was corrected. |
| `pytest -q app/tests/unit/test_transit_performance.py` | `backend/`, venv active | PASS | 0 | `2 passed in 0.48s`. |
| `$env:RUN_PERF_BENCHMARKS='1'; pytest -q app/tests/unit/test_transit_performance.py; Remove-Item Env:RUN_PERF_BENCHMARKS` | `backend/`, venv active | PASS | 0 | `2 passed in 0.48s`; strict benchmark path executed. |
| `pytest -q app/tests/unit/test_backend_noop_tests.py` | `backend/`, venv active | PASS | 0 | `3 passed in 2.82s`. |
| `ruff format .` | `backend/`, venv active | PASS | 0 | `1242 files left unchanged`. |
| `ruff check .` | `backend/`, venv active | FAIL | 1 | First run found unused `dur_agg`; fixed by retaining a non-budget duration sanity assertion. |
| `ruff check .` | `backend/`, venv active | PASS | 0 | All checks passed. |
| `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/`, venv active | PASS | 0 | `3491 tests collected in 4.77s`. |
| `rg -n "assert dur_.*< .*TARGET_BUDGET_MS" app/tests/unit/test_transit_performance.py` | `backend/` | PASS | 0 | Hits only at lines 138-139 inside `if _run_perf_benchmarks()`. |
| `rg -n "TARGET_BUDGET_MS = " app/prediction` | `backend/` | PASS | 0 | Budgets unchanged: impulse `50.0`, activation `50.0`, transit `100.0`. |
| `pytest -q` | `backend/`, venv active | BLOCKED | 124 | First full-suite run timed out after 10 minutes without failure output. |
| `pytest -q` | `backend/`, venv active | PASS | 0 | `3479 passed, 12 skipped in 822.24s (0:13:42)`. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\stabilize-transit-performance-benchmark` | repo root, venv active | PASS | 0 | CONDAMAD validation passed. |
| `git diff --stat` | repo root | PASS | 0 | Tracked diff shows this story test plus pre-existing topology diff; untracked story files are under this capsule. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; CRLF warnings only. |
| `git status --short` | repo root | PASS | 0 | Final status recorded below; Git warned on unreadable temp folders. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Local app startup | no | Story changes backend tests/evidence only; no API runtime, frontend, dependency, or app startup path changed. | Startup regressions outside the touched surface would not be caught by this story. | Backend lint, targeted tests, collect-only, and full `pytest -q` passed. |

## DRY / No Legacy evidence

- No duplicate benchmark test file, benchmark framework, compatibility shim, alias, fallback, or re-export was introduced.
- Allowed exception is exact and explicit: `RUN_PERF_BENCHMARKS=1`.
- Strict budget assertions remain present only inside the opt-in block and are protected by AST guard.
- Budget constants were not raised: transit remains `100.0`, activation remains `50.0`.
- No unconditional `pytest.skip`, `pass`, or `assert True` was added.

## Diff review

- Story-owned tracked diff: `backend/app/tests/unit/test_transit_performance.py`.
- Story-owned untracked capsule: `_condamad/stories/stabilize-transit-performance-benchmark/`.
- Pre-existing dirty tracked diff remains visible in `backend/app/tests/unit/test_backend_test_topology.py`; it was not edited for this story.
- `git diff --check`: PASS with CRLF warnings only.

## Final worktree status

```text
 M backend/app/tests/unit/test_backend_test_topology.py
 M backend/app/tests/unit/test_transit_performance.py
?? _condamad/audits/backend-tests/2026-04-29-1510/
?? _condamad/stories/classify-backend-ops-quality-tests/
?? _condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/
?? _condamad/stories/guard-backend-pytest-test-roots/
?? _condamad/stories/replace-deprecated-llm-narrator-tests/
?? _condamad/stories/stabilize-transit-performance-benchmark/
```

`git status --short` also emitted permission warnings for unreadable pytest temp directories under `.codex-artifacts/` and `artifacts/`; those directories were not modified.

## Remaining risks

- None identified for the story scope.
- The wall-clock sensitivity of the strict benchmark is not a remaining risk for the standard suite: it is intentionally isolated behind the explicit opt-in command `RUN_PERF_BENCHMARKS=1`.

## Suggested reviewer focus

- Review the AST guard shape in `test_v3_performance_wall_clock_budget_assertions_are_opt_in`.
- Confirm the env var opt-in behavior is the desired permanent exception for strict V3 wall-clock budgets.
