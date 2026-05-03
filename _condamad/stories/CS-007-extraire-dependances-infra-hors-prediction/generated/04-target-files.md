# Target files - CS-007

## Must read

- `backend/app/prediction/context_loader.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/services/prediction/compute_runner.py`
- `backend/app/services/prediction/service.py`
- `backend/app/tests/unit/test_context_loader.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/integration/test_prediction_persistence.py`
- `backend/app/tests/integration/test_engine_persistence_e2e.py`

## Must search

- `rg -n "app\\.prediction\\.context_loader|app\\.prediction\\.persistence_service" backend/app backend/tests backend/app/tests`
- `rg -n "PredictionContextLoader|PredictionPersistenceService" backend/app backend/tests backend/app/tests`
- `rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\\.infra" backend/app/prediction -g "*.py"`

## Likely modified

- `backend/app/services/prediction/**`
- `backend/app/tests/unit/test_context_loader.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- imports in consumers under `backend/app/**` and `backend/app/tests/**`

## Likely deleted

- `backend/app/prediction/context_loader.py`
- `backend/app/prediction/persistence_service.py`

## Forbidden unless directly justified

- `frontend/**`
- `backend/app/api/v1/routers/public/predictions.py`
- DB migrations and models, unless validation reveals a direct blocker.
