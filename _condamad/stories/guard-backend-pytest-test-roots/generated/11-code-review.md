# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/guard-backend-pytest-test-roots/00-story.md`
- Review date: 2026-04-30
- Verdict: `CLEAN`

## Inputs reviewed

- `_condamad/stories/guard-backend-pytest-test-roots/00-story.md`
- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md`
- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-before.md`
- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-after.md`
- `_condamad/stories/guard-backend-pytest-test-roots/generated/03-acceptance-traceability.md`
- `_condamad/stories/guard-backend-pytest-test-roots/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/guard-backend-pytest-test-roots/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/converge-backend-test-topology/backend-test-topology.md`
- `_condamad/stories/stabilize-transit-performance-benchmark/generated/10-final-evidence.md`
- `backend/pyproject.toml`
- `backend/app/tests/unit/test_backend_test_topology.py`

## Diff summary

- `backend/app/tests/unit/test_backend_test_topology.py` now reads the current story registry and validates standard roots, hidden backend test files, exact non-standard `tests` exceptions, and no active test files under documented exceptions.
- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` is the active canonical registry for backend pytest roots.
- `_condamad/stories/converge-backend-test-topology/backend-test-topology.md` is explicitly historical evidence and points to the active canonical registry.
- The before/after inventories remain stable at 431 backend test files under documented roots only.

## Findings

No actionable findings.

## Acceptance audit

- AC1: PASS. The active registry documents all configured pytest roots and the guard checks registry/config equality.
- AC2: PASS. Hidden backend test roots and non-standard `tests` exceptions are guarded by `test_backend_test_topology.py`.
- AC3: PASS. Standard pytest collection passes with `3491 tests collected`.
- AC4: PASS. Before/after backend test file inventory remains persisted at 431 files under documented roots only.

## Validation audit

- `RG-010` applies and is covered by `pytest -q app/tests/unit/test_backend_test_topology.py`, `pytest -q app/tests/unit/test_backend_pytest_collection.py`, standard collect-only, and the backend test inventory scan.
- `RG-013` applies because cross-import guard roots depend on this topology. Reviewer reran `pytest -q app/tests/unit/test_backend_test_helper_imports.py` and the targeted forbidden-import scan; both passed.
- The prior full-suite performance fluctuation is documented as resolved by `_condamad/stories/stabilize-transit-performance-benchmark/generated/10-final-evidence.md`, which records `pytest -q` PASS with `3479 passed, 12 skipped`.

## DRY / No Legacy audit

- No second active topology guard or parser was introduced.
- The previous registry ambiguity is resolved: the old topology document is historical only, and the current story registry is canonical.
- No compatibility wrapper, alias, fallback, re-export, duplicate active implementation, or new backend test root was found.

## Commands run by reviewer

| Command | Working directory | Result |
|---|---|---|
| `git status --short` | repo root | PASS, dirty/untracked state inspected |
| `git diff -- backend/app/tests/unit/test_backend_test_topology.py _condamad/stories/guard-backend-pytest-test-roots _condamad/stories/converge-backend-test-topology/backend-test-topology.md` | repo root | PASS |
| `git diff --check` | repo root | PASS, CRLF warnings only |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` | repo root | PASS, 1242 files already formatted |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_test_topology.py` | repo root | PASS, 6 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_pytest_collection.py` | repo root | PASS, 3 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_test_helper_imports.py` | repo root | PASS, 1 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest --collect-only -q --ignore=.tmp-pytest` | repo root | PASS, 3491 tests collected |
| `rg --files backend -g 'test_*.py' -g '*_test.py' -g '!backend/.tmp-pytest/**'` | repo root | PASS, 431 files |
| `rg --files backend\app -g 'test_*.py' -g '*_test.py' -g '!backend/app/tests/**' -g '!backend/.tmp-pytest/**'` | repo root | PASS, zero hits |
| `rg -n "from app\.tests\.(integration\|unit\|regression)\.test_\|from tests\.integration\.test_" backend/app/tests backend/tests -g test_*.py` | repo root | PASS, zero hits |

## Residual risks

- Full `pytest -q` was not rerun during this review. The current story requires targeted topology, collection, lint, and guard evidence; the previously failing full-suite benchmark is covered by the follow-up stabilization evidence.
- Unrelated CONDAMAD story/audit directories remain untracked in the worktree and were not reviewed beyond their impact on this target.

## Verdict

`CLEAN`
