# No Legacy / DRY Guardrails

## Canonical Ownership

- Request correlation source: API dependency or request context, then service call parameters.
- Horoscope narration IDs: explicit input reaching `services/llm_generation/horoscope_daily`.
- Public projection: deterministic public DTO assembly only.

## Forbidden Patterns

- `uuid.uuid4()` in `backend/app/prediction/public_projection.py`
- `request_id = str(uuid.uuid4())`
- `trace_id = str(uuid.uuid4())`
- silent fallback generation of correlation IDs in projection
- `LLMNarrator` as nominal runtime dependency
- new tracing dependency or parallel observability context

## Required Negative Evidence

- `rg -n "uuid\\.uuid4\\(|request_id = str\\(|trace_id = str\\(" app/prediction/public_projection.py`
- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`

## Applicable Regression Guardrails

- `RG-017`: no direct legacy LLM provider path.
- `RG-019`: horoscope daily prompt assembly remains governed.
- `RG-029`: public projection remains deterministic and outside runtime LLM ownership.
- `RG-033`: correlation IDs come from API/service path, not local projection generation.

## Exceptions

- No exception is allowed for local UUID generation in `public_projection.py`.

## Review Checklist

- No compatibility shim or fallback was introduced.
- Tests prove propagation with caller-provided IDs.
- Public payload shape remains unchanged.
- All search hits are classified in final evidence.
