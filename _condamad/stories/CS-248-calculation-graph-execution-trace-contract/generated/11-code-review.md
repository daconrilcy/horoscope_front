# Code Review - CS-248 calculation-graph-execution-trace-contract

Verdict: CLEAN

Review date: 2026-05-24

## Review Scope

- Story: `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/00-story.md`
- Source brief: `_story_briefs/cs-248-calculation-graph-execution-trace-contract.md`
- Tracker row: `_condamad/stories/story-status.md`
- Implementation files reviewed:
  - `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`
  - `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
  - `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`
  - `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`
  - `backend/tests/architecture/test_api_contract_neutrality.py`
- Evidence reviewed:
  - `generated/10-final-evidence.md`
  - `generated/03-acceptance-traceability.md`
  - `generated/07-no-legacy-dry-guardrails.md`
  - `evidence/validation.md`
  - `evidence/trace-after.json`
  - `evidence/openapi-routes.md`

## Iteration 1 Findings

- No actionable implementation issue found.
- No story, AC, scope or brief change was required.
- No code correction was applied during this review/fix cycle.

## Implementation Conformance

- AC1-AC3: runner results attach a versioned execution trace with graph identity, run id, ordered nodes and duration metrics.
- AC4: failed calculator and missing-input cases expose normalized error kinds without raw cause objects.
- AC5: cache hits expose hit state and output keys without cached values.
- AC6-AC7: trace payloads expose input/output keys and provenance refs, not raw runtime values.
- AC8: the trace contract distinguishes trace, provenance and replay snapshot, with replay remaining unimplemented.
- AC9: no API router, OpenAPI schema, frontend, DB model or migration is introduced by CS-248.
- AC10: before/after, API neutrality and validation evidence artifacts are present in the story capsule.

## Guardrails

- RG-002: PASS. Trace ownership stays under backend domain runtime; no API router owns the trace.
- RG-003: PASS. `app.routes`, `app.openapi()` and `TestClient` evidence show no route or public schema exposure.
- RG-010: PASS. Tests stay under collected backend test roots.
- No new allowlist, compatibility shim, fallback trace contract, replay snapshot, persistence surface or public serializer was found.

## Validation Results

All Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.

| Command | Result | Evidence |
|---|---|---|
| `python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py .\_condamad\stories\CS-248-calculation-graph-execution-trace-contract\00-story.md` | PASS | `CONDAMAD story validation: PASS` |
| `python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict .\_condamad\stories\CS-248-calculation-graph-execution-trace-contract\00-story.md` | PASS | `CONDAMAD story lint: PASS` |
| `ruff check backend\app\domain\astrology\runtime\calculation_graph_execution_trace.py backend\app\domain\astrology\runtime\calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py` | PASS | `All checks passed!` |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py` | PASS | `23 passed` |
| `ruff check backend` | PASS | `All checks passed!` |
| `python -B -m pytest -q backend\tests` | PASS | `904 passed, 201 deselected` |
| `python -B -c "from app.main import app; assert 'ExecutionTrace' not in str(app.openapi())"` | PASS | Run with `PYTHONPATH=backend` |
| `python -B -c "from app.main import app; assert not any('execution-trace' in getattr(r, 'path', '') for r in app.routes)"` | PASS | Run with `PYTHONPATH=backend` |
| `rg -n "ExecutionTrace\|redaction_policy\|provenance_ref" backend\app\domain\astrology\runtime backend\tests\unit\domain\astrology -g "*.py"` | PASS | Hits limited to runtime module, runner hook and unit tests |
| `rg -n "ExecutionTrace\|CalculationGraphExecutionTrace\|execution-trace\|execution_trace\|replay_snapshot" backend\app\api frontend backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"` | PASS_WITH_LIMITATIONS | Only unrelated LLM replay migrations matched |

## Fresh Review

Fresh review after validation remains CLEAN. The implementation closes the source brief phase without residual in-domain work.

## Propagation

- no-propagation: the review produced no reusable correction or guardrail update.

## Residual Risk

- Existing unrelated LLM replay migration names remain outside CS-248.
