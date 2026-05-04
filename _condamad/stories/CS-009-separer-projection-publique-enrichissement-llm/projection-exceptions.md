# Projection Exceptions

| File | Symbol / Route / Import | Reason | Expiry or permanence decision | Validation |
|---|---|---|---|---|
| `backend/app/prediction/public_projection.py` | deterministic projection helpers and public policy classes | Migration par etapes vers owner public; la story ne migre pas tout le namespace `app.prediction`. | Until CS-006 namespace convergence completes. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`; scan exact `AIEngineAdapter`, `settings`, `uuid.uuid4()`, `Session` sans hit. |

No wildcard exception, folder-wide exception, runtime LLM exception, DB session exception, or local correlation ID exception is allowed.
