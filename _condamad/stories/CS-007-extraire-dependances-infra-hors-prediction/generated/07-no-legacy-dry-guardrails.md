# No Legacy / DRY guardrails - CS-007

## Canonical owners

- Prediction context loading use case: `backend/app/services/prediction`.
- Prediction persistence DB implementation: `backend/app/services/prediction` using existing infra repositories.
- Pure prediction package: `backend/app/prediction`, without SQLAlchemy sessions or DB repositories.

## Forbidden active paths

- `backend/app/prediction/context_loader.py`
- `backend/app/prediction/persistence_service.py`
- `from app.prediction.context_loader import`
- `from app.prediction.persistence_service import`
- `from sqlalchemy` in `backend/app/prediction`
- `Session`, `DailyPredictionRepository`, `PredictionReferenceRepository`, `PredictionRulesetRepository`, `from app.infra` in `backend/app/prediction`.

## Required negative evidence

- `rg -n "app\\.prediction\\.context_loader|app\\.prediction\\.persistence_service" app tests`
- `rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\\.infra" app/prediction -g "*.py"`
- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`

## Review checklist

- No old module remains as facade, wrapper, alias, or re-export.
- Consumers import the canonical service path directly.
- Tests assert canonical behavior and guard against forbidden import growth.
- The forbidden infra scan returns zero active hits.
