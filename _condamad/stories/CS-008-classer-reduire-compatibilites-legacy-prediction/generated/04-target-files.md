# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/prediction/schemas.py`
- `backend/app/services/prediction/persistence_service.py`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/tests/unit/test_public_projection.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`

## Required searches before editing

```bash
rg -n "EngineOutput|TimeBlock|engine_output=|\bcategories\b|LLMNarrator" backend/app backend/tests frontend _condamad
rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/prediction backend/app/tests backend/tests -g "*.py"
```

## Modified files

- `backend/app/prediction/schemas.py`
- `backend/app/services/prediction/persistence_service.py`
- `backend/app/tests/integration/test_v3_baselines.py`
- `backend/app/tests/unit/test_calibration_versioning.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/unit/test_persistence_explainability.py`
- `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/legacy-surface-audit.md`
- `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/legacy-surface-after.md`
- `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/generated/*`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `frontend/src/**`: read-only for this story; active `categories` consumers block deletion.
- `backend/app/prediction/public_projection.py`: public field unchanged.
- API contract schemas: unchanged because no public payload removal was approved.
