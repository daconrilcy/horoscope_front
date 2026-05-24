# Dev Log

## Preflight

- Initial `git status --short`: dirty worktree with pre-existing CS-246, CS-247, architecture, runtime and test changes.
- Current branch: not required for implementation.
- Existing dirty files: recorded in final evidence; unrelated user changes preserved.

## Search evidence

- Story, brief and `story-status.md` alignment verified.
- Capsule generated and validated after required generated files were missing.
- Scoped guardrails resolved by IDs named in the story: RG-002, RG-003, RG-010.
- Runner, graph contracts, natal graph and runner/API tests inspected.

## Implementation notes

- Added canonical internal trace module under astrology runtime.
- Attached redacted trace to runner results for success, failed node, validation failure and cache hit paths.
- Kept runner provenance distinct and did not expose trace through API routes or OpenAPI.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `condamad_prepare.py ... --with-optional` | PASS | Generated capsule files. |
| `condamad_validate.py _condamad\stories\CS-248-calculation-graph-execution-trace-contract` | PASS | Capsule structure valid. |
| `ruff format <changed files>` | PASS | Scoped formatting. |
| `python -B -m pytest -q <targeted CS-248 tests>` | PASS | 23 passed. |
| `ruff check backend` | PASS | All checks passed. |
| `python -B -m pytest -q backend\tests` | PASS | 904 passed, 201 deselected. |

## Issues encountered

- The capsule preparer initially created an extra derived capsule path; that agent-created accidental directory was removed after verifying it was inside the workspace.
- The broad forbidden scan reported existing unrelated `raw_output` frontend admin prompt files and an absent `backend\alembic` path; an adjusted public trace scan against `backend\migrations` found only unrelated LLM replay migrations.

## Decisions made

- Do not enrich the regression guardrail registry, per story instruction.
- Do not export the trace from `runtime/__init__.py`; direct module ownership is clearer and avoids widening public import surface.
- Use `duration_ms` on node results so trace metrics come from runner execution, not reconstructed evidence.

## Final `git status --short`

- Pending final status recorded in `10-final-evidence.md`.
