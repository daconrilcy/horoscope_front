# Final Evidence — CS-248-calculation-graph-execution-trace-contract

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-248-calculation-graph-execution-trace-contract
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-248-calculation-graph-execution-trace-contract`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `00-story.md`
- Initial `git status --short`: dirty worktree with pre-existing CS-246/CS-247, architecture, story-status and backend changes.
- Pre-existing dirty files: left intact; CS-248 edits are scoped to runtime trace, runner hook, tests and CS-248 evidence.
- AGENTS.md files considered: root `AGENTS.md` from prompt/workspace.
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | |
| `generated/01-execution-brief.md` | yes | yes | PASS | |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC1-AC10. |
| `generated/04-target-files.md` | yes | yes | PASS | Updated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Updated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generic guardrails retained. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Runner-attached ordered `execution_trace.nodes`. | Targeted pytest PASS. | PASS | |
| AC2 | Stable `version`, `graph_code`, `graph_version`, `run_id`. | Unit tests and `trace-after.json` PASS. | PASS | |
| AC3 | `duration_ms` recorded per node trace. | Unit test PASS. | PASS | |
| AC4 | Normalized `CalculationTraceErrorKind`. | Failed calculator test PASS. | PASS | |
| AC5 | Cache hit state without cached value. | Cache trace test PASS. | PASS | |
| AC6 | Input values redacted to `input_keys`. | Secret absence tests PASS. | PASS | |
| AC7 | Output values redacted to `output_keys` and refs. | Secret/cache tests PASS. | PASS | |
| AC8 | Trace/provenance/replay separated in contract note. | Terminology test PASS. | PASS | |
| AC9 | No public API/OpenAPI exposure. | API neutrality test and python assertions PASS. | PASS | |
| AC10 | Evidence artifacts persisted. | Evidence files present and capsule validation PASS. | PASS | |

## Files changed

- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/**`
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/generated/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `condamad_validate.py _condamad\stories\CS-248-calculation-graph-execution-trace-contract` | repo root | PASS | 0 | Capsule valid. |
| `ruff format <changed files>` | repo root | PASS | 0 | Scoped formatting. |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py` | repo root | PASS | 0 | 23 passed. |
| `rg -n "ExecutionTrace\|redaction_policy\|provenance_ref" backend\app\domain\astrology\runtime backend\tests\unit\domain\astrology -g "*.py"` | repo root | PASS | 0 | Trace symbols scoped. |
| `python -B -c "from app.main import app; assert 'ExecutionTrace' not in str(app.openapi())"` | repo root | PASS | 0 | Run with `PYTHONPATH=backend`. |
| `python -B -c "from app.main import app; assert not any('execution-trace' in getattr(r, 'path', '') for r in app.routes)"` | repo root | PASS | 0 | Run with `PYTHONPATH=backend`. |
| `ruff check backend` | repo root | PASS | 0 | All checks passed. |
| `python -B -m pytest -q backend\tests` | repo root | PASS | 0 | 904 passed, 201 deselected. |
| `git diff --check` | repo root | PASS | 0 | Only line-ending warnings. |

## Commands skipped or blocked

- `rg -n "ExecutionTrace|execution-trace|replay_snapshot|raw_input|raw_output" backend\app\api frontend backend\alembic -g "*.py" -g "*.ts" -g "*.tsx"` returned existing unrelated frontend admin prompt `raw_output` and missing `backend\alembic`; compensated with targeted API/OpenAPI assertions and adjusted scan against `backend\migrations`.
- `rg -n "ExecutionTrace|CalculationGraphExecutionTrace|execution-trace|execution_trace|replay_snapshot" backend\app\api frontend backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"` returned existing unrelated LLM replay migrations; no CS-248 execution trace public exposure.

## DRY / No Legacy evidence

- One canonical trace module: `calculation_graph_execution_trace.py`.
- No frontend, API route, DB model or migration changed by CS-248.
- Trace contains keys, statuses, duration, error kinds and provenance refs only; tests assert no raw input/output/cause values.
- No replay snapshot capability implemented.

## Diff review

- `git diff --stat`: reviewed; includes pre-existing unrelated dirty files plus CS-248 changes.
- `git diff --check`: PASS with line-ending warnings only.

## Final worktree status

- Dirty worktree remains because this repo already contained unrelated CS-246/CS-247/architecture changes and untracked story brief files. CS-248 files are ready for review.

## Remaining risks

- Existing unrelated frontend admin prompt `raw_output` and LLM replay migration terms remain outside CS-248.
- `backend\tests` deselected 201 tests according to project markers/config.

## Suggested reviewer focus

- Verify the new trace contract stays internal and that future consumers do not treat `provenance` or `execution_trace` as a replay snapshot.
