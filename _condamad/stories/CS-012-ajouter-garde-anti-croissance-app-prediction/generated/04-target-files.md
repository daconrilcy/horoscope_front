# Target Files - CS-012

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- `backend/app/prediction`

## Must search

- `rg --files app/prediction`
- `rg -n "from app\\.api|import app\\.api|fastapi|AIEngineAdapter|from sqlalchemy|import sqlalchemy|LLMNarrator" app/prediction -g "*.py"`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" app/prediction app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py`

## Likely modified

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/generated/*.md`
- `_condamad/stories/story-status.md`

## Forbidden unless justified

- `backend/app/prediction/*.py`
- `backend/app/api/**`
- `backend/app/services/**`
- `frontend/**`

## Existing tests to inspect first

- `backend/app/tests/unit/test_backend_services_structure_guard.py`
- `backend/app/tests/unit/test_scope_separation_imports.py`
