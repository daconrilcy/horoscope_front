# CONDAMAD Code Review

## Review target

- Story: `CS-012-ajouter-garde-anti-croissance-app-prediction`
- Source: `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/00-story.md`
- Reviewer date: 2026-05-04

## Inputs reviewed

- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/00-story.md`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/06-validation-plan.md`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/10-final-evidence.md`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- Untracked context inspected: `.agents/skills/condamad-review-fix-story/`, `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/` listed as out of target.

## Diff summary

- Code change is scoped to `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
- CS-012 adds a persistent allowlist artifact for `backend/app/prediction`.
- Governance changes add `RG-032` and track CS-012 as `done` in `story-status.md`.
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` has exact line-number realignment only, required to keep the full backend suite passing after route line drift.
- `CS-013` and `.agents/skills/condamad-review-fix-story/` are present in the dirty worktree but are outside this review target.

## Review layers

- Diff integrity: no unexpected application runtime changes found; unrelated untracked paths were identified and scoped out.
- Acceptance audit: AC1-AC5 are mapped to executable guard evidence.
- Validation audit: required targeted lint, targeted tests, forbidden import scan, SQL boundary guard, and full backend suite pass.
- DRY / No Legacy audit: no wildcard, folder-wide exception, shim, alias, fallback, or re-export introduced by CS-012.
- Regression guardrail audit: `RG-016`, `RG-017`, `RG-032`, and the affected SQL guardrail `RG-008` are covered by executable evidence.

## Findings

No actionable findings.

## Acceptance audit

| AC | Review result | Evidence |
|---|---|---|
| AC1 | PASS | `test_prediction_namespace_python_inventory_does_not_grow` reads the persisted allowlist and compares exact Python inventory. |
| AC2 | PASS | A new Python file under `backend/app/prediction` fails unless added to the allowlist. |
| AC3 | PASS | AST guards block `app.api`, `fastapi`, `app.core.config`, `app.infra`, SQLAlchemy, `AIEngineAdapter`, `LLMRuntime`, `settings`, and `LLMNarrator`. |
| AC4 | PASS | Exception register exists; active exception rows require non-permanent exit conditions. No active exceptions remain. |
| AC5 | PASS | LLM narrator deprecation guard passes with the prediction guard. |

## Validation audit

Reviewer commands run:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/tests/unit/test_daily_prediction_guardrails.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist
git diff --check
rg -n "from app\\.api|import app\\.api|fastapi|AIEngineAdapter|LLMRuntime|from sqlalchemy|import sqlalchemy|LLMNarrator|from app\\.core\\.config|settings|from app\\.infra|import app\\.infra" app/prediction -g "*.py"
rg --files app/prediction
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q
git status --short
git diff --stat
```

Results:

- `ruff check app/tests/unit/test_daily_prediction_guardrails.py`: PASS.
- Targeted pytest including CS-012 and SQL allowlist guard: PASS, 17 tests.
- `git diff --check`: PASS with LF-to-CRLF warnings only.
- Forbidden import scan: zero hits; `rg` exit status 1 is expected for zero matches.
- Full `pytest -q`: PASS, 3591 passed and 12 skipped in 702.19 seconds.

## DRY / No Legacy audit

- No duplicate active guard path added.
- No wildcard allowlist or folder-wide exception found.
- The prediction allowlist is a single persistent register consumed by the test.
- No application code under `backend/app/prediction` changed.
- SQL allowlist changes are exact line-number realignment, not a new exception class or widened rule.

## Residual risks

- Existing legacy/fallback terminology remains in `app/prediction`; it is outside this guard-only story and was not introduced here.
- `.agents/skills/condamad-review-fix-story/` remains untracked and outside CS-012.

## Verdict

CLEAN
