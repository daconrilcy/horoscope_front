# CONDAMAD Code Review

## Review target

- Story: `CS-190-seed-astral-dignity-reference-runtime`
- Capsule: `_condamad/stories/CS-190-seed-astral-dignity-reference-runtime`
- Scope reviewed: backend dignity DB models, Alembic migrations, reference seed service, repository, JSON seed files, targeted tests and CONDAMAD evidence.

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- `git status --short`, `git diff --stat`, untracked story files and targeted source/test reads.

## Diff summary

- Added SQLAlchemy models for the dignity reference and runtime/audit tables.
- Added `DignityReferenceRepository` and typed repository inputs/outputs.
- Wired dignity seeding into `ReferenceDataService` and prediction reference seeding.
- Added Alembic revisions `20260519_0128` and `20260519_0129`.
- Added/updated backend unit and migration tests.
- Added new dignity seed JSON files and updated shared astrology JSON seeds.

## Review layers

- Diff integrity: expected backend, seed JSON and CONDAMAD files only.
- Acceptance audit: AC1-AC5 mapped to code and validation evidence.
- Validation audit: reviewer reran lint, format, targeted unit tests, long migration tests, guardrail tests and negative scans.
- DRY / No Legacy audit: no duplicate seed loader; legacy score profile table and accidental code column scans are zero-hit.
- Edge/security/data audit: runtime result table is repository-owned, not seeded, and constrained by chart/planet/profile/version uniqueness.

## Findings

No open findings.

Resolved during review/fix loop:

### CR-001 High - Migration constraints were not directly validated

- Bucket: patch
- Location: `backend/app/tests/integration/test_reference_data_migrations.py`
- Source layer: acceptance / validation
- Evidence: initial migration test asserted new dignity table presence but did not assert the critical columns, FK targets or unique constraints required by AC4.
- Impact: AC4 could pass with missing or weakened DB constraints.
- Fix applied: added focused schema assertions for score profiles, essential rules, accidental rules and runtime result table.

### CR-002 Medium - New create_all test usage was not classified

- Bucket: patch
- Location: `backend/app/tests/unit/test_backend_db_test_harness.py`
- Source layer: regression guardrail `RG-011`
- Evidence: `pytest backend/app/tests/unit/test_backend_db_test_harness.py backend/app/tests/unit/test_backend_noop_tests.py -q` failed because `app/tests/unit/test_dignity_reference_seed.py` used `Base.metadata.create_all` without allowlist classification.
- Impact: the DB test harness guardrail could not pass for the story.
- Fix applied: classified `app/tests/unit/test_dignity_reference_seed.py` in `APPROVED_CREATE_ALL_PATHS`.

### CR-003 Low - No Legacy scan mixed forbidden DB columns with accepted lookup parameters

- Bucket: patch
- Location: `_condamad/stories/CS-190-seed-astral-dignity-reference-runtime/generated/06-validation-plan.md`
- Source layer: no-legacy / evidence
- Evidence: the planned scan included `score_profile_code` across all backend files even though repository inputs legitimately resolve profile codes to `score_profile_id`.
- Impact: validation evidence could produce false failures.
- Fix applied: split the scan into DB-schema/seed checks and legacy table/code-column checks.

## Acceptance audit

- AC1: Passed. Dignity JSON tables are represented by SQLAlchemy models under `backend/app/infra/db/models/dignity_reference.py`.
- AC2: Passed. `sync_astral_dignity_seed_data` is called from canonical reference seed paths.
- AC3: Passed. `AstralChartPlanetDignityResultModel` and repository upsert/fetch exist; seed tests prove runtime rows are not required seed data.
- AC4: Passed after CR-001. Migration test now asserts critical FK targets and unique constraints.
- AC5: Passed. Targeted seed, repository, migration and guardrail tests pass.

## Validation audit

- `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff check .` - passed.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .` - passed.
- `.\.venv\Scripts\Activate.ps1; pytest backend/app/tests/unit/test_dignity_reference_seed.py backend/app/tests/unit/test_reference_data_service.py backend/app/tests/unit/test_prediction_reference_repository.py -q` - passed, 54 tests.
- `.\.venv\Scripts\Activate.ps1; pytest --long backend/app/tests/integration/test_reference_data_migrations.py -q` - passed, 5 tests.
- `.\.venv\Scripts\Activate.ps1; pytest backend/app/tests/unit/test_backend_db_test_harness.py backend/app/tests/unit/test_backend_noop_tests.py -q` - passed, 7 tests.
- `git diff --check` - passed.
- `rg -n "astral_essential_dignity_score_profiles|accidental_dignity_type_code" backend docs/db_seeder/astrology` - zero hits.
- `rg -n "score_profile_code" backend/app/infra/db/models backend/migrations docs/db_seeder/astrology` - zero hits.

## DRY / No Legacy audit

- Seed logic is centralized in `sync_astral_dignity_seed_data`.
- No duplicate legacy score profile table is active.
- DB schema uses linked IDs for score profiles and accidental dignity types.
- Repository input code lookup is accepted because it resolves caller-facing codes to DB IDs.

## Commands run by reviewer

- `git status --short`
- `git diff --stat`
- `git ls-files --others --exclude-standard`
- All validation commands listed above.

## Residual risks

- `condition_json` stores nested condition references as JSON values; relational FK enforcement inside JSON remains out of scope for the current schema.

## Verdict

CLEAN
