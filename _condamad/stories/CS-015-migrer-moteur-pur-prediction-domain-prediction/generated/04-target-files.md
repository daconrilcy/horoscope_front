# Target Files

## Must read

- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/domain/prediction/__init__.py`
- `backend/app/domain/prediction/schemas.py`
- `backend/app/domain/prediction/aggregator.py`
- `backend/app/domain/prediction/astro_calculator.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/unit/test_transit_signal_v3.py`
- `backend/tests/unit/prediction/test_public_astro_foundation.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`

## Must search

- `rg --files app/domain/prediction`
- `rg -n "from app\.prediction|import app\.prediction|app\.prediction" app tests -g "*.py"`
- `rg -n "from app\.prediction" app/services/prediction -g "*.py"`
- `rg -n "fastapi|sqlalchemy|Session|settings|AIEngineAdapter|from app\.infra|from app\.api|from app\.services" app/domain/prediction -g "*.py"`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py -g "*.py"`

## Likely modified

- `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/*`
- `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/domain-prediction-before.md`
- `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/domain-prediction-after.md`
- `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/00-story.md`
- `_condamad/stories/story-status.md`

## Forbidden unless justified

- `backend/app/api/**`
- `frontend/**`
- `backend/app/infra/**`
- New dependencies or dependency manifests.
- Recreating `backend/app/prediction/**`.

## Existing tests to inspect first

- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/unit/test_transit_signal_v3.py`
- `backend/tests/unit/prediction/test_public_astro_foundation.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
