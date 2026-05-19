# Final Evidence

## Story status

- Validation outcome: Passed after review/fix loop
- Ready for review: no - final review verdict is `CLEAN`
- Story key: `CS-190-seed-astral-dignity-reference-runtime`
- Source story: user prompt on 2026-05-19
- Capsule path: `_condamad/stories/CS-190-seed-astral-dignity-reference-runtime`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: JSON seed files were already dirty/untracked from previous work and treated as story input.
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrails consulted: `_condamad/stories/regression-guardrails.md`

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Added SQLAlchemy models in `backend/app/infra/db/models/dignity_reference.py` and model registry exports. | `pytest --long backend/app/tests/integration/test_reference_data_migrations.py -q` | Passed | Includes reference and runtime tables. |
| AC2 | Added `sync_astral_dignity_seed_data` and wired it into `ReferenceDataService` and the prediction seed flow. | `pytest backend/app/tests/unit/test_dignity_reference_seed.py ... -q` | Passed | Local active reference seed completed for `2.0.0`. |
| AC3 | Added `AstralChartPlanetDignityResultModel` and `DignityReferenceRepository` upsert/fetch methods. | `test_dignity_repository_reads_weights_and_upserts_runtime_result` | Passed | Runtime table remains empty after seed. |
| AC4 | Added Alembic migrations `20260519_0128` and `20260519_0129` with FK/unique constraints. | Migration integration suite now asserts critical columns, FK targets and unique constraints for dignity score profiles, dignity rules and runtime results. | Passed | `0129` reconciles existing local DBs that had applied early `0128`. |
| AC5 | Added focused unit tests and updated migration tests. | Ruff + pytest commands below | Passed | |

## Files changed

- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/repositories/dignity_reference_repository.py`
- `backend/app/infra/db/repositories/__init__.py`
- `backend/app/services/reference_data/dignity_seed_service.py`
- `backend/app/services/reference_data_service.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/migrations/versions/20260519_0128_create_astral_dignity_tables.py`
- `backend/migrations/versions/20260519_0129_reconcile_astral_dignity_lookup_sort_order.py`
- `backend/app/tests/unit/test_dignity_reference_seed.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/unit/test_backend_db_test_harness.py`

## Files deleted

- None.

## Tests added or updated

- Added `backend/app/tests/unit/test_dignity_reference_seed.py`.
- Updated `backend/app/tests/integration/test_reference_data_migrations.py`.
- Updated `backend/app/tests/unit/test_backend_db_test_harness.py` to classify the new isolated `create_all` usage required by `RG-011`.

## Commands run

- `.\.venv\Scripts\Activate.ps1; pytest backend/app/tests/unit/test_dignity_reference_seed.py -q`
- `.\.venv\Scripts\Activate.ps1; pytest --long backend/app/tests/integration/test_reference_data_migrations.py -q`
- `.\.venv\Scripts\Activate.ps1; pytest backend/app/tests/unit/test_dignity_reference_seed.py backend/app/tests/unit/test_reference_data_service.py backend/app/tests/unit/test_prediction_reference_repository.py -q`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff check .`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .`
- `.\.venv\Scripts\Activate.ps1; pytest backend/app/tests/unit/test_backend_db_test_harness.py backend/app/tests/unit/test_backend_noop_tests.py -q`
- `git diff --check`
- `rg -n "astral_essential_dignity_score_profiles|accidental_dignity_type_code" backend docs/db_seeder/astrology`
- `rg -n "score_profile_code" backend/app/infra/db/models backend/migrations docs/db_seeder/astrology`
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-code-review/scripts/condamad_review_validate.py .agents/skills/condamad-code-review`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 8019` then `Invoke-WebRequest http://127.0.0.1:8019/docs` returned `HTTP 200`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; alembic upgrade head`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -` with `ReferenceDataService.seed_reference_version(db)`
- Local seed count check: `astral_sources=6`, `astral_diginity_score_profiles=5`, `astral_essential_dignity_rules=38`, `astral_accidental_dignity_rules=41`, `astral_chart_planet_dignity_results=0`.

## Commands skipped or blocked

- Full `pytest -q --long` was not run; scope stayed on migration, reference seed, and repository regression surfaces.
- Two early commands were launched from `backend` with the root venv path and printed activation errors; both were rerun correctly from repository root and are not counted as validation evidence.

## DRY / No Legacy evidence

- Seed logic centralized in `sync_astral_dignity_seed_data`.
- Score profiles consistently use the requested table spelling `astral_diginity_score_profiles`.
- No duplicate `astral_essential_dignity_score_profiles` backend reference remains.
- `score_profile_code` is absent from DB models, migrations and seed JSON; repository parameters may still resolve profile codes to DB IDs.

## Review/fix loop

- Iteration 1 verdict: `CHANGES_REQUESTED`.
  - Fixed missing direct migration constraint validation for AC4.
  - Fixed missing `RG-011` create_all classification for `test_dignity_reference_seed.py`.
  - Fixed No Legacy evidence scan that mixed forbidden DB columns with accepted repository lookup parameters.
- Iteration 2 verdict: `CLEAN`.
  - Review evidence: `generated/11-code-review.md`.

## Diff review

- Migrations create schema and preserve local DB compatibility through `0129`.
- Runtime dignity result table has no reference seed rows and has the requested functional uniqueness.

## Final worktree status

- Backend implementation and CONDAMAD capsule files are modified/untracked as expected.
- Existing JSON seed files remain untracked/modified from the prior JSON work and are part of this story input.

## Remaining risks

- `condition_json` still stores nested FK references as JSON values; database-level FK enforcement inside JSON is not possible with the current schema.

## Suggested reviewer focus

- Validate the intentionally misspelled table name `astral_diginity_score_profiles` before merge.
- Review whether `astral_sources` should remain distinct from the older `astral_reference_sources`.
