# Target files - CS-018

## Must read

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`

## Must search

- `rg --files backend/app/prediction`
- `rg -n "from app\.prediction|import app\.prediction" backend/app backend/tests backend/app/tests -g "*.py"`
- `rg -n "_PREDICTION_NAMESPACE_ALLOWLIST|prediction-namespace-allowlist|allowlist" backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app backend/tests backend/app/tests -g "*.py"`

## Likely modified

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/guard-before.md`
- `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/guard-after.md`
- `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/generated/*.md`
- `_condamad/stories/story-status.md`

## Forbidden unless directly justified

- `frontend/**`
- `backend/pyproject.toml`
- Runtime route, service, infra or domain prediction implementation files.
- Any new `backend/app/prediction` file or compatibility wrapper.

## Inspection result

- `backend/app/prediction` is absent.
- No active Python import `app.prediction` was found under backend runtime or tests.
- The guard file already expresses the final extinction invariant and does not read the CS-012 allowlist.
