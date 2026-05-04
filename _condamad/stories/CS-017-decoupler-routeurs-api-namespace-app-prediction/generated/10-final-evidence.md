# Final Evidence - CS-017

## Story status

- Validation outcome: PASS
- Ready for review: completed
- Review verdict: CLEAN
- Story key: CS-017-decoupler-routeurs-api-namespace-app-prediction
- Source story: `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/00-story.md`
- Capsule path: `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `00-story.md`
- Initial `git status --short`: `_condamad/stories/regression-guardrails.md` modified, `_condamad/stories/story-status.md` modified, CS-017 and CS-018 story directories untracked.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/`, `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/`.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific brief. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All ACs mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and searches recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands concrete and executed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | CS-017 guardrails recorded. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Routeurs prediction preserved; `openapi-before.json` and `openapi-after.json` persisted. | `pytest -q app/tests/integration/test_daily_prediction_api.py` PASS; `pytest -q` PASS; OpenAPI compare count `0`. | PASS | No runtime contract diff. |
| AC2 | `backend/app/api` has no `app.prediction` import; AST guard added. | `rg -n "app\.prediction" app/api -g "*.py"` zero-hit; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` PASS. | PASS | Guard is API-scoped. |
| AC3 | Routeurs consume `app.domain.prediction` and `app.services.prediction`; no API business owner added. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` PASS; `ruff check .` PASS; diff reviewed. | PASS | Route import convergence was already present in current worktree. |
| AC4 | Horoscope daily narration path remains through service enrichment. | `pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py` PASS; `pytest -q` PASS. | PASS | No narration behavior change. |
| AC5 | OpenAPI snapshots and import audit persisted. | `Compare-Object` produced zero differences; `api-import-audit.md` records zero-hit import scan. | PASS | Snapshots are full OpenAPI JSON. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/tests/unit/test_daily_prediction_guardrails.py` | modified | Add API-specific AST guard against `app.prediction` imports. | AC2, AC3 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/00-story.md` | modified | Mark story ready for review and complete task checkboxes. | AC1-AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/01-execution-brief.md` | added | Execution brief. | AC1-AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/03-acceptance-traceability.md` | added | AC traceability. | AC1-AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/04-target-files.md` | added | Target file map. | AC1-AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/05-implementation-plan.md` | added | Implementation plan. | AC1-AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/06-validation-plan.md` | added | Validation plan. | AC1-AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/07-no-legacy-dry-guardrails.md` | added | No Legacy guardrails. | AC2, AC3 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/09-dev-log.md` | added | Dev log. | AC1-AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/10-final-evidence.md` | added | Final evidence. | AC1-AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/openapi-before.json` | added | Runtime contract baseline. | AC1, AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/openapi-after.json` | added | Runtime contract after snapshot. | AC1, AC5 |
| `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/api-import-audit.md` | added | API import audit. | AC2, AC3 |
| `_condamad/stories/story-status.md` | modified | Set CS-017 to `ready-to-review`. | AC1-AC5 |

## Files deleted

- None.

## Tests added or updated

- Added `test_api_prediction_routers_do_not_import_legacy_prediction_namespace` in `backend/app/tests/unit/test_daily_prediction_guardrails.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-dev-story/scripts/condamad_prepare.py _condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/00-story.md --root . --story-key CS-017-decoupler-routeurs-api-namespace-app-prediction --with-optional` | repo root | PASS | 0 | Capsule generated. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -` | repo root | PASS | 0 | Wrote `openapi-before.json` and `openapi-after.json` from `app.openapi()`. |
| `Compare-Object ...openapi-before.json ...openapi-after.json` | repo root | PASS | 0 | No differences; count `0`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | repo root | PASS | 0 | 16 passed after format. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_daily_prediction_api.py` | repo root | PASS | 0 | 25 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py` | repo root | PASS | 0 | 2 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "app\.prediction" app/api -g "*.py"` | repo root | PASS | 0 | Zero-hit scan normalized from `rg` exit 1 to success. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app/tests/unit/test_daily_prediction_guardrails.py` | repo root | PASS | 0 | 1 touched file reformatted. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | FAIL | 124 | First attempt timed out after 10 minutes with no useful output. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS | 0 | 3595 passed, 12 skipped in 697.62s. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` | repo root | PASS | 0 | 1255 files already formatted. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; app.openapi(); print('app import/openapi OK')"` | repo root | PASS | 0 | App import and OpenAPI generation OK. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed; untracked CS-017 capsule not shown by Git stat. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git emitted CRLF conversion warnings only. |
| `git status --short` | repo root | PASS | 0 | Expected dirty files recorded below. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | repo root | PASS | 0 | Reviewer rerun: 16 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_daily_prediction_api.py` | repo root | PASS | 0 | Reviewer rerun: 25 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py` | repo root | PASS | 0 | Reviewer rerun: 2 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` | repo root | PASS | 0 | Reviewer rerun: 1255 files already formatted. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | Reviewer rerun: all checks passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "app\.prediction" app/api -g "*.py"` | repo root | PASS | 0 | Reviewer rerun: zero-hit scan normalized from `rg` exit 1 to success. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS | 0 | Reviewer rerun: 3595 passed, 12 skipped in 521.34s. |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

| Pattern | File/scope | Classification | Action | Status |
|---|---|---|---|---|
| `app.prediction` | `backend/app/api/**/*.py` | zero active hits | none | PASS |
| `legacy|compat|shim|fallback|deprecated|alias` | touched API/guard files | expected guard terminology and pre-existing fallback tests only | no wrapper, alias, re-export, or route fallback introduced | PASS |
| `app.domain.prediction` imports in routeurs | `public/predictions.py`, `internal/llm/qa.py` | canonical owner usage | preserve | PASS |

## Diff review

- `git diff --stat`: story registry rows, CS-017 status row, and guard test change are expected; untracked CS-017 capsule files are expected.
- `git diff --check`: PASS with CRLF conversion warnings only.
- Route handlers were not changed; no API payload, path, status code, or OpenAPI schema change was introduced.
- CS-018 remains present as pre-existing untracked story work and was not modified for this implementation.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M backend/app/tests/unit/test_daily_prediction_guardrails.py
?? _condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/
?? _condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/
```

## Remaining risks

- Aucun risque restant identifie.

## Suggested reviewer focus

- Review completed in `generated/11-code-review.md`; verdict `CLEAN`.
