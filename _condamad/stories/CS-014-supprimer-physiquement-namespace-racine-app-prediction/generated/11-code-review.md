# CONDAMAD Code Review

## Review target

- Story: `CS-014-supprimer-physiquement-namespace-racine-app-prediction`
- Capsule: `_condamad/stories/CS-014-supprimer-physiquement-namespace-racine-app-prediction`
- Scope reviewed: physical removal of `backend/app/prediction`, import migration to `app.domain.prediction`, extinction guard, inventories and removal audit.

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `prediction-namespace-before.md`
- `prediction-namespace-after.md`
- `removal-audit.md`
- `_condamad/stories/regression-guardrails.md`
- Git diff and validation commands.

## Diff summary

- `backend/app/prediction/**` was physically removed as an importable package and moved to `backend/app/domain/prediction/**`.
- Active consumers under `backend/app`, `backend/app/tests` and `backend/tests` now import `app.domain.prediction.*`.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` now verifies package non-importability, folder absence and forbidden legacy imports.
- Review fixes updated stale guard paths in tests and exact SQL allowlist rows affected by import ordering.

## Findings

No open findings.

### Resolved CR-001 High - Full regression still referenced the removed template directory

- Bucket: patch
- Location: `backend/app/tests/unit/test_editorial_i18n.py`
- Source layer: validation / no-legacy
- Evidence: initial full `pytest -q` failed because the test expected `backend/app/prediction/editorial_templates/fr`.
- Impact: full regression could not pass after physical namespace deletion.
- Fix: `TEMPLATE_BASE` now points to `backend/app/domain/prediction/editorial_templates`.
- Status: resolved.

### Resolved CR-002 High - Prompt builder guard read the deleted legacy file path

- Bucket: patch
- Location: `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
- Source layer: validation / no-legacy
- Evidence: initial full `pytest -q` failed with `FileNotFoundError` on `backend/app/prediction/astrologer_prompt_builder.py`.
- Impact: a guard intended to prevent durable prompt regressions became incompatible with the physical deletion.
- Fix: the guard now reads `backend/app/domain/prediction/astrologer_prompt_builder.py`.
- Status: resolved.

### Resolved CR-003 Medium - SQL boundary allowlist was stale after import migration

- Bucket: patch
- Location: `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- Source layer: validation
- Evidence: `test_api_sql_boundary_debt_matches_exact_allowlist` reported four missing and four stale exact entries for `internal/llm/qa.py` and `public/predictions.py`.
- Impact: architecture debt guard failed even though the SQL debt itself did not grow.
- Fix: exact line numbers were updated to match the current imports.
- Status: resolved.

## Acceptance audit

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | Before/after inventory files are present and final evidence maps validation. |
| AC2 | PASS | `backend/app/prediction` is absent; `rg --files app/prediction` from `backend/` returns no files. |
| AC3 | PASS | Import scans under `app tests` and `backend/tests` are zero-hit. |
| AC4 | PASS | `removal-audit.md` classifies deleted legacy path, consumers and canonical route. |
| AC5 | PASS | Extinction guard passes and blocks importability, folder recreation and AST legacy imports. |

## Validation audit

| Command | Result |
|---|---|
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_engine_orchestrator.py` | PASS, 38 passed |
| `pytest -q app/tests/integration/test_daily_prediction_api.py` | PASS, 25 passed |
| `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_editorial_i18n.py tests/unit/prediction/test_astrologer_prompt_builder.py` | PASS, 7 passed |
| `pytest -q` | PASS, 3593 passed, 12 skipped |
| `ruff check app tests` | PASS |
| `ruff format --check app tests` | PASS |
| `rg --files app/prediction` | PASS as zero-file evidence; missing path returns exit 1 |
| `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` | PASS as zero-hit; exit 1 |
| `rg -n "from app\.prediction\|import app\.prediction" ..\backend\tests -g "*.py"` | PASS as zero-hit; exit 1 |
| `python -c "import importlib.util; assert importlib.util.find_spec('app.prediction') is None; import app.main"` | PASS |
| `git diff --check` | PASS; line-ending warnings only |

## DRY / No Legacy audit

- No `backend/app/prediction` package remains.
- No active Python import of `app.prediction` remains in application or backend tests.
- No facade, alias, wrapper, re-export or fallback was added.
- Historical mentions in CONDAMAD stories and audits are not runtime paths.

## Residual risks

- CS-015, CS-016 and CS-017 still carry finer ownership cleanup after the physical namespace removal.
- No CS-014 blocking risk remains.

## Verdict

CLEAN
