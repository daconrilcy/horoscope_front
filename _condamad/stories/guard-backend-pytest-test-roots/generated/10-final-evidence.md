# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: `guard-backend-pytest-test-roots`
- Source story: `_condamad/stories/guard-backend-pytest-test-roots/00-story.md`
- Capsule path: `_condamad/stories/guard-backend-pytest-test-roots`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/guard-backend-pytest-test-roots/00-story.md`
- Initial `git status --short`: untracked backend-test audit/story directories, including `_condamad/stories/guard-backend-pytest-test-roots/`.
- Pre-existing dirty files: untracked `_condamad/audits/backend-tests/2026-04-29-1510/`, `_condamad/stories/classify-backend-ops-quality-tests/`, `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/`, `_condamad/stories/guard-backend-pytest-test-roots/`, `_condamad/stories/replace-deprecated-llm-narrator-tests/`.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes; the helper generated a title-derived duplicate first, then its `generated/` files were moved into the user-provided capsule and the duplicate was removed.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific boundaries recorded. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 covered. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and searches recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Required commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific canonical paths and scans recorded. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` documents all pytest roots with owners; `test_backend_test_topology.py` reads this registry. | `pytest -q app/tests/unit/test_backend_test_topology.py` PASS, including registry/config equality. | PASS | `backend/pyproject.toml` was not changed. |
| AC2 | `test_backend_test_topology.py` now checks exact documented exception directories and verifies exceptions contain no active test files. | `pytest -q app/tests/unit/test_backend_test_topology.py` PASS; hidden app-root scan returned zero hits. | PASS | Guard fails for `backend/app/**/tests/test_*.py` outside allowed roots. |
| AC3 | No collection config changed; `backend/pyproject.toml` still defines the same `testpaths`. | `pytest --collect-only -q --ignore=.tmp-pytest` PASS, 3491 tests collected after the later benchmark-stabilization story. | PASS | `pytest -q app/tests/unit/test_backend_pytest_collection.py` also PASS. |
| AC4 | `backend-test-files-before.md` and `backend-test-files-after.md` persist the same 431-file inventory by documented root. | Final `rg --files backend -g 'test_*.py' -g '*_test.py' -g '!backend/.tmp-pytest/**'` count remains 431 with 0 `OTHER`. | PASS | No test movement was needed. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/guard-backend-pytest-test-roots/00-story.md` | modified | Mark implementation tasks complete. | AC1-AC4 |
| `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` | added | Persist canonical topology registry for this story. | AC1 |
| `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-before.md` | added | Persist baseline inventory. | AC4 |
| `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-after.md` | added | Persist after inventory. | AC4 |
| `_condamad/stories/guard-backend-pytest-test-roots/generated/*.md` | added/modified | Capsule plan, traceability, validation, and evidence. | AC1-AC4 |
| `backend/app/tests/unit/test_backend_test_topology.py` | modified | Point guard to current registry and harden exact exception checks. | AC1-AC2 |

## Files deleted

None.

## Tests added or updated

- Updated `backend/app/tests/unit/test_backend_test_topology.py`; targeted guard now has 6 passing tests.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial dirty state captured; Git warned on unreadable pytest temp folders. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\guard-backend-pytest-test-roots\00-story.md` | repo root, venv active | PASS | 0 | Generated capsule files under a title-derived duplicate path; files were moved to the requested capsule. |
| `rg --files backend -g 'test_*.py' -g '*_test.py' -g '!backend/.tmp-pytest/**'` | repo root | PASS | 0 | 431 backend test files, all under documented roots. |
| `rg --files backend\app -g 'test_*.py' -g '*_test.py' -g '!backend/app/tests/**' -g '!backend/.tmp-pytest/**'` | repo root | PASS | 1 | Zero hidden app test files found. |
| `ruff format .` | `backend/` | PASS | 0 | 1242 files left unchanged. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_backend_test_topology.py` | `backend/` | PASS | 0 | 6 passed. |
| `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | PASS | 0 | 3491 tests collected after the later benchmark-stabilization story. |
| `pytest -q app/tests/unit/test_backend_pytest_collection.py` | `backend/` | PASS | 0 | 3 passed. |
| `pytest -q` | `backend/` | FAIL | 1 | 1 performance benchmark failed at 104.02 ms against a 100 ms budget; 3477 passed, 12 skipped. |
| `pytest -q app/tests/unit/test_transit_performance.py::test_v3_layers_performance_benchmark` | `backend/` | PASS | 0 | Isolated rerun passed in 0.41s, classifying the full-suite failure as local performance fluctuation outside this story. |
| `rg -n "legacy\|compat\|shim\|fallback\|deprecated\|alias" _condamad\stories\guard-backend-pytest-test-roots backend\app\tests\unit\test_backend_test_topology.py backend\pyproject.toml` | repo root | PASS | 0 | Hits are CONDAMAD No Legacy prose only; no active code shim/fallback hit. |
| `git diff --check` | repo root | PASS | 0 | No whitespace or conflict marker issues; Git warned about future CRLF conversion for the modified test file. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\guard-backend-pytest-test-roots` | repo root, venv active | PASS | 0 | CONDAMAD capsule validation passed. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Local app startup | no | Story changes a pytest topology guard and docs only; no runtime API or frontend surface changed. | Startup regressions outside changed surface would not be caught here. | Backend lint, targeted guards, collection, and broad pytest run were executed. |

## DRY / No Legacy evidence

- No compatibility wrapper, alias, fallback, re-export, or duplicate topology guard was added.
- Canonical topology registry for this story is `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md`.
- Runtime pytest source of truth remains `backend/pyproject.toml`.
- The hidden-root scan returned zero files outside `backend/app/tests`.
- Keyword scan hits are story/capsule No Legacy instructions only, plus no hits in `backend/app/tests/unit/test_backend_test_topology.py` or `backend/pyproject.toml`.

## Diff review

- `git diff --stat`: tracked diff is limited to `backend/app/tests/unit/test_backend_test_topology.py`; untracked story artifacts are under `_condamad/stories/guard-backend-pytest-test-roots/`.
- `git diff --check`: PASS, with CRLF warning only.
- Diff scope matches AC1-AC4; no production runtime code changed.

## Final worktree status

```text
 M backend/app/tests/unit/test_backend_test_topology.py
?? _condamad/audits/backend-tests/2026-04-29-1510/
?? _condamad/stories/classify-backend-ops-quality-tests/
?? _condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/
?? _condamad/stories/guard-backend-pytest-test-roots/
?? _condamad/stories/replace-deprecated-llm-narrator-tests/
```

`git status --short` also emitted warnings for unreadable pytest temp folders under `.codex-artifacts/`, `artifacts/`, and `backend/.tmp-pytest/`; those directories were not modified.

## Remaining risks

- Full `pytest -q` had one transient local performance failure in `app/tests/unit/test_transit_performance.py::test_v3_layers_performance_benchmark` at 104.02 ms versus a 100 ms budget. The isolated rerun passed, and the failure is unrelated to this topology story.
- The existing `_condamad/stories/converge-backend-test-topology/backend-test-topology.md` remains only as prior story evidence and now points to this story's canonical registry. The active guard reads the current story registry.

## Suggested reviewer focus

- Review the new topology registry ownership rows and confirm the old topology document is now historical evidence only.
- Review whether the broad-suite performance fluctuation should be tracked separately from this story.
