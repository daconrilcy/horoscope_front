# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `renommer-tables-maisons-astrales`
- Source story: `_condamad/stories/renommer-tables-maisons-astrales/00-story.md`
- Capsule path: `_condamad/stories/renommer-tables-maisons-astrales/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing dirty artifacts and docs present before implementation.
- Pre-existing dirty files: `.codex-artifacts/**`, `docs/recherches astro/**`, `docs/tables-maisons-et-roles.md`, `output/`.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | |
| `generated/01-execution-brief.md` | yes | yes | PASS | |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | |
| `generated/04-target-files.md` | yes | yes | PASS | |
| `generated/06-validation-plan.md` | yes | yes | PASS | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | |
| `generated/10-final-evidence.md` | yes | yes | PASS | |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/infra/db/models/reference.py` and `backend/app/infra/db/models/prediction_reference.py` now use `astral_houses`, `astral_prediction_daily_house_profiles`, `astral_house_category_weights`, and `ForeignKey("astral_houses.id")`. | Targeted pytest passed; strict scan `__tablename__ = "houses"|ForeignKey("houses.id")` returned zero hits in `backend/app` and `backend/tests`. | PASS | Python field names remain unchanged by design. |
| AC2 | `backend/migrations/versions/20260513_0094_rename_house_tables.py` renames the three tables, recreates canonical indexes, and downgrades to old names. | Migration tests passed; `alembic heads` reports `20260513_0094 (head)`. | PASS | Old names appear inside the migration only as rename/downgrade references. |
| AC3 | `test_migration_a_prediction_tables.py` and `test_reference_data_migrations.py` assert canonical table names, old-name absence at head, and FK targets to `astral_houses`. | `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py -q` passed: 12 tests. | PASS | |
| AC4 | `docs/tables-maisons-et-roles.md` now documents canonical SQL table names and keeps runtime JSON `houses` wording separate. | Search review classified remaining old-name hits as Python runtime fields/methods, historical migration/downgrade references, or negative test guards. | PASS | The doc file was already untracked before this story and was edited in place. |
| AC5 | Validation stayed on changed backend files, targeted migrations/repositories, scans, and diff checks. | Full `pytest -q` was not run per user request; targeted tests and lint/format passed. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/infra/db/models/reference.py` | modified | Rename active house table mapping to `astral_houses`. | AC1 |
| `backend/app/infra/db/models/prediction_reference.py` | modified | Rename active house profile/weight table mappings and FK target. | AC1 |
| `backend/migrations/versions/20260513_0094_rename_house_tables.py` | added | Alembic rename/downgrade migration. | AC2 |
| `backend/app/tests/unit/test_prediction_reference_repository.py` | modified | Add canonical table-name model guard. | AC1, AC3 |
| `backend/app/tests/integration/test_migration_a_prediction_tables.py` | modified | Expect canonical table/index names at head. | AC2, AC3 |
| `backend/app/tests/integration/test_reference_data_migrations.py` | modified | Assert canonical house table, old-name absence, and FK targets. | AC2, AC3 |
| `docs/tables-maisons-et-roles.md` | modified | Document canonical SQL names. | AC4 |
| `_condamad/stories/regression-guardrails.md` | modified | Update RG-092 wording/guard to `astral_houses`. | AC3 |
| `_condamad/stories/story-status.md` | modified | Register story as ready for review. | AC5 |
| `_condamad/stories/renommer-tables-maisons-astrales/**` | added/modified | CONDAMAD capsule and final evidence. | AC5 |

## Files deleted

None.

## Tests added or updated

- Added `test_house_models_use_canonical_astral_table_names`.
- Updated migration integration tests for canonical house table names, canonical indexes, FK target, and old table-name absence.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Pre-existing dirty files identified before editing. |
| `ruff format app/infra/db/models/reference.py app/infra/db/models/prediction_reference.py app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py migrations/versions/20260513_0094_rename_house_tables.py` | `backend/` after venv activation | PASS | 0 | 1 file reformatted, 5 unchanged. |
| `ruff check app/infra/db/models/reference.py app/infra/db/models/prediction_reference.py app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py migrations/versions/20260513_0094_rename_house_tables.py` | `backend/` after venv activation | PASS | 0 | All checks passed. |
| `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py -q` | `backend/` after venv activation | PASS | 0 | 12 passed; 18 SQLAlchemy reflection warnings on existing expression-based index handling. |
| `ruff format --check app/infra/db/models/reference.py app/infra/db/models/prediction_reference.py app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py migrations/versions/20260513_0094_rename_house_tables.py` | `backend/` after venv activation | PASS | 0 | 6 files already formatted. |
| `alembic heads` | `backend/` after venv activation | PASS | 0 | `20260513_0094 (head)`. |
| `rg -n '__tablename__ = "houses"\|ForeignKey\("houses\.id"\)' backend/app backend/tests` | repo root | PASS | 1 | Zero active hits. |
| `rg -n 'HouseModel\.reference_version_id\|HouseModel\(reference_version_id\|__tablename__ = "houses"\|ForeignKey\("houses\.id"\)' backend/app backend/tests` | repo root | PASS | 1 | Zero active hits. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict issues; Git reported line-ending warnings on pre-existing and touched files. |
| `git diff --stat` | repo root | PASS | 0 | Shows expected tracked story files plus pre-existing `.codex-artifacts/**` modifications. |
| `git status --short` | repo root | PASS | 0 | Final worktree recorded below. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `pytest -q` | no | Explicit user instruction: do not run the full test suite. | Regressions outside migrations/reference repository not covered in this run. | Targeted repository/migration tests, lint/format, Alembic head check, and No Legacy scans passed. |
| Local app startup | no | Backend DB schema rename was validated through Alembic upgrade/downgrade tests; no frontend/runtime server change. | Startup-only integration issue outside targeted scope could remain. | Migration tests instantiate head schema; repository/model tests validate ORM mappings. |

## DRY / No Legacy evidence

- No compatibility view, alias table, dual-read, dual-write, or fallback was added.
- Strict active SQL scan for `__tablename__ = "houses"` and `ForeignKey("houses.id")` returned zero hits in `backend/app` and `backend/tests`.
- Remaining `house_profiles` / `house_category_weights` hits in `backend/app` and active tests are Python domain field, method, or object names; they are not SQL table names.
- Old table names remain in historical migrations and in the new migration's downgrade/rename constants only.
- `RG-092` now names `astral_houses` as the stable non-versioned house vocabulary and extends the guard with old-table-name scans.

## Diff review

- Reviewed model, migration, tests, guardrail registry, story-status, and doc changes.
- No unrelated backend/frontend application files were modified.
- `.codex-artifacts/**`, `output/`, and `docs/recherches astro/**` were pre-existing dirty/untracked files and were not touched by this story.
- Review finding: no blocking issue found in the modified scope.

## Final worktree status

Final `git status --short` includes expected story changes plus pre-existing dirty files:

- Expected: `_condamad/stories/renommer-tables-maisons-astrales/`, `backend/migrations/versions/20260513_0094_rename_house_tables.py`, backend model/test changes, `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `docs/tables-maisons-et-roles.md`.
- Pre-existing/unrelated: `.codex-artifacts/**`, `docs/recherches astro/Aspects.png`, `docs/recherches astro/next step/`, `docs/recherches astro/planetes.png`, `output/`.

## Remaining risks

- Full backend regression suite was intentionally skipped by user request.
- SQLAlchemy emitted known reflection warnings while migrations inspected an expression-based index; tests still passed.
- Existing databases must apply Alembic migration `20260513_0094` before runtime uses the new ORM mappings.

## Suggested reviewer focus

- Verify the Alembic rename strategy and downgrade are acceptable for the supported DB engines.
- Verify remaining old-name hits are correctly classified as runtime/domain fields or historical migration references, not active SQL table names.
