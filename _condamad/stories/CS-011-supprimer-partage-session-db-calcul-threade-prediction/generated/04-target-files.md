# Target Files

## Must read

- `backend/app/services/prediction/compute_runner.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/services/prediction/service.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `_condamad/stories/regression-guardrails.md`

## Must search

- `rg -n "PredictionComputeRunner|run_with_timeout|with_context_loader|context_loader" backend/app backend/tests`
- `rg -n "non-thread-safe|thread-safe|session worker|contexte precharge" backend/app/services/prediction/compute_runner.py`
- `rg -n "SessionLocal|engine" backend/app/tests/unit/test_prediction_compute_runner.py backend/app/tests/unit/test_daily_prediction_service.py`

## Likely modified

- `backend/app/services/prediction/compute_runner.py`
- `backend/app/tests/unit/test_prediction_compute_runner.py`
- `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-before.md`
- `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-after.md`
- `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/generated/*`
- `_condamad/stories/story-status.md`

## Forbidden unless justified

- `frontend/**`
- API routers
- DB schema or migrations
- New dependencies
