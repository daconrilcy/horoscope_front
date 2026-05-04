# No Legacy / DRY Guardrails

## Canonical ownership

| Responsibility | Canonical owner | Forbidden surface |
|---|---|---|
| Public prediction deterministic projection | `backend/app/prediction/public_projection.py` during staged namespace convergence, with final owner documented as `services/prediction/public_predictions.py` | LLM runtime, DB session, local correlation ID generation |
| Horoscope daily narrative generation | `backend/app/services/llm_generation/horoscope_daily/narration_service.py` via `backend/app/services/prediction/public_predictions.py` orchestration | `backend/app/prediction/public_projection.py` |

## Forbidden symbols in `public_projection.py`

- `AIEngineAdapter`
- `settings`
- `uuid.uuid4()`
- `Session`

## Required evidence

- AST guard in `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
- Negative scan: `rg -n "AIEngineAdapter|uuid\\.uuid4\\(|settings|Session" app/prediction/public_projection.py`.
- Tests proving persisted narratives remain projected and short free narratives are enriched by the service layer.

## Allowed exception

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/prediction/public_projection.py` | deterministic projection helpers | Migration par etapes vers owner public. | Until CS-006 namespace convergence completes. |

## Review checklist

- No compatibility wrapper or re-export was introduced.
- No second narrator or adapter was created.
- Routeurs pass `request_id` and `trace_id` into the service orchestration.
- Projection remains callable without DB/session/prompt context.
