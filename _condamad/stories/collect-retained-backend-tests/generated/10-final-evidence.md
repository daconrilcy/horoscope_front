# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `collect-retained-backend-tests`
- Source story: `_condamad/stories/collect-retained-backend-tests/00-story.md`
- Capsule path: `_condamad/stories/collect-retained-backend-tests`

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/pyproject.toml` includes retained backend roots: `app/tests`, `tests/evaluation`, `tests/integration`, `tests/llm_orchestration`, `tests/unit`. Evidence files before/after persisted. | `pytest --collect-only -q --ignore=.tmp-pytest` collected 3468 tests; `pytest -q` passed with 3456 passed, 12 skipped. | PASS | One exact opt-in exception is documented separately. |
| AC2 | `app/ai_engine/tests` removed from `testpaths`; `test_configured_pytest_testpaths_exist` guards configured roots. | `pytest -q app/tests/unit/test_backend_pytest_collection.py` passed with 3 tests. | PASS | |
| AC3 | `OPT_IN_TEST_FILES` in `backend/app/tests/unit/test_backend_pytest_collection.py`; `uncollected-tests-after.md` records the exact exception and reason. | `test_opt_in_test_files_are_exact_existing_exceptions` passed; `uncollected-tests-after.md` reports 0 uncollected retained files and 1 exact opt-in exception. | PASS | Exception: `app/domain/llm/prompting/tests/test_qualified_context.py`. |
| AC4 | `backend/app/tests/unit/test_backend_pytest_collection.py` compares static backend test files with runtime collected files. | `pytest -q app/tests/unit/test_backend_pytest_collection.py` passed with 3 tests. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/pyproject.toml` | modified | Remove nonexistent `app/ai_engine/tests`; add `tests/llm_orchestration` and `tests/unit` to standard pytest roots. | AC1, AC2 |
| `backend/app/tests/unit/test_backend_pytest_collection.py` | added | Guard configured roots, static-vs-runtime collection, and exact opt-in exceptions. | AC1-AC4 |
| `backend/tests/llm_orchestration/*.py` | modified | Update newly collected retained tests to current LLM DB/API/runtime contracts instead of preserving stale legacy assumptions. | AC1 |
| `backend/app/api/v1/routers/admin/llm/prompts.py` | modified | Normalize prompt audit status when SQLAlchemy returns a string-backed status. | AC1 |
| `_condamad/stories/collect-retained-backend-tests/pytest-collection-after.md` | regenerated | Runtime collection after fixes. | AC1 |
| `_condamad/stories/collect-retained-backend-tests/static-test-inventory-after.md` | regenerated | Static test-file inventory after fixes. | AC1 |
| `_condamad/stories/collect-retained-backend-tests/uncollected-tests-after.md` | generated | Uncollected retained file and opt-in register. | AC1, AC3 |

## Tests added or updated

- Added `backend/app/tests/unit/test_backend_pytest_collection.py` with 3 guard tests.
- Updated stale retained tests under `backend/tests/llm_orchestration` so the newly collected suite validates current contracts:
  - `LlmPromptVersionModel` no longer accepts provider model fields.
  - `PromptAssemblyConfigModel` requires execution profiles for published assemblies.
  - use-case fallback tests no longer rely on unregistered runtime use cases.
  - persona fixtures use allowed enum values.
  - admin prompt payloads use the current `LlmPromptVersionCreate` contract.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `. .\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q tests/llm_orchestration` | repo root | PASS | 0 | 186 passed. |
| `. .\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_pytest_collection.py` | repo root | PASS | 0 | 3 passed. |
| `. .\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format .` | repo root | PASS | 0 | 6 files reformatted during fixes; later run reported 1234 files unchanged. |
| `. .\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `. .\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_backend_pytest_collection.py` | repo root | PASS | 0 | 57 passed. |
| `. .\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` | repo root | PASS | 0 | 3456 passed, 12 skipped, 7 warnings in 552.27s. |
| `. .\\.venv\\Scripts\\Activate.ps1; cd backend; pytest --collect-only -q --ignore=.tmp-pytest *> '..\\_condamad\\stories\\collect-retained-backend-tests\\pytest-collection-after.md'` | repo root | PASS | 0 | 3468 tests collected; evidence persisted. |
| `rg --files backend -g 'test_*.py' -g '*_test.py' -g '!backend/.tmp-pytest/**'` | repo root | PASS | 0 | Static inventory: 426 files; evidence persisted. |
| `. .\\.venv\\Scripts\\Activate.ps1; cd backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 8765` | repo root | PASS | 0 | Server started, `/docs` returned HTTP 200, then the process was stopped. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; CRLF normalization warnings only. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| none | no | All required validation completed. | none | none |

## DRY / No Legacy evidence

- No duplicate pytest configuration was introduced.
- `backend/pyproject.toml` remains the single pytest configuration source.
- `app/ai_engine/tests` no longer appears in `backend/pyproject.toml`.
- No compatibility shim, alias, fallback collection command, or wildcard opt-in list was added.
- Newly collected LLM orchestration tests were updated to current contracts instead of reintroducing removed fields.
- Exact opt-in exception remains `app/domain/llm/prompting/tests/test_qualified_context.py`, guarded in code and persisted in `uncollected-tests-after.md`.

## Diff review

- `git diff --check` passed with CRLF normalization warnings only.
- API architecture guard passed after avoiding new private helpers in router modules and preserving exact SQL boundary allowlist line references.
- The previous blocker is resolved: the standard backend command `pytest -q` now passes.

## Remaining risks

- The embedded `app/domain/llm/prompting/tests/test_qualified_context.py` remains opt-in because collecting its package requires missing local `tests/data/prompt_governance_registry.json`.
- `pytest -q` emits existing `LLMNarrator` deprecation warnings in prediction tests.

## Suggested reviewer focus

- Review the exact opt-in exception in the dedicated topology-convergence story.
- Review whether the updated `tests/llm_orchestration` tests should later be moved into the canonical backend test topology.
