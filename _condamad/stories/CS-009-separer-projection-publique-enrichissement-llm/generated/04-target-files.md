# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/prediction/public_projection.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- `backend/app/tests/unit/test_public_projection.py`
- `backend/app/tests/unit/prediction/test_public_projection_evidence.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`

## Required searches

```powershell
rg -n "AIEngineAdapter|uuid\\.uuid4\\(|settings|Session" backend/app/prediction/public_projection.py
rg -n "AIEngineAdapter\\.generate_horoscope_narration|generate_horoscope_narration" backend/app/tests backend/tests
rg -n "assemble\\(" backend/app backend/tests -g "*.py"
```

## Modified files

- `backend/app/prediction/public_projection.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/unit/prediction/test_public_projection_evidence.py`
- `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`
- `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/**`
- `_condamad/stories/story-status.md`

## Forbidden unless directly justified

- `frontend/src/**`
- `backend/app/domain/llm/**` provider/runtime internals
- Dependency or pyproject changes
