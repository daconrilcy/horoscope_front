# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/converge-backend-test-topology/00-story.md`
- Verdict: `CLEAN`

## Inputs reviewed

- Source story and generated capsule evidence.
- Regression guardrail registry `_condamad/stories/regression-guardrails.md`.
- Backend pytest topology doc and guards.
- Moved LLM context test and related conftests.
- Git diff, untracked story files, and validation commands.

## Diff summary

- Added topology registry `_condamad/stories/converge-backend-test-topology/backend-test-topology.md`.
- Added topology guard `backend/app/tests/unit/test_backend_test_topology.py`.
- Removed embedded active test path under `backend/app/domain/llm/prompting/tests`.
- Added moved test under `backend/tests/llm_orchestration/test_qualified_context.py`.
- Removed obsolete opt-in exception from `backend/app/tests/unit/test_backend_pytest_collection.py`.
- Added RG-010 to `_condamad/stories/regression-guardrails.md`.

## Findings

No open actionable findings.

### Resolved - La garde ne bloquait pas les nouveaux dossiers `tests` embarques sans fichier de test

- Resolution: `backend/app/tests/unit/test_backend_test_topology.py` now inventories directories named `tests` under `backend/app`, allows only `backend/app/tests` and the documented non-test package directory `backend/app/domain/llm/prompting/tests`, and fails on any other embedded `tests` directory regardless of contents.
- Evidence: `pytest -q app/tests/unit/test_backend_test_topology.py` passes.

## Acceptance audit

- AC1: satisfied by the topology documentation and doc/config parity guard.
- AC2: satisfied for active backend test files; the embedded active test moved to `backend/tests/llm_orchestration`.
- AC3: satisfied by standard pytest collection.
- AC4: satisfied by guards for undocumented test files, embedded `tests` directories, and doc/config drift.
- RG-001..RG-009: no protected application surface changed.
- RG-010: protected by `test_backend_test_topology.py`, `test_backend_pytest_collection.py`, and standard collection.

## Validation audit

Reviewer/fix validation commands run with the venv activated:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format --check .
ruff check .
pytest -q app/tests/unit/test_backend_test_topology.py
pytest -q app/tests/unit/test_backend_pytest_collection.py
pytest -q tests/llm_orchestration/test_qualified_context.py
pytest --collect-only -q --ignore=.tmp-pytest
```

Results: all passed; collect-only reported 3475 tests collected.

## DRY / No Legacy audit

- No compatibility re-export or pytest collection shim was introduced.
- The moved test preserves the old assertions and uses the existing `tests/llm_orchestration` fixture.
- `OPT_IN_TEST_FILES` is empty as intended.
- The remaining `backend/app/domain/llm/prompting/tests` directory is documented as a non-test historical module and is explicitly allowlisted by the topology guard.

## Residual risks

- None identified for the reviewed story scope.
