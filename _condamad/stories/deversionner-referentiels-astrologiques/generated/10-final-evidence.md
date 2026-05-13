# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: `deversionner-referentiels-astrologiques`
- Source story: `_condamad/stories/deversionner-referentiels-astrologiques/00-story.md`
- Capsule path: `_condamad/stories/deversionner-referentiels-astrologiques/`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: pre-existing `.codex-artifacts/**` modifications and `output/`.
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrails: `RG-091` and new `RG-092` applicable.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Generated from user request. |
| `generated/01-execution-brief.md` | yes | yes | PASS | |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | |
| `generated/04-target-files.md` | yes | yes | PASS | |
| `generated/06-validation-plan.md` | yes | yes | PASS | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | |
| `generated/10-final-evidence.md` | yes | yes | PASS | In progress. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `reference.py`, `prediction_reference.py`, migration `20260512_0086` remove structural version ownership. | Schema assertions in `test_reference_data_migrations.py`; model guard in `test_prediction_reference_repository.py`. | PASS | |
| AC2 | Unique constraints moved to stable keys: `code` for planets/signs/aspects/astro_points and `number` for houses. | Migration upgrade/downgrade tests passed. | PASS | |
| AC3 | Profiles and weights now carry explicit `reference_version_id`; sign rulerships/categories/rulesets remain versioned. | Repository and seed integration tests passed. | PASS | |
| AC4 | `reference_seed_service.py` no longer clones structural rows for V2 and repairs only versioned data. | `test_seed_31_prediction_v2.py` passed. | PASS | |
| AC5 | `prediction_reference_repository.py` filters profiles/weights by their own version and loads structures globally. | `test_prediction_reference_repository.py` passed. | PASS | |
| AC6 | Added model guard plus `RG-092`; targeted scan has zero active structural-version hits. | `rg` zero-hit scan and `git diff --check` passed. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/infra/db/models/reference.py` | modified | Remove structural `reference_version_id` fields and relationships. | AC1, AC2 |
| `backend/app/infra/db/models/prediction_reference.py` | modified | Add explicit version ownership to profiles and weights; keep astro points stable. | AC1, AC3 |
| `backend/app/infra/db/repositories/reference_repository.py` | modified | Seed and read stable vocabulary globally. | AC4, AC5 |
| `backend/app/infra/db/repositories/prediction_reference_repository.py` | modified | Filter versioned data via profile/weight/category/rulership tables. | AC3, AC5 |
| `backend/app/services/prediction/reference_seed_service.py` | modified | Stop cloning stable structure rows and seed V2 parametric data by version. | AC4 |
| `backend/app/services/reference_data_service.py` | modified | Clone versions without duplicating structures. | AC4 |
| `backend/app/services/b2b/astrology_service.py` | modified | Read signs without structural version predicate. | AC5 |
| `backend/migrations/versions/20260307_0032_migration_a_prediction_reference_tables.py` | modified | Name legacy unique constraints for deterministic later migration. | AC2, AC3 |
| `backend/migrations/versions/20260512_0086_deversion_astrology_structures.py` | added | Deduplicate structures, remap FKs, add parametric version columns, drop structural version columns. | AC1-AC4 |
| Backend tests listed below | modified | Cover model, repository, seed, and migration behavior. | AC1-AC6 |
| `_condamad/stories/regression-guardrails.md` | modified | Add `RG-092`. | AC6 |
| `_condamad/stories/story-status.md` | modified | Register story as ready to review. | AC6 |

## Files deleted

None.

## Tests added or updated

| File | Purpose |
|---|---|
| `backend/app/tests/unit/test_prediction_reference_repository.py` | Model guard and repository behavior for stable structures/versioned parameters. |
| `backend/app/tests/unit/test_reference_data_service.py` | Stable reference seeding/cloning and parametric immutability behavior. |
| `backend/app/tests/integration/test_reference_data_migrations.py` | Head schema assertions for structural/versioned tables. |
| `backend/app/tests/integration/test_seed_31_prediction_v2.py` | Seed count/idempotence checks with explicit versioned profiles/weights. |
| `backend/app/tests/integration/test_migration_a_prediction_tables.py` | Current migration/index behavior after profile/weight versioning. |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q` | repo root | PASS | 0 | 15 tests passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py app/tests/integration/test_migration_a_prediction_tables.py -q` | repo root | PASS | 0 | 6 tests passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | PASS | 0 | Formatting completed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py app/tests/integration/test_migration_a_prediction_tables.py -q` | repo root | PASS | 0 | 21 tests passed after final formatting. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(app.title)"` | repo root | PASS | 0 | App imports and reports `horoscope-backend`. |
| `rg -n "PlanetModel\.reference_version_id|SignModel\.reference_version_id|HouseModel\.reference_version_id|AspectModel\.reference_version_id|AstroPointModel\.reference_version_id|PlanetModel\(reference_version_id|SignModel\(reference_version_id|HouseModel\(reference_version_id|AspectModel\(reference_version_id|AstroPointModel\(reference_version_id|clone_version_data" backend/app backend/tests` | repo root | PASS | 1 | Zero active hits. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only for existing files. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | yes | Full suite reached an unrelated architecture guard failure after `1102 passed, 2 skipped`: `test_api_sql_boundary_debt_matches_exact_allowlist` reports pre-existing direct SQL debt in `backend/app/api/v1/routers/public/astrologers.py`, a file not changed by this story. | PASS_WITH_LIMITATIONS until that separate guard debt is resolved. | Targeted story tests, migrations, lint, app import, and No Legacy scans all passed. |

## DRY / No Legacy evidence

| Pattern | Classification | Action | Status |
|---|---|---|---|
| Structural model/version references scan | active legacy absent | Zero hits for `PlanetModel.reference_version_id`, structural constructors with `reference_version_id`, and `clone_version_data`. | PASS |
| `reference_version_id` in `reference.py` helper | allowed parametric lock helper | `_ensure_reference_version_is_mutable` remains for versioned parametric models only. | PASS |
| `reference_version_id` in prediction models/repositories/seed | canonical versioned parameter data | Hits are on profiles, weights, categories, rulerships, rulesets, and seed counting. | PASS |

## Diff review

`git diff --check` passed. Diff is scoped to backend reference models/repositories/services/tests/migrations plus CONDAMAD evidence/guardrails. Pre-existing `.codex-artifacts/**` and `output/` remain unrelated user changes.

## Final worktree status

Recorded in final response; `git status --short` includes expected story files, pre-existing `.codex-artifacts/**`, and pre-existing `output/`.

## Remaining risks

Full backend suite is limited by an unrelated API SQL boundary guard failure in `public/astrologers.py`.

## Suggested reviewer focus

Review the Alembic remapping/deduplication logic in `20260512_0086`, especially FK remaps from duplicate structural rows to canonical stable rows.
