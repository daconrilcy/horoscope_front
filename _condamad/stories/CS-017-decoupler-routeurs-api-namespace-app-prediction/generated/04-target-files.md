# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/prediction/persisted_snapshot.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`
- `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`

## Required searches before editing

```powershell
rg -n "from app\.prediction|import app\.prediction|PublicPredictionAssembler|PersistedPredictionSnapshot" backend/app/api backend/app/services backend/app/tests -g "*.py"
rg -n "app\.prediction" backend/app/api -g "*.py"
rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/api/v1/routers/public/predictions.py backend/app/api/v1/routers/internal/llm/qa.py backend/app/tests/unit/test_daily_prediction_guardrails.py
```

## Modified files

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/00-story.md`
- `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/generated/*.md`
- `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/openapi-before.json`
- `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/openapi-after.json`
- `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/api-import-audit.md`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `frontend/src`: hors scope.
- `backend/alembic`: aucune migration.
- `backend/app/prediction`: ne pas recreer.
