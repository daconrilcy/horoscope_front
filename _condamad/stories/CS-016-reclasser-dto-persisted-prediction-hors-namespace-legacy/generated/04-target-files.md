# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
- `backend/app/domain/prediction/persisted_snapshot.py`
- `backend/app/domain/prediction/persisted_relative_score.py`
- `backend/app/domain/prediction/persisted_baseline.py`
- `backend/app/domain/prediction/context.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`

## Required searches

```powershell
rg -n "app\.prediction\.persisted|app\.prediction\.context" backend/app/infra/db/repositories -g "*.py"
rg -n "from app\.prediction\.persisted|from app\.prediction\.context" backend/app backend/tests -g "*.py"
rg --files backend/app | rg "(^|/)prediction/(persisted_(snapshot|relative_score|baseline)|context)\.py$"
```

## Modified files

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-classification.md`
- `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-before.md`
- `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-after.md`
- CONDAMAD generated evidence files for CS-016
- `_condamad/stories/story-status.md`

## Forbidden unless directly justified

- `backend/alembic`
- `frontend`
- `backend/app/prediction`
