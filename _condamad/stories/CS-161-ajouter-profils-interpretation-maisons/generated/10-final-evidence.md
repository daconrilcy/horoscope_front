# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: `CS-161-ajouter-profils-interpretation-maisons`
- Source story: `_condamad/stories/CS-161-ajouter-profils-interpretation-maisons/00-story.md`
- Capsule path: `_condamad/stories/CS-161-ajouter-profils-interpretation-maisons`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: `?? "docs/recherches astro/house_interpretation_vocabulary.json"`
- Pre-existing dirty files: `docs/recherches astro/house_interpretation_vocabulary.json`
- AGENTS.md files considered: root `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | generated from user request |
| `generated/01-execution-brief.md` | yes | yes | PASS | |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | |
| `generated/04-target-files.md` | yes | yes | PASS | |
| `generated/06-validation-plan.md` | yes | yes | PASS | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | |
| `generated/10-final-evidence.md` | yes | yes | PASS | |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/migrations/versions/20260514_0096_create_house_interpretation_profiles.py` creates `house_interpretation_profiles`; `backend/app/infra/db/models/interpretation_reference.py` maps all editorial fields. | `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_reference_data_migrations.py` PASS. | PASS | JSON fields are stored as `Text` columns with `_json` names. |
| AC2 | FK constraints to `reference_versions` and `astral_houses`; unique constraint on `(reference_version_id, house_id, language, tradition)` in model and migration. | Model and migration tests inspect constraints, foreign keys, and locked-version update rejection. | PASS | Updates are protected by `_ensure_reference_version_is_mutable`. |
| AC3 | No `domain/astrology` or prediction scoring consumer was added; documentation records the separation. | `rg -n "house_interpretation_profiles|HouseInterpretationProfileModel" app/domain/astrology -g "*.py"` zero-hit; existing table-name tests pass. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/infra/db/models/interpretation_reference.py` | added | SQLAlchemy model for editorial house interpretation profiles. | AC1, AC2 |
| `backend/migrations/versions/20260514_0096_create_house_interpretation_profiles.py` | added | Alembic table creation. | AC1, AC2 |
| `backend/app/infra/db/models/__init__.py` | modified | Export model for SQLAlchemy registry import coverage. | AC1 |
| `backend/app/tests/unit/test_prediction_reference_repository.py` | modified | Model contract test. | AC1, AC2, AC3 |
| `backend/app/tests/integration/test_reference_data_migrations.py` | modified | Alembic schema regression test. | AC1, AC2 |
| `docs/tables-maisons-et-roles.md` | modified | Current schema documentation and responsibility separation. | AC3 |
| `_condamad/stories/story-status.md` | modified | Register new story status. | evidence |
| `_condamad/stories/CS-161-ajouter-profils-interpretation-maisons/**` | added | CONDAMAD capsule and evidence. | evidence |

## Files deleted

None.

## Tests added or updated

- Added model contract assertions for `HouseInterpretationProfileModel`.
- Added locked-version update rejection coverage for `HouseInterpretationProfileModel`.
- Updated migration integration test to assert table columns, FKs and unique constraint at Alembic head.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | one pre-existing untracked JSON file |
| `.\.venv\Scripts\Activate.ps1; cd backend; alembic heads` | repo root | PASS | 0 | current Alembic head is `20260514_0096` |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_reference_data_migrations.py` | repo root | PASS | 0 | 13 tests passed, 9 known SQLAlchemy reflection warnings |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | PASS | 0 | final run: 1301 files left unchanged |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | all checks passed |
| `rg -n "house_interpretation_profiles\|HouseInterpretationProfileModel" app/domain/astrology -g "*.py"` | `backend` | PASS | 1 | zero hits, command exits 1 for no matches |
| `rg -n "AstroCharacteristicModel\|astro_characteristics" app tests -g "*.py"` | `backend` | PASS | 0 | only expected migration test assertions proving old table removal |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(app.title)"` | repo root | PASS | 0 | imported FastAPI app, title `horoscope-backend` |
| `git diff --check` | repo root | PASS | 0 | no whitespace errors; line-ending warnings only |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | conditional | Timed out after 604 seconds in this environment. | Full-suite regressions outside the reference/migration surface may remain undetected. | Targeted model + migration tests, lint, import guard, app import check. |

## DRY / No Legacy evidence

- Dedicated table introduced; no keywords added to `astral_houses`.
- No generic `astro_characteristics` model/table reintroduced.
- No `domain/astrology` consumer of `house_interpretation_profiles`.
- Existing product tables `astral_prediction_daily_house_profiles` and `astral_house_category_weights` remain unchanged.
- Migration no longer silently returns when a partial `house_interpretation_profiles` table exists.

## Diff review

- Scope reviewed with `git diff --stat`.
- No frontend files changed.
- Pre-existing untracked `docs/recherches astro/house_interpretation_vocabulary.json` left untouched.

## Review findings fixed

| Finding | Source | Status | Correction |
|---|---|---|---|
| Story status inconsistent | Story Conformance Reviewer | FIXED | `00-story.md` aligned to `ready-to-review`. |
| Final evidence recorded old Alembic head | Story Conformance Reviewer | FIXED | Evidence refreshed to `20260514_0096`. |
| Migration could silently accept a partial table | Technical Risk Reviewer | FIXED | Removed early return on existing table. |
| Locked-version behavior not directly tested | Technical Risk Reviewer | FIXED | Added update rejection test for `HouseInterpretationProfileModel`. |
| Untracked research JSON in worktree | Technical Risk Reviewer | REJECTED_AS_STORY_FINDING | Pre-existing user file, documented and left untouched/out of scope. |
| Story source status not aligned with final `done` registry status | Main re-review | FIXED | `00-story.md` now says `Status: done`. |

## Final worktree status

```text
 M _condamad/stories/story-status.md
 M backend/app/infra/db/models/__init__.py
 M backend/app/tests/integration/test_reference_data_migrations.py
 M backend/app/tests/unit/test_prediction_reference_repository.py
 M docs/tables-maisons-et-roles.md
?? _condamad/stories/CS-161-ajouter-profils-interpretation-maisons/
?? backend/app/infra/db/models/interpretation_reference.py
?? backend/migrations/versions/20260514_0096_create_house_interpretation_profiles.py
?? "docs/recherches astro/house_interpretation_vocabulary.json"
```

The untracked JSON file is pre-existing and intentionally out of scope.

## Remaining risks

Full backend `pytest -q` timed out after 604 seconds; targeted reference/migration validation passed.

## Suggested reviewer focus

Review table boundaries: editorial vocabulary must remain separate from runtime astrology and prediction scoring. Confirm the accepted full-suite timeout limitation is acceptable for this narrow DB reference change.
