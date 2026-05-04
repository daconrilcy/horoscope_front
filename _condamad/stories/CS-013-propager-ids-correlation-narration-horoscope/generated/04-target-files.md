# Target Files

## Must Read

- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/services/prediction/service.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/tests/unit/test_request_id.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/app/tests/unit/test_public_projection.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/regression-guardrails.md`

## Must Search

- `rg -n "request_id|trace_id|Correlation|X-Request|X-Correlation" backend/app backend/tests`
- `rg -n "uuid\\.uuid4\\(|request_id = str\\(|trace_id = str\\(" backend/app/prediction/public_projection.py`
- `rg -n "LLMNarrator|chat\\.completions\\.create|openai\\.AsyncOpenAI" backend/app backend/tests`

## Likely Modified

- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/services/prediction/service.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- Story evidence files under `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/`
- `_condamad/stories/story-status.md`

## Forbidden Unless Justified

- `frontend/src`
- New dependencies or dependency metadata
- `backend/app/domain/llm` prompt governance files
