# Final Evidence — CS-016

## Story status

- Validation outcome: PASS
- Review outcome: CLEAN
- Final status: done
- Ready for review: completed
- Story key: CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy
- Source story: `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/00-story.md`
- Capsule path: `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/stories/regression-guardrails.md` modified, `_condamad/stories/story-status.md` modified, CS-016/CS-017/CS-018 capsule directories untracked.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/`, `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/`, `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/`.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific brief. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All ACs mapped and passed. |
| `generated/04-target-files.md` | yes | yes | PASS | Targeted file/search map. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable validation commands. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-036 guardrails. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `persisted-dto-classification.md`, `persisted-dto-before.md`, `persisted-dto-after.md`. | `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` PASS. | PASS | DTOs classified under `app.domain.prediction`. |
| AC2 | `backend/app/tests/unit/test_daily_prediction_guardrails.py` adds repository-level forbidden import guard. | `rg -n "app\.prediction\.persisted\|app\.prediction\.context" app/infra/db/repositories -g "*.py"` zero-hit; guard test PASS. | PASS | Repositories import canonical domain DTOs only. |
| AC3 | No `backend/app/prediction` owner or duplicate DTO added. | `rg -n "from app\.prediction\.persisted\|from app\.prediction\.context" app tests -g "*.py"` zero-hit; `rg --files app/prediction` path absent. | PASS | No shim/re-export/fallback. |
| AC4 | Persistence code unchanged except guard; canonical DTO shape preserved. | `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` PASS. | PASS | 4 tests passed. |
| AC5 | Daily API snapshot compatibility preserved. | `pytest -q app/tests/integration/test_daily_prediction_api.py` PASS. | PASS | 25 tests passed. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/tests/unit/test_daily_prediction_guardrails.py` | modified | Add RG-036 AST guard for repository imports of legacy persisted DTOs. | AC2, AC3 |
| `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/00-story.md` | modified | Mark status/tasks ready for review. | AC1-AC5 |
| `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-classification.md` | added | Persist canonical owner decisions. | AC1, AC3 |
| `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-before.md` | added | Baseline inventory. | AC1 |
| `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-after.md` | added | After inventory and guard evidence. | AC1-AC3 |
| `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/generated/*` | added/modified | Capsule, validation and evidence. | AC1-AC5 |
| `_condamad/stories/story-status.md` | modified | Set CS-016 to `ready-to-review`. | AC1-AC5 |

## Files deleted

- None.

## Tests added or updated

- Updated `backend/app/tests/unit/test_daily_prediction_guardrails.py` with `test_prediction_repositories_do_not_import_legacy_persisted_dtos`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy\00-story.md --root . --story-key CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy --with-optional` | repo root, venv active | PASS | 0 | Capsule generated. |
| `ruff format app/tests/unit/test_daily_prediction_guardrails.py` | `backend`, venv active | PASS | 0 | 1 file reformatted. |
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend`, venv active | PASS | 0 | 15 passed. |
| `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` | `backend`, venv active | PASS | 0 | 4 passed. |
| `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend`, venv active | PASS | 0 | 25 passed. |
| `python -c "from app.main import app; print(app.title)"` | `backend`, venv active | PASS | 0 | Backend app import smoke returned `horoscope-backend`. |
| `rg -n "app\.prediction\.persisted\|app\.prediction\.context" app/infra/db/repositories -g "*.py"` | `backend`, venv active | PASS | 1 | No hits. |
| `rg -n "from app\.prediction\.persisted\|from app\.prediction\.context" app tests -g "*.py"` | `backend`, venv active | PASS | 1 | No hits. |
| `rg --files app/prediction` | `backend`, venv active | PASS | 1 | Legacy path absent. |
| `ruff check app/infra/db/repositories app/tests` | `backend`, venv active | PASS | 0 | All checks passed. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |
| `git diff --stat` | repo root | PASS | 0 | Story-scoped tracked diff plus pre-existing tracked docs. |
| `git status --short` | repo root | PASS | 0 | Final state recorded below. |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `app.prediction.persisted_*` in repositories | none | active legacy absent | Guarded by pytest and scan. | PASS |
| `app.prediction.context` in repositories | none | active legacy absent | Guarded by pytest and scan. | PASS |
| `from app.prediction.persisted*` in app/tests | none | active legacy absent | Scan zero-hit. | PASS |
| `backend/app/prediction` | path absent | legacy namespace absent | No recreation. | PASS |
| `app.domain.prediction.persisted_*` | repositories/services/tests | canonical owner usage | Preserved. | PASS |

## Diff review

- `git diff --check`: PASS, CRLF warnings only.
- `git diff --stat`: tracked diff includes `backend/app/tests/unit/test_daily_prediction_guardrails.py`; `_condamad/stories/regression-guardrails.md` and `_condamad/stories/story-status.md` were already dirty before implementation.
- Untracked CS-016 capsule contains expected story evidence files.
- Untracked CS-017 and CS-018 capsule directories are pre-existing and unrelated.

## Final worktree status

Recorded after implementation:

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M backend/app/tests/unit/test_daily_prediction_guardrails.py
?? _condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/
?? _condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/
?? _condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/
```

## Remaining risks

- The current worktree already had the DTO migration mostly applied before CS-016 execution; this story therefore finalizes ownership evidence and guardrails rather than moving runtime code.
- `_condamad/stories/regression-guardrails.md`, CS-017 and CS-018 are dirty/untracked pre-existing surfaces and were not modified for this story.

## Review closure

- Review artifact: `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/generated/11-code-review.md`
- Review verdict: CLEAN
- Review/fix iterations: 1
- Findings fixed during review loop: none
- Story status synchronized to `done` in `_condamad/stories/story-status.md`.

## Suggested reviewer focus

- Confirm `app.domain.prediction` is the intended long-term owner for these DTOs.
- Review the new repository-level AST guard for the exact forbidden legacy import modules.
- Confirm the pre-existing dirty files outside CS-016 are acceptable in the review context.
