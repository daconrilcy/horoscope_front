# Target Files

## Must read

- `backend/app/prediction/llm_narrator.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/prompting/narrator_contract.py`
- `backend/tests/llm_orchestration/test_narrator_migration.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- `_condamad/stories/regression-guardrails.md`

## Must search

- `rg -n "LLMNarrator|llm_narrator" backend/app backend/tests docs`
- `rg -n "chat\.completions\.create|openai\.AsyncOpenAI" backend/app backend/tests`
- `rg -n "from app\.prediction\.llm_narrator import|import app\.prediction\.llm_narrator" backend/app backend/tests`

## Likely modified

- `backend/app/domain/llm/prompting/narrator_contract.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/tests/llm_orchestration/test_narrator_migration.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- Tests importing `NarratorResult` from the legacy module.

## Likely deleted

- `backend/app/prediction/llm_narrator.py`
- `backend/tests/unit/prediction/test_llm_narrator.py`

## Forbidden unless justified

- Frontend files.
- API router behavior.
- OpenAPI contracts.
- Dependency manifests.
