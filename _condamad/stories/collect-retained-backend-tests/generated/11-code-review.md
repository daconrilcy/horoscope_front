# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/collect-retained-backend-tests/00-story.md`
- Implementation surface: `backend/pyproject.toml`, `backend/app/tests/unit/test_backend_pytest_collection.py`, retained backend tests, persisted collection evidence.
- Verdict: `CLEAN`

## Inputs reviewed

- Story source and generated capsule files.
- `_condamad/stories/regression-guardrails.md` (`RG-001` through `RG-009` all applicable because this story changes backend test collection).
- `backend/pyproject.toml` pytest configuration.
- New collection guard test.
- Persisted before/after inventories and final evidence.

## Diff summary

- `backend/pyproject.toml` removes nonexistent `app/ai_engine/tests` and adds `tests/llm_orchestration` plus `tests/unit` to `testpaths`.
- `backend/app/tests/unit/test_backend_pytest_collection.py` adds guards for existing configured roots, static-vs-runtime collection coverage, and exact opt-in exceptions.
- Stale newly collected tests under `backend/tests/llm_orchestration` were updated to current LLM DB/API/runtime contracts.
- `backend/app/api/v1/routers/admin/llm/prompts.py` now records prompt audit status safely when SQLAlchemy returns a string-backed enum value.

## Findings

No open findings.

Previously reported findings were resolved:

- CR-001: standard backend pytest suite is now green. `pytest -q` passed with 3456 passed, 12 skipped.
- CR-002: final evidence now reports `Validation outcome: PASS` and `Ready for review: yes`.

## Acceptance audit

- AC1: passes. `pytest --collect-only -q --ignore=.tmp-pytest` collects 3468 tests and `pytest -q` passes.
- AC2: passes. Configured `testpaths` exist and `app/ai_engine/tests` is no longer configured.
- AC3: passes. The only opt-in exception is exact and persisted: `app/domain/llm/prompting/tests/test_qualified_context.py`.
- AC4: passes. The guard compares static backend test files against runtime collect-only files.

## Validation audit

Commands run in the venv:

```powershell
. .\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/llm_orchestration
. .\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_pytest_collection.py
. .\.venv\Scripts\Activate.ps1; cd backend; ruff format .
. .\.venv\Scripts\Activate.ps1; cd backend; ruff check .
. .\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_backend_pytest_collection.py
. .\.venv\Scripts\Activate.ps1; cd backend; pytest -q
. .\.venv\Scripts\Activate.ps1; cd backend; pytest --collect-only -q --ignore=.tmp-pytest
git diff --check
```

Results:

- `tests/llm_orchestration`: 186 passed.
- Collection guard: 3 passed.
- Architecture and collection guards together: 57 passed.
- Full backend suite: 3456 passed, 12 skipped, 7 warnings.
- `ruff check .`: passed.
- `git diff --check`: passed with CRLF normalization warnings only.

## DRY / No Legacy audit

- No duplicate pytest configuration was introduced.
- No compatibility wrapper or alternate collection command was introduced.
- The opt-in exception is explicit rather than wildcarded.
- Newly collected retained tests were repaired to current contracts rather than preserving removed DB/API fields.

## Residual risks

- `app/domain/llm/prompting/tests/test_qualified_context.py` remains opt-in pending the dedicated topology-convergence decision.
- Existing `LLMNarrator` deprecation warnings remain in unrelated prediction tests.

## Verdict

`CLEAN`
