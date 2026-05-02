# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/services/llm_generation/consultation_generation_service.py`
- `backend/app/services/llm_generation/guidance/guidance_service.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `docs/llm-prompt-generation-by-feature.md`
- `backend/app/tests/unit/test_guidance_service.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`

## Required searches

- `rg -n "guidance_contextual|consultation_contextual|prompt_content|developer_prompt|PROMPT_FALLBACK_CONFIGS|canonical_families" backend\app backend\tests docs\llm-prompt-generation-by-feature.md`
- `rg -n '"consultation"|consultation_contextual|developer_prompt.*prompt_content|PROMPT_FALLBACK_CONFIGS' backend\app\domain backend\app\services backend\tests`
- `rg -n "guidance_contextual" docs\llm-prompt-generation-by-feature.md`

## Modified files

- `docs/llm-prompt-generation-by-feature.md`
- `backend/app/tests/unit/test_guidance_service.py`
- `backend/app/tests/unit/test_consultation_generation_service.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-before.md`
- `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-after.md`
- `_condamad/stories/formalize-consultation-guidance-prompt-ownership/generated/*`

## Forbidden unless explicitly justified

- `frontend/src`
- `backend/app/api/v1/routers`
- Any new `consultation` LLM family, `consultation_contextual` runtime use case, prompt fallback, shim, alias, or duplicate owner.
