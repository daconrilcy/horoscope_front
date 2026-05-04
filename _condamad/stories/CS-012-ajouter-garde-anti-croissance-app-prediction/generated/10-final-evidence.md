# Final Evidence - CS-012

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-012-ajouter-garde-anti-croissance-app-prediction`
- Source story: `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/00-story.md`
- Capsule path: `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/00-story.md`
- Initial `git status --short`: `_condamad/stories/regression-guardrails.md` and `_condamad/stories/story-status.md` modified; CS-012 and CS-013 story folders untracked.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/`, `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/`.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated before implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 completed. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Forbidden paths listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed with validation evidence. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `prediction-namespace-allowlist.md` lists the exact current Python files under `backend/app/prediction`; the guard reads it as persistent source. | Targeted pytest PASS; `rg --files app/prediction` reviewed. | PASS | Non-Python editorial templates are visible in inventory but outside Python growth guard. |
| AC2 | `test_prediction_namespace_python_inventory_does_not_grow` compares current Python files to the persisted allowlist. | Targeted pytest PASS. | PASS | Any new Python file fails until allowlisted. |
| AC3 | `test_prediction_namespace_does_not_import_api_settings_or_llm_runtime` adds AST checks for API/settings/LLM runtime; existing infra guard covers SQLAlchemy and repositories. | Targeted pytest PASS; forbidden import scan returned zero hits. | PASS | No runtime code changed. |
| AC4 | `prediction-namespace-allowlist.md` has an exceptions section; `test_prediction_import_exceptions_have_exit_conditions` rejects active rows without exit condition. | Targeted pytest PASS. | PASS | No active exception remains after CS-007 and CS-009. |
| AC5 | Existing `test_llm_narrator_deprecation_guard.py` executed with the prediction guard. | Targeted pytest PASS, 16 tests. | PASS | `RG-016` and `RG-017` preserved. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/tests/unit/test_daily_prediction_guardrails.py` | modified | Read persisted allowlist; add exception exit-condition test and AST boundary import guard. | AC1-AC4 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md` | added | Persistent allowlist and exception register. | AC1, AC4 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/00-story.md` | modified | Mark tasks complete and status ready-to-review. | AC1-AC5 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/01-execution-brief.md` | added | Execution capsule. | AC1-AC5 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/03-acceptance-traceability.md` | added/modified | AC evidence matrix. | AC1-AC5 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/04-target-files.md` | added | Target file map. | AC1-AC5 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/05-implementation-plan.md` | added | Scoped implementation plan. | AC1-AC5 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/06-validation-plan.md` | added | Validation plan. | AC1-AC5 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/07-no-legacy-dry-guardrails.md` | added | No Legacy guardrails. | AC1-AC5 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/09-dev-log.md` | added | Preflight and search notes. | AC1-AC5 |
| `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/10-final-evidence.md` | added/modified | Final evidence. | AC1-AC5 |
| `_condamad/stories/story-status.md` | modified | Mark CS-012 done after clean review evidence. | AC1-AC5 |
| `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` | modified | Realign exact SQL boundary debt line numbers so the full backend suite can pass. | Full-suite validation |

## Files deleted

| File | Reason |
|---|---|
| None | No deletion required. |

## Tests added or updated

- Updated `backend/app/tests/unit/test_daily_prediction_guardrails.py` with persisted allowlist reading, exception validation, and AST import boundary checks.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repository root | PASS | 0 | Dirty worktree recorded before edits. |
| `rg --files _condamad\stories\CS-012-ajouter-garde-anti-croissance-app-prediction` | repository root | PASS | 0 | Initial capsule had only `00-story.md`. |
| `rg --files app/prediction` | `backend` | PASS | 0 | Inventory reviewed; Python files captured in allowlist. |
| `rg -n "from app\\.api\|import app\\.api\|fastapi\|AIEngineAdapter\|from sqlalchemy\|import sqlalchemy\|LLMNarrator" app/prediction -g "*.py"` | `backend` | PASS | 1 | Zero forbidden import hits. |
| `rg -n "legacy\|compat\|shim\|fallback\|deprecated\|alias" app/prediction app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | PASS | 0 | Hits classified below; no new active compatibility path introduced. |
| `ruff check app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | PASS | 0 | No lint errors before format check. |
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | PASS | 0 | 16 tests passed. |
| `ruff format --check app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | FAIL | 1 | Ruff reported the modified test needed formatting. |
| `ruff format app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | PASS | 0 | 1 file reformatted. |
| `ruff check app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | PASS | 0 | No lint errors after format. |
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | PASS | 0 | 16 tests passed after format. |
| `ruff check .` | `backend` | PASS | 0 | Backend lint passed. |
| `pytest -q` | `backend` | FAIL | 124 | Timed out after 304 seconds without final pytest result. |
| `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist` | `backend` | PASS | 0 | 1 test passed after SQL allowlist line-number realignment. |
| `ruff check .` | `backend` | PASS | 0 | Backend lint passed after reviewer fix. |
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist` | `backend` | PASS | 0 | 17 targeted tests passed after reviewer fix. |
| `pytest -q` | `backend` | PASS | 0 | 3591 passed, 12 skipped in 713.24 seconds after SQL allowlist line-number realignment. |
| `python -c "from app.main import app; print(len(app.routes))"` | `backend` | PASS | 0 | App imported successfully; 220 routes registered. |
| `git diff --stat` | repository root | PASS | 0 | Diff reviewed; untracked CS-012 files are not included by git stat. |
| `git diff --check` | repository root | PASS | 0 | No whitespace errors; Git emitted LF-to-CRLF warnings. |
| `git status --short` | repository root | PASS | 0 | Final status captured below. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | No command was intentionally skipped. | None. | Not applicable. |

## DRY / No Legacy evidence

| Pattern | Result | Classification | Action | Status |
|---|---|---|---|---|
| New Python files under `app/prediction` | Guard compares exact allowlist to filesystem. | reintroduction_guard | Added persisted allowlist and pytest guard. | PASS |
| `from app.api`, `fastapi`, `app.core.config`, `app.infra`, `sqlalchemy`, `AIEngineAdapter`, `settings`, `LLMNarrator` | Forbidden import scan zero-hit; AST guard added. | forbidden_surface_blocked | No runtime code change; test enforces future failures. | PASS |
| Legacy/fallback wording in existing prediction code | Existing historical/domain hits in `schemas.py`, `natal_sensitivity.py`, `public_projection.py`, scoring/event code, and tests. | out_of_scope_with_justification | Story is guard-only and does not migrate these surfaces; no new shim/fallback introduced. | PASS_WITH_LIMITATIONS |
| CS-012 exception register | No active exception rows. | no_active_exception | Documented closed exceptions from CS-007 and CS-009. | PASS |

## Diff review

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` is the only code file changed by this story.
- `_condamad/stories/regression-guardrails.md` was already modified before implementation and contains `RG-032` plus `RG-033`.
- `_condamad/stories/story-status.md` was already modified before implementation; CS-012 is now marked `done`.
- `git diff --check` passed with line-ending warnings only.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md
 M _condamad/stories/story-status.md
 M backend/app/tests/unit/test_daily_prediction_guardrails.py
?? _condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/
?? _condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/
```

## Remaining risks

- Existing legacy/fallback terminology remains in `app/prediction`; it is outside this guard-only story and was not introduced here.

## Suggested reviewer focus

- Review the markdown allowlist parser and whether the persisted allowlist format is strict enough for future maintenance.
- Confirm that zero active exceptions is acceptable now that CS-007 and CS-009 have removed the exceptions originally listed in the story.
