# Target Files

## Inspected

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/prediction/astrologer_prompt_builder.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/services/llm_generation/admin_prompts.py`
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
- `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py`
- `backend/tests/llm_orchestration/test_narrator_migration.py`
- `backend/tests/integration/test_admin_llm_catalog.py`

## Modified

- `backend/app/prediction/astrologer_prompt_builder.py`
- `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
- `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py`
- `backend/tests/llm_orchestration/test_narrator_migration.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-before.md`
- `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-after.md`
- `_condamad/stories/converge-horoscope-daily-narration-assembly/generated/*`

## Forbidden Unless Re-Scoped

- `frontend/src`
- `backend/app/api/v1/routers`
- `backend/app/services/ai_engine_adapter.py`
- public horoscope daily JSON schema changes
