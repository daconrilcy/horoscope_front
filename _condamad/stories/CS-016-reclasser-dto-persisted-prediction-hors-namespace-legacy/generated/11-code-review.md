# CONDAMAD Code Review

## Review target

- Story: `CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy`
- Capsule: `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy`
- Reviewed implementation surface:
  - `backend/app/tests/unit/test_daily_prediction_guardrails.py`
  - `backend/app/infra/db/repositories/daily_prediction_repository.py`
  - `backend/app/infra/db/repositories/prediction_schemas.py`
  - `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
  - `backend/app/domain/prediction/persisted_snapshot.py`
  - `backend/app/domain/prediction/persisted_relative_score.py`
  - `backend/app/domain/prediction/persisted_baseline.py`
  - `backend/app/domain/prediction/context.py`
  - CS-016 capsule evidence files

## Inputs reviewed

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/04-target-files.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `persisted-dto-classification.md`
- `persisted-dto-before.md`
- `persisted-dto-after.md`
- `git status --short`, `git diff --stat`, targeted diffs and repository scans

## Diff summary

- Added a repository-level AST guard in `backend/app/tests/unit/test_daily_prediction_guardrails.py` to block legacy persisted DTO imports from DB repositories.
- Added CS-016 governance and evidence artifacts.
- `_condamad/stories/regression-guardrails.md` contains RG-036 for persisted prediction DTO ownership.
- `_condamad/stories/story-status.md` is synchronized to `done` for CS-016 after this clean review.
- CS-017 and CS-018 capsule directories remain out of scope and were not reviewed for this verdict.

## Review layers

- Diff integrity: PASS. No application code outside the expected guard file is changed in the tracked diff.
- Acceptance audit: PASS. AC1-AC5 have explicit evidence and current validation.
- Validation audit: PASS. Required commands were rerun in the repository environment with the venv activated for Python commands.
- DRY / No Legacy audit: PASS. Legacy imports and legacy `app/prediction` files are absent in the targeted scans.
- Edge-case and failure audit: PASS. The new AST guard covers both `from ... import ...` and direct `import ...` forms for the forbidden modules.
- Security and data audit: PASS. No secrets, auth, SQL schema, migration, or API contract change is introduced.

## Findings

Aucun finding actionnable.

## Acceptance audit

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `persisted-dto-classification.md`, before/after inventories, persistence tests passing. |
| AC2 | PASS | Repositories import `app.domain.prediction.*`; repository legacy scan is zero-hit; RG-036 guard test passing. |
| AC3 | PASS | `backend/app/prediction` is absent; active legacy import scan is zero-hit; no shim or duplicate DTO was introduced. |
| AC4 | PASS | `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` passed. |
| AC5 | PASS | `pytest -q app/tests/integration/test_daily_prediction_api.py` passed. |

## Validation audit

| Command | Working directory | Result |
|---|---|---|
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend`, venv active | PASS, 15 passed |
| `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` | `backend`, venv active | PASS, 4 passed |
| `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend`, venv active | PASS, 25 passed |
| `rg -n "app\.prediction\.persisted\|app\.prediction\.context" app/infra/db/repositories -g "*.py"` | `backend` | PASS, zero-hit |
| `rg -n "from app\.prediction\.persisted\|from app\.prediction\.context" app tests -g "*.py"` | `backend` | PASS, zero-hit |
| `rg --files app/prediction` | `backend` | PASS, path absent |
| `ruff check app/infra/db/repositories app/tests` | `backend`, venv active | PASS |
| `git diff --check` | repo root | PASS, CRLF warnings only |
| `python -c "from app.main import app; print(app.title)"` | `backend`, venv active | PASS, `horoscope-backend` |

## DRY / No Legacy audit

- `RG-027`: PASS. The reviewed DTO owner stays under `app.domain.prediction`; no infra import was added to the domain.
- `RG-032`: PASS. No new file was added under `backend/app/prediction`.
- `RG-034`: PASS. `backend/app/prediction` remains absent.
- `RG-036`: PASS. Persisted DTO ownership is documented and repository imports of `app.prediction.persisted_*` / `app.prediction.context` are guarded.

## Commands run by reviewer

- `git status --short`
- `git diff -- backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `git diff -- _condamad/stories/regression-guardrails.md _condamad/stories/story-status.md`
- `rg -n "app\.prediction\.persisted\|app\.prediction\.context" backend/app/infra/db/repositories -g "*.py"`
- `rg -n "from app\.prediction\.persisted\|from app\.prediction\.context" backend/app backend/tests -g "*.py"`
- `rg --files backend/app | rg "(^|/)prediction/(persisted_(snapshot|relative_score|baseline)|context)\.py$"`
- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`
- `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py`
- `pytest -q app/tests/integration/test_daily_prediction_api.py`
- `rg -n "app\.prediction\.persisted\|app\.prediction\.context" app/infra/db/repositories -g "*.py"`
- `rg -n "from app\.prediction\.persisted\|from app\.prediction\.context" app tests -g "*.py"`
- `rg --files app/prediction`
- `ruff check app/infra/db/repositories app/tests`
- `git diff --check`
- `git diff --stat`
- `python -c "from app.main import app; print(app.title)"`

## Residual risks

- The worktree contains out-of-scope CS-017 and CS-018 untracked capsules. They were not included in this CS-016 review.
- The runtime DTO migration was already largely present before the CS-016 closure work; this review validates the final owner evidence, guard and absence of legacy imports.

## Verdict

CLEAN
