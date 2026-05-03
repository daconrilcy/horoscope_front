# Target Files - CS-006

## Must read

- `backend/app/prediction`
- `backend/app/services/prediction`
- `backend/app/services/prediction/compute_runner.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- `_condamad/audits/prediction/2026-05-03-2214/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`

## Must search

- `rg -n "app\\.prediction\\.engine_orchestrator|EngineOrchestrator|DailyEngineMode" backend/app backend/tests`
- `rg -n "from app\\.prediction import|app\\.prediction\\.llm_narrator|LLMNarrator" app tests`
- `rg --files app/prediction`

## Likely modified

- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/services/prediction/compute_runner.py`
- `backend/app/services/prediction/service.py`
- `backend/app/jobs/**`
- `backend/app/services/user_profile/prediction_baseline_service.py`
- `backend/app/services/natal/astro_context_builder.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/**` consumers of `EngineOrchestrator`
- `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/**`
- `_condamad/stories/story-status.md`

## Forbidden unless justified

- `frontend/src`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/prediction/llm_narrator.py`
- Any compatibility module under `backend/app/prediction`
