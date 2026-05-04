# Source canonique de correlation

## Decision

La source canonique des IDs de correlation HTTP est `backend/app/core/request_id.py`.

- `resolve_request_id(request)` privilegie `request.state.request_id`, puis le header `X-Request-Id`, puis genere un ID technique au niveau coeur HTTP si aucun ID externe exploitable n'existe.
- `resolve_trace_id(request, fallback=request_id)` privilegie le header `X-Trace-Id`, puis reutilise le `request_id` deja resolu.

## Chemin runtime horoscope daily

1. `backend/app/api/v1/routers/public/predictions.py` resout `request_id` et `trace_id` depuis la requete HTTP.
2. Le routeur transmet ces valeurs a `enrich_public_prediction_with_horoscope_narration`.
3. `backend/app/services/prediction/public_predictions.py` transmet les memes valeurs a `generate_horoscope_narration_via_gateway`.
4. `backend/app/services/llm_generation/horoscope_daily/narration_service.py` les place dans `LLMExecutionRequest`.

## Limite volontaire

`backend/app/prediction/public_projection.py` reste une projection deterministe. Il ne lit pas la requete HTTP, ne genere pas d'UUID et ne porte pas le runtime LLM.
