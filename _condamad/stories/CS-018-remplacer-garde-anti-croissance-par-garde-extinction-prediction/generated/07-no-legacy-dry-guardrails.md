# No Legacy / DRY guardrails - CS-018

## Canonical owner

- Architecture guard: `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- Historical evidence: `_condamad/**`
- Runtime prediction implementation: canonical owners outside `backend/app/prediction`.

## Forbidden active surfaces

- `backend/app/prediction`
- `from app.prediction`
- `import app.prediction`
- `_PREDICTION_NAMESPACE_ALLOWLIST` as a runtime test exception.
- Compatibility wrapper, shim, alias, fallback or re-export preserving `app.prediction`.

## Required negative evidence

- `rg --files app/prediction` from `backend/`.
- `rg -n "from app\.prediction|import app\.prediction" app tests -g "*.py"` from `backend/`.
- AST guard `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`.

## Allowed historical references

- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md`
- `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md`
- Current story capsule and evidence files.

## Applicable regression guardrails

- `RG-026`: no shim, alias, fallback or re-export from the legacy namespace.
- `RG-032`: temporary anti-growth guard replaced by final extinction evidence.
- `RG-034`: physical namespace extinction must stay protected.
- `RG-037`: API routers must not import `app.prediction`.
- `RG-038`: final zero-file and zero-import invariant for prediction extinction.

## Review checklist

- No active file under `backend/app/prediction`.
- No active Python import of `app.prediction` under runtime or collected tests.
- No allowlist-powered runtime exception remains.
- `_condamad` references are historical only.
- No duplicate guard file was created.
