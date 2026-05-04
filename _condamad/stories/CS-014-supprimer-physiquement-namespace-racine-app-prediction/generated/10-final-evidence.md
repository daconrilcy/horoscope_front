# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: clean review completed
- Final status: done
- Story key: CS-014-supprimer-physiquement-namespace-racine-app-prediction
- Source story: `_condamad/stories/CS-014-supprimer-physiquement-namespace-racine-app-prediction/00-story.md`
- Capsule path: `_condamad/stories/CS-014-supprimer-physiquement-namespace-racine-app-prediction`

## Review/fix loop

| Iteration | Verdict | Findings | Fix evidence |
|---:|---|---:|---|
| 1 | CHANGES_REQUESTED | 3 | Full pytest exposed stale guard paths and stale SQL allowlist line numbers. |
| 2 | CLEAN | 0 | Targeted tests, story validations, lint/format and full pytest pass. |

## Issues fixed during review

| Finding | Category | Fix |
|---|---|---|
| `test_editorial_i18n.py` still read templates from `backend/app/prediction`. | reintroduction guard evidence | Updated the test path to `backend/app/domain/prediction/editorial_templates`. |
| `test_astrologer_prompt_builder.py` still read `backend/app/prediction/astrologer_prompt_builder.py`. | reintroduction guard evidence | Updated the source guard to inspect `backend/app/domain/prediction/astrologer_prompt_builder.py`. |
| API SQL boundary allowlist had stale line numbers after import migration. | architecture guard evidence | Updated exact allowlist rows for `internal/llm/qa.py` and `public/predictions.py`. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `prediction-namespace-before.md` and `prediction-namespace-after.md` are present. | Guard tests and full pytest PASS. | PASS | Before inventory records 55 tracked legacy files. |
| AC2 | Tracked files moved from `backend/app/prediction/**` to `backend/app/domain/prediction/**`; old folder absent. | `rg --files app/prediction` from `backend/` returns missing path/no files. | PASS | Missing path is expected zero-file evidence. |
| AC3 | Internal consumers import `app.domain.prediction.*`. | Zero-hit scans for `from app.prediction` and `import app.prediction` under `app tests` and `backend/tests`. | PASS | Guard literals remain only in tests/evidence. |
| AC4 | `removal-audit.md` classifies removed surfaces and canonical decisions. | API, engine and full regression tests PASS. | PASS | Fine-grained owners remain tracked by CS-015 to CS-017. |
| AC5 | `test_daily_prediction_guardrails.py` checks non-importability, missing folder and forbidden import AST. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_engine_orchestrator.py` PASS. | PASS | Guards fail if `app.prediction` returns. |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_engine_orchestrator.py` | `backend/`, venv active | PASS | 0 | 38 passed. |
| `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend/`, venv active | PASS | 0 | 25 passed. |
| `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_editorial_i18n.py tests/unit/prediction/test_astrologer_prompt_builder.py` | `backend/`, venv active | PASS | 0 | 7 passed after review fixes. |
| `pytest -q` | `backend/`, venv active | PASS | 0 | 3593 passed, 12 skipped. |
| `ruff check app tests` | `backend/`, venv active | PASS | 0 | All checks passed. |
| `ruff format --check app tests` | `backend/`, venv active | PASS | 0 | 1081 files already formatted. |
| `rg --files app/prediction` | `backend/` | PASS | 1 | Missing path/no files, expected after removal. |
| `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` | `backend/` | PASS | 1 | Zero-hit. |
| `rg -n "from app\.prediction\|import app\.prediction" ..\backend\tests -g "*.py"` | `backend/` | PASS | 1 | Zero-hit. |
| `python -c "import importlib.util; assert importlib.util.find_spec('app.prediction') is None; import app.main"` | `backend/`, venv active | PASS | 0 | Legacy module absent; app import succeeds. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only. |

## DRY / No Legacy evidence

- No `backend/app/prediction` directory remains.
- No active `from app.prediction` or `import app.prediction` remains under `backend/app`, `backend/app/tests`, or `backend/tests`.
- `app.prediction` is not importable via Python.
- No compatibility package, re-export, alias, wrapper or fallback was added.
- Remaining text references to `app.prediction` are test literals, CONDAMAD story/audit history, or guard evidence.

## Remaining risks

- Fine-grained ownership refinement for pure engine, persisted DTOs and public projection remains tracked by CS-015, CS-016 and CS-017.
- No runtime legacy risk remains for CS-014.
