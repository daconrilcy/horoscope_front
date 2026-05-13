# Final Evidence

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Story source: prompt body persisted to `00-story.md`
- Initial `git status --short`: recorded before implementation; worktree already contained unrelated modified/untracked files.
- Pre-existing dirty files: `.codex-artifacts/**`, `backend/app/infra/db/models/__init__.py`, `backend/app/infra/db/models/reference.py`, `backend/app/infra/db/repositories/reference_repository.py`, `backend/app/services/prediction/reference_seed_service.py`, `backend/app/tests/integration/test_reference_data_migrations.py`, `backend/app/tests/integration/test_seed_31_prediction_v2.py`, `backend/migrations/versions/20260513_0088_add_astral_dignity_type.py`, docs/images/output.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Prompt persisted. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Created. |
| `generated/04-target-files.md` | yes | yes | PASS | Created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Created. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Created. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/infra/db/models/prediction_reference.py` maps `PlanetProfileModel` to `astral_prediction_daily_planet_profiles`. | Targeted repository and migration tests passed. | PASS | Python DTO field names intentionally unchanged. |
| AC2 | `backend/migrations/versions/20260513_0089_rename_daily_planet_profiles.py` renames the table and normalizes index names; downgrade restores the old name. | `test_migration_a_prediction_tables.py` passed upgrade and downgrade through Alembic on a temp DB. | PASS | No compatibility table/view added. |
| AC3 | `test_migration_a_prediction_tables.py` and `test_reference_data_migrations.py` assert the canonical table and absence of `planet_profiles` at head. | Targeted pytest command passed: 12 tests. | PASS | |
| AC4 | `docs/tables-planetes-et-roles.md` now documents the canonical SQL table name. | `rg -n "astral_prediction_daily_planet_profiles" backend docs` shows model, migration, tests and docs. | PASS | |
| AC5 | Residual `planet_profiles` hits in active code are runtime collection/count names or negative assertions; migrations keep historical old-table references. | Targeted scans completed and classified. | PASS | |

## Files changed

- `backend/app/infra/db/models/prediction_reference.py`
- `backend/migrations/versions/20260513_0089_rename_daily_planet_profiles.py`
- `backend/app/tests/integration/test_migration_a_prediction_tables.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `docs/tables-planetes-et-roles.md`
- `_condamad/stories/rename-planet-profiles-table/**`
- `_condamad/stories/story-status.md`

## Files deleted

None.

## Tests added or updated

- Updated migration/schema tests to assert `astral_prediction_daily_planet_profiles` and reject active `planet_profiles` at Alembic head.

## Commands run

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app/infra/db/models/prediction_reference.py app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py migrations/versions/20260513_0089_rename_daily_planet_profiles.py` - PASS
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/integration/test_migration_a_prediction_tables.py app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py app/tests/unit/test_prediction_reference_repository.py -q` - PASS, 12 passed
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` - PASS
- `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(app.title)"` - PASS, printed `horoscope-backend`
- `rg -n '__tablename__ = "planet_profiles"|create_table\("planet_profiles"|drop_table\("planet_profiles"|"planet_profiles"' backend/app backend/tests docs -g "*.py" -g "*.md"` - PASS_WITH_CLASSIFIED_HITS
- `rg -n "astral_prediction_daily_planet_profiles" backend docs` - PASS
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` - FAIL, unrelated file `app\api\v1\routers\public\astrologers.py` would be reformatted.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` - FAIL, unrelated existing issues: API SQL boundary allowlist for `astrologers.py`, QA fixture deleting `astral_signs` before dependent profiles, and local `horoscope.db` revision mismatch.
- `.\.venv\Scripts\Activate.ps1; cd backend; alembic upgrade head` - FAIL on local ignored DB because `astral_dignity_type` already exists while `alembic_version` is still `20260513_0087`.

## Commands not run

None intentionally skipped. Full-suite and local DB checks were attempted and failed for non-story issues documented above.

## Legacy / DRY evidence

- Canonical SQL table is `astral_prediction_daily_planet_profiles`.
- No active SQLAlchemy model maps to `planet_profiles`.
- No compatibility alias, view, dual-read or dual-write was added.
- Remaining active-code hits for `"planet_profiles"` are runtime mapping/count labels or negative assertions proving the old table is absent.
- Historical Alembic revisions retain old-table references before the rename migration, which is required for upgrade/downgrade history.

## Remaining risks

- Full backend suite is not green in the current worktree because of pre-existing/out-of-scope issues listed under commands run.
- Local ignored `backend/horoscope.db` is inconsistent around the untracked `20260513_0088` migration; temp-DB Alembic validation for this story passes.

## Reviewer focus

- Review the Alembic rename/downgrade sequence and index names.
- Confirm the chosen SQL name is acceptable while retaining Python runtime names like `planet_profiles`.
- Treat full-suite failures separately from this table rename unless the review scope is expanded.
