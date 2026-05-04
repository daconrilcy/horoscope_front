# Target Files

## Inspected

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `backend/app/prediction`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`

## Searches

- `rg -n "from app\.prediction|import app\.prediction" backend/app backend/tests -g "*.py"`
- `rg -n "app\.prediction" backend -g "*.py"`
- `rg --files backend/app/prediction`
- `rg --files backend/app/domain backend/app/services/api_contracts backend/app/infra/db/repositories backend/app/services/prediction`

## Modified or moved

- Moved: `backend/app/prediction/**` -> `backend/app/domain/prediction/**`
- Modified: active imports under `backend/app/**`, `backend/app/tests/**`, `backend/tests/**`
- Modified: `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- Added/updated: CS-014 CONDAMAD evidence files

## Forbidden unless justified

- `frontend/**`: unchanged.
- `backend/pyproject.toml`: unchanged.
- Any compatibility module under `backend/app/prediction`: forbidden and absent.
