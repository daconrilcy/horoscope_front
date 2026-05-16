# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-180-aligner-registre-modeles-db-infra`
- Source story: `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/00-story.md`
- Capsule path: `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/stories/regression-guardrails.md` modified, `_condamad/stories/story-status.md` modified, story capsule untracked.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/`.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes, generated files created in this execution.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 covered. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | In progress. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/infra/db/models/__init__.py` imports and exports `FlaggedContentModel`; `backend/app/infra/db/base.py` loads ORM registries. | `pytest -q app/tests/unit/test_db_model_registry_guard.py` - PASS, 4 tests passed. | PASS | `flagged_contents` present in `Base.metadata.tables`. |
| AC2 | `db-table-exception-register.md` lists exact exceptions only. | `pytest -q app/tests/unit/test_db_model_registry_guard.py` - PASS. | PASS | Guard verifies exact exception set. |
| AC3 | `Base.metadata` now loads all 125 declared model tables; audit after has no metadata gaps. | `pytest -q app/tests/unit/test_db_model_registry_guard.py` + `db-model-registry-after.md` - PASS. | PASS | Remaining SQLite tables without models are exact classified exceptions. |
| AC4 | `backend/app/api/v1/routers/admin/support.py` unchanged; model registry now supports `Base.metadata.create_all`. | `pytest -q --long app/tests/integration/test_admin_support_api.py` - PASS, 1 test passed. | PASS | Initial run without `--long` was deselected by repo fast-test hook and rerun with `--long`. |
| AC5 | No DB file, migration, or destructive cleanup changed. | Targeted modified-file scan for `drop_table\(|DROP TABLE` - PASS zero hits; broad story scan classified historical migration downgrade hits. | PASS | `_alembic_tmp_astrologer_profiles` remains classified, not modified. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/infra/db/models/__init__.py` | modified | Export `FlaggedContentModel` from the non-LLM model registry. | AC1 |
| `backend/app/infra/db/base.py` | modified | Load both non-LLM and LLM registries into `Base.metadata` without duplicating LLM exports. | AC1, AC3 |
| `backend/app/tests/unit/test_db_model_registry_guard.py` | added | Add deterministic guard for SQLite/model/metadata alignment and exact exceptions. | AC1, AC2, AC3, AC5 |
| `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-before.md` | added | Persist before audit. | AC2, AC3 |
| `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md` | added | Persist after audit. | AC2, AC3 |
| `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md` | added | Persist exact exceptions. | AC2 |
| `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/generated/**` | added/modified | CONDAMAD execution and validation evidence. | AC1-AC5 |
| `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/00-story.md` | modified | Mark implementation tasks complete and story ready for review. | AC1-AC5 |

## Files deleted

- None.

## Tests added or updated

- `backend/app/tests/unit/test_db_model_registry_guard.py` added.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Pre-existing dirty files recorded. |
| Python DB/model/metadata audit script | `backend/` | PASS | 0 | Before audit found `flagged_contents` missing from `Base.metadata`. |
| Python DB/model/metadata audit script | `backend/` | PASS | 0 | After audit: DB 129, model 125, metadata 125, no model missing metadata. |
| `pytest -q app/tests/unit/test_db_model_registry_guard.py` | `backend/` | FAIL then PASS | 1 then 0 | First run rejected prose mentioning forbidden wildcard examples; after artifact correction, 4 tests passed. |
| `pytest -q app/tests/integration/test_admin_support_api.py` | `backend/` | SKIPPED | 1 | Repo fast-test hook deselected integration tests without `--long`; rerun below. |
| `pytest -q --long app/tests/integration/test_admin_support_api.py` | `backend/` | PASS | 0 | 1 test passed. |
| `ruff format .` | `backend/` | PASS | 0 | 1389 files left unchanged. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q` | `backend/` | PASS | 0 | 2595 passed, 1 skipped, 1175 deselected in 151.79s. |
| `rg -n "drop_table\\(|DROP TABLE|_alembic_tmp_astrologer_profiles" app migrations ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra` | `backend/` | PASS_WITH_CLASSIFIED_HITS | 0 | Historical migration downgrade and story-evidence hits only; no story code/migration cleanup added. |
| `rg -n "drop_table\\(|DROP TABLE" app/infra/db/base.py app/infra/db/models/__init__.py app/tests/unit/test_db_model_registry_guard.py ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md` | `backend/` | PASS | 1 | Zero hits in modified implementation/evidence files; `rg` exit 1 means no match. |
| `rg -n "flagged_contents|FlaggedContentModel|llm_prompt_version_fallback_archives|SQLAlchemyJobStore|_alembic_tmp_astrologer_profiles|astrologer_prompt_profiles" app ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra -g "*.py" -g "*.md"` | `backend/` | PASS_WITH_CLASSIFIED_HITS | 0 | Hits classified as model, root registry export, support consumer, scheduler owner, exact exception evidence, story evidence, or historical migration test reference. |
| Independent review layer: Story Conformance | repo root | PASS | n/a | CLEAN; residual risk limited to not rerunning tests in read-only review. |
| Independent review layer: Technical Risk | repo root | CHANGES_REQUESTED | n/a | Accepted CR-1: guard depended on ignored local `backend/horoscope.db`; fixed by allowing deterministic reconstructed inventory from tracked models plus exact exception register when local DB is absent. |
| Independent review layer: Source Finding Closure | repo root | PASS | n/a | CLEAN; read-only runtime inventory confirmed closure on local DB. |
| Missing-DB guard simulation | `backend/` | PASS | 0 | `_sqlite_table_names()` returned 129 audited tables when `SQLITE_DB_PATH` pointed to a missing file. |
| `ruff format .` | `backend/` | PASS | 0 | Final rerun after review fix; 1389 files left unchanged. |
| `ruff check .` | `backend/` | PASS | 0 | Final rerun after review fix; all checks passed. |
| `pytest -q --long app/tests/integration/test_admin_support_api.py` | `backend/` | PASS | 0 | Final rerun after review fix; 1 test passed. |
| `pytest -q` | `backend/` | PASS | 0 | Final rerun after review fix; 2595 passed, 1 skipped, 1175 deselected in 151.48s. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict issues; line-ending warnings only. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | All required targeted checks ran. | None. | Not applicable. |

## DRY / No Legacy evidence

- No compatibility shim, alias, broad allowlist or destructive cleanup introduced.
- The guard no longer requires the ignored local `backend/horoscope.db` to exist; when absent, it reconstructs the audited inventory from tracked model declarations plus exact registered exceptions.
- LLM models remain exported from `app.infra.db.models.llm`; `base.py` only imports the registry for metadata side effects.
- Exact exceptions are enforced by `test_db_model_registry_guard.py`.

## Diff review

- `git diff --stat` and implementation diff reviewed. Changed code is scoped to DB metadata registry and the new guard; story/governance files are scoped to CS-180 evidence and status.

## Final worktree status

- `_condamad/stories/regression-guardrails.md` modified before this execution and contains RG-111 for CS-180.
- `_condamad/stories/story-status.md` updated to `done` for CS-180.
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/` remains untracked as the new story capsule.
- `backend/app/infra/db/base.py`, `backend/app/infra/db/models/__init__.py`, and `backend/app/tests/unit/test_db_model_registry_guard.py` are expected story changes.

## Remaining risks

- Fresh closure review on 2026-05-16 reran the CONDAMAD review/fix loop and
  found no new actionable finding. The final review artifact is
  `generated/11-code-review.md` with verdict `CLEAN`.
- Required validation was rerun after activating `.\.venv\Scripts\Activate.ps1`:
  `ruff format .`, `ruff check .`,
  `pytest -q app/tests/unit/test_db_model_registry_guard.py`,
  `pytest -q --long app/tests/integration/test_admin_support_api.py`,
  `pytest -q`, `git diff --check`, and the targeted destructive scan.
- None identified.

## Suggested reviewer focus

- Review exact exception classification and whether LLM metadata loading preserves the separated registry ownership.
