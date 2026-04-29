# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `converge-backend-test-topology`
- Source story: `_condamad/stories/converge-backend-test-topology/00-story.md`
- Capsule path: `_condamad/stories/converge-backend-test-topology`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: untracked CONDAMAD story directories, including `_condamad/stories/converge-backend-test-topology/`.
- Pre-existing dirty files: untracked story directories shown by initial status.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, generated files created because only `00-story.md` existed.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Generated with AC1-AC4. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `_condamad/stories/converge-backend-test-topology/backend-test-topology.md` documents standard roots and opt-in policy; `test_backend_test_topology.py` parses it. | `pytest -q app/tests/unit/test_backend_test_topology.py` PASS. | PASS | Documentation and `pyproject.toml` must match. |
| AC2 | `backend/tests/llm_orchestration/test_qualified_context.py` replaces the embedded test path; `OPT_IN_TEST_FILES` is now empty. | Static inventory after has no `backend/app/domain/llm/prompting/tests` test files; topology guard PASS. | PASS | Historical references remain only in prior story evidence and current audit/story docs. |
| AC3 | `backend/pyproject.toml` standard roots match topology doc; no opt-in suite active. | `pytest --collect-only -q --ignore=.tmp-pytest` PASS, 3475 tests collected; collection guard PASS. | PASS | Full suite also passed. |
| AC4 | `backend/app/tests/unit/test_backend_test_topology.py` blocks undocumented roots, embedded domain test files, and doc/config drift. | `pytest -q app/tests/unit/test_backend_test_topology.py` PASS. | PASS | RG-010 added for durable invariant. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/regression-guardrails.md` | modified | Add RG-010 backend test topology invariant. | AC4 |
| `_condamad/stories/converge-backend-test-topology/00-story.md` | modified | Mark implementation tasks complete while preserving validator-required source status. | AC1-AC4 |
| `_condamad/stories/converge-backend-test-topology/backend-test-topology.md` | added | Document approved backend test roots. | AC1 |
| `_condamad/stories/converge-backend-test-topology/test-root-inventory-before.md` | added | Persist baseline root inventory. | AC2 |
| `_condamad/stories/converge-backend-test-topology/test-root-inventory-after.md` | added | Persist final root inventory. | AC2 |
| `_condamad/stories/converge-backend-test-topology/test-root-diff.md` | added | Explain topology changes. | AC2 |
| `_condamad/stories/converge-backend-test-topology/generated/*.md` | added/modified | Capsule execution and evidence files. | AC1-AC4 |
| `backend/app/tests/unit/test_backend_pytest_collection.py` | modified | Remove obsolete opt-in exception. | AC2, AC3 |
| `backend/app/tests/unit/test_backend_test_topology.py` | added | Guard topology and doc/config drift. | AC1, AC2, AC4 |
| `backend/tests/llm_orchestration/test_qualified_context.py` | added | Move embedded LLM context test into documented root. | AC2, AC3 |

## Files deleted

| File | Reason |
|---|---|
| `backend/app/domain/llm/prompting/tests/test_qualified_context.py` | Moved to `backend/tests/llm_orchestration/test_qualified_context.py`. |
| `backend/app/domain/llm/prompting/tests/conftest.py` | Obsolete support fixture after removing the embedded active test. |

## Tests added or updated

- Added `backend/app/tests/unit/test_backend_test_topology.py`.
- Updated `backend/app/tests/unit/test_backend_pytest_collection.py`.
- Moved `test_qualified_context.py` into `backend/tests/llm_orchestration`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial dirty state captured; unrelated untracked story dirs existed. |
| `rg --files backend -g test_*.py -g *_test.py -g !.tmp-pytest/**` | repo root | PASS | 0 | Before/after inventories captured. |
| `ruff format .` | `backend/` | PASS | 0 | 1 file reformatted, 1233 unchanged. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_backend_test_topology.py` | `backend/` | PASS | 0 | 4 passed. |
| `pytest -q app/tests/unit/test_backend_pytest_collection.py` | `backend/` | PASS | 0 | 3 passed. |
| `pytest -q tests/llm_orchestration/test_qualified_context.py` | `backend/` | PASS | 0 | 3 passed. |
| `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | PASS | 0 | 3475 tests collected. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict issues; Git warned about future CRLF conversion for one file. |
| `pytest -q` | `backend/` | PASS | 0 | 3463 passed, 12 skipped, 7 warnings. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/converge-backend-test-topology/00-story.md` | repo root | FAIL | 1 | Failed after changing source story status to `ready-for-review`; validator requires `Status: ready-for-dev`. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/converge-backend-test-topology/00-story.md` | repo root | FAIL | 1 | Failed after changing source story status to `ready-for-review`; linter requires `Status: ready-for-dev`. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/converge-backend-test-topology/00-story.md` | repo root | PASS | 0 | CONDAMAD story validation PASS. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/converge-backend-test-topology/00-story.md` | repo root | PASS | 0 | CONDAMAD story lint PASS. |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- No compatibility re-export, collection shim, alias, or fallback collection path was added.
- `OPT_IN_TEST_FILES` is empty in `test_backend_pytest_collection.py`.
- Old active test path removed from backend test inventory.
- Legacy keyword scan hits are classified as:
  - `backend/tests/llm_orchestration/test_qualified_context.py`: expected business assertion for `res.source == "fallback"`, not a topology fallback.
  - Current story/capsule docs: explicit No Legacy requirements and evidence.
  - `test-root-inventory-before.md`: historical existing `legacy_services` directory in test inventory, out of scope for this topology story.
  - Prior story `_condamad/stories/collect-retained-backend-tests/*`: allowed historical references explaining the old opt-in exception.

## Diff review

- `git diff --check` passed.
- Diff is limited to this story's CONDAMAD artifacts, backend topology guards, the moved LLM test, and RG-010.
- The moved test preserves the same behavioral assertions while adding French module/function docstrings.
- `00-story.md` keeps `Status: ready-for-dev` because the repository story validator requires that source status; readiness is recorded in this final evidence file.

## Final worktree status

Final `git status --short` includes expected story changes plus pre-existing untracked story directories:

```text
 D backend/app/domain/llm/prompting/tests/conftest.py
 D backend/app/domain/llm/prompting/tests/test_qualified_context.py
 M backend/app/tests/unit/test_backend_pytest_collection.py
 M _condamad/stories/regression-guardrails.md
?? _condamad/stories/converge-backend-test-topology/
?? _condamad/stories/converge-db-test-fixtures/
?? _condamad/stories/reclassify-story-regression-guards/
?? _condamad/stories/remove-cross-test-module-imports/
?? _condamad/stories/replace-seed-validation-facade-test/
?? backend/app/tests/unit/test_backend_test_topology.py
?? backend/tests/llm_orchestration/test_qualified_context.py
```

## Remaining risks

- `backend/app/domain/llm/prompting/tests/__init__.py` remains as a non-test historical module. It is documented as out of scope and guarded so no active test file returns there.
- Full suite warnings are pre-existing deprecation warnings in `tests/unit/prediction/test_llm_narrator.py`.

## Suggested reviewer focus

Review the topology guard's root parsing and confirm `app/tests`, `tests/evaluation`, `tests/integration`, `tests/llm_orchestration`, and `tests/unit` are the intended long-term backend pytest roots.
