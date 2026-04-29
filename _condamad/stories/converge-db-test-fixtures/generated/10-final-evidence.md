# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: `converge-db-test-fixtures`
- Source story: `_condamad/stories/converge-db-test-fixtures/00-story.md`
- Capsule path: `_condamad/stories/converge-db-test-fixtures`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: story folders under `_condamad/stories/*` were untracked before implementation.
- Pre-existing dirty files: `_condamad/stories/converge-db-test-fixtures/`, `_condamad/stories/reclassify-story-regression-guards/`, `_condamad/stories/remove-cross-test-module-imports/`, `_condamad/stories/replace-seed-validation-facade-test/`.
- AGENTS.md files considered: `AGENTS.md`; no `backend/AGENTS.md` exists.
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story provided. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Generated. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Generated and pending final update. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `db-test-session-imports-before.md`, `db-test-session-imports-after.md`, `db-session-allowlist.md` persist the inventory and exceptions. | `pytest -q app/tests/unit/test_backend_db_test_harness.py` PASS; direct import `rg` run and hits classified as allowlisted/canonical/helper guard. | PASS | |
| AC2 | `backend/tests/integration/app_db.py` typed/documented; `backend/app/tests/helpers/db_session.py` added; `test_llm_release.py` and `test_admin_content_api.py` migrated to helpers. | `pytest -q app/tests/integration/test_admin_content_api.py` PASS; selected migrated subset of `test_llm_release.py` PASS. | PASS | Full `test_llm_release.py` still fails for release-service issues outside this DB harness story and is not the required migrated lot command. |
| AC3 | No Alembic/model changes; helpers resolve the effective runtime test DB session; `horoscope.db` side effect from tests was restored. | `pytest -q tests/integration/test_backend_sqlite_alignment.py` PASS. | PASS | |
| AC4 | `backend/app/tests/unit/test_backend_db_test_harness.py`, `db-session-allowlist.md`, and `RG-011` enforce no new direct imports, no unclassified `create_all`, no unclassified SQLite factories, and no `create_all` in files that reference `horoscope.db`. | `pytest -q app/tests/unit/test_backend_db_test_harness.py` PASS. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/regression-guardrails.md` | modified | Add durable DB harness invariant `RG-011`. | AC4 |
| `_condamad/stories/converge-db-test-fixtures/00-story.md` | existing | Source story, unchanged. | all |
| `_condamad/stories/converge-db-test-fixtures/generated/*.md` | added | CONDAMAD capsule, plan, traceability, validation, evidence. | all |
| `_condamad/stories/converge-db-test-fixtures/db-test-session-imports-before.md` | added | Before inventory. | AC1 |
| `_condamad/stories/converge-db-test-fixtures/db-test-session-imports-after.md` | added | After inventory. | AC1 |
| `_condamad/stories/converge-db-test-fixtures/db-fixture-topology-before.md` | added | Before topology. | AC1, AC3 |
| `_condamad/stories/converge-db-test-fixtures/db-fixture-topology-after.md` | added | After topology. | AC2, AC3 |
| `_condamad/stories/converge-db-test-fixtures/db-session-allowlist.md` | added | Exact temporary exceptions. | AC1, AC4 |
| `backend/app/tests/helpers/db_session.py` | added | Canonical DB helper for `app/tests`. | AC2 |
| `backend/app/tests/unit/test_backend_db_test_harness.py` | added | AST guard against new direct production DB session imports, unclassified `create_all`, unclassified SQLite factories, and primary DB `create_all` risk. | AC1, AC4 |
| `backend/tests/integration/app_db.py` | modified | Document and type canonical integration helper. | AC2 |
| `backend/app/tests/integration/test_admin_content_api.py` | modified | Migrate representative app integration test to helper. | AC2 |
| `backend/tests/integration/test_llm_release.py` | modified | Migrate representative backend integration test to helper. | AC2 |

## Files deleted

None.

## Tests added or updated

- Added `backend/app/tests/unit/test_backend_db_test_harness.py`.
- Updated `backend/app/tests/integration/test_admin_content_api.py`.
- Updated `backend/tests/integration/test_llm_release.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial dirty worktree recorded; story folders already untracked. |
| `pytest -q app/tests/unit/test_backend_db_test_harness.py` | `backend/` | PASS | 0 | 4 passed after guard hardening. |
| `pytest -q tests/integration/test_backend_sqlite_alignment.py` | `backend/` | PASS | 0 | 6 passed. |
| `pytest -q app/tests/integration/test_admin_content_api.py` | `backend/` | FAIL then PASS | 1 then 0 | First run exposed one missed `SessionLocal`; after fix, 3 passed. |
| `pytest -q tests/integration/test_llm_release.py` | `backend/` | FAIL, not required after review fix | 1 | 4 passed, 7 failed; failures are release-service behavior outside this DB harness story. |
| `pytest -q tests/integration/test_llm_release.py -k "activation_evidence_requires_timezone_aware_datetime or activate_endpoint_rejects_naive_generated_at_with_422 or llm_release_lifecycle or snapshot_validation_independence"` | `backend/` | PASS | 0 | 4 passed, 7 deselected. Required migrated backend lot. |
| `ruff format .` | `backend/` | PASS | 0 | 1236 files left unchanged. |
| `ruff check . --fix` | `backend/` | PASS | 0 | 2 import-order issues fixed. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `rg -n "from app\.infra\.db\.session import .*\b(SessionLocal\|engine)\b\|db_session_module\.SessionLocal" app/tests tests -g "*.py"` | `backend/` | PASS | 0 | Remaining hits are canonical helper/guard or allowlisted exceptions. |
| `rg -n "Base\.metadata\.create_all" app/tests tests -g "*.py"` | `backend/` | PASS | 0 | Existing test DB setup hits classified; no new `horoscope.db` create_all introduced. |
| `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | PASS | 0 | 3479 tests collected. |
| `pytest -q` | `backend/` | PASS, user-provided manual evidence | 0 | 3467 passed, 12 skipped, 7 warnings in 783.97s (0:13:03). Warnings are `LLMNarrator` deprecation warnings in `tests/unit/prediction/test_llm_narrator.py`. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/converge-db-test-fixtures/00-story.md` | repo root | PASS | 0 | Story validation PASS. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/converge-db-test-fixtures/00-story.md` | repo root | PASS | 0 | Story lint PASS. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed; untracked added files not included by Git stat. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | Full backend regression was completed manually by the user after the review pass. | Residual risk limited to warnings. | `pytest -q`: 3467 passed, 12 skipped, 7 warnings in 783.97s. |

## DRY / No Legacy evidence

- Canonical helpers are `backend/tests/integration/app_db.py` and `backend/app/tests/helpers/db_session.py`.
- No compatibility alias or re-export was introduced.
- `backend/tests/integration/test_llm_release.py` and `backend/app/tests/integration/test_admin_content_api.py` no longer import production `SessionLocal` or `engine`.
- Remaining direct import hits are either canonical helper internals, guard expected text, or listed in `db-session-allowlist.md`; `db-test-session-imports-after.md` now records file-level classifications and hit counts.
- `test_backend_db_test_harness.py` also blocks unclassified `Base.metadata.create_all`, unclassified SQLite factories, and `create_all` in files that reference `horoscope.db`.
- `RG-011` records the durable anti-reintroduction invariant.

## Diff review

- Diff is scoped to story evidence, DB test helpers, representative migrated tests, architecture guard, and regression guardrail registry.
- `backend/horoscope.db` was modified by test execution and restored because it was not part of the story.
- No Alembic migration, SQLAlchemy model, frontend, dependency, or requirements file changed.

## Final worktree status

Final `git status --short`:

```text
 M _condamad/stories/regression-guardrails.md
 M backend/app/tests/integration/test_admin_content_api.py
 M backend/tests/integration/app_db.py
 M backend/tests/integration/test_llm_release.py
?? _condamad/stories/converge-db-test-fixtures/
?? _condamad/stories/reclassify-story-regression-guards/
?? _condamad/stories/remove-cross-test-module-imports/
?? _condamad/stories/replace-seed-validation-facade-test/
?? backend/app/tests/helpers/db_session.py
?? backend/app/tests/unit/test_backend_db_test_harness.py
```

The untracked story folders other than `converge-db-test-fixtures` existed at preflight and were left untouched.

## Remaining risks

- Full backend regression now has user-provided manual evidence: `pytest -q` passed with 3467 passed, 12 skipped, 7 warnings.
- The 7 warnings are known `LLMNarrator` deprecation warnings in `tests/unit/prediction/test_llm_narrator.py`.
- Many existing direct DB session imports remain allowlisted and should be migrated in later batches.
- Untracked folders `reclassify-story-regression-guards`, `remove-cross-test-module-imports`, and `replace-seed-validation-facade-test` are upcoming stories, not residual risk for this story.

## Suggested reviewer focus

- Review the allowlist scope and whether any exception should be migrated in the next batch.
- Review the AST guard path parsing and canonical helper exclusions.
- Review the `test_llm_release.py` limitation separately from this DB helper migration.
