# Target Files

## Read before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/integration/test_llm_legacy_extinction.py`

## Searches performed

- `rg --files backend | rg "test_llm_legacy_extinction|test_assembly_resolution|test_prompt_governance_registry"`
- `rg -n "PROMPT_FALLBACK_CONFIGS|build_fallback_use_case_config|legacy_use_case_fallback|_allows_nominal_bootstrap_fallback|fallback_config_used|missing assembly|assembly" ...`
- `rg -n "\"chat\"|\"chat_astrologer\"|\"guidance_contextual\"|\"natal_interpretation\"|\"horoscope_daily\"" ...`
- `rg -n "PROMPT_FALLBACK_CONFIGS|legacy_use_case_fallback" app tests`

## Modified files

- `backend/app/domain/llm/prompting/catalog.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `_condamad/stories/block-supported-family-prompt-fallbacks/fallback-exception-audit.md`
- CONDAMAD generated evidence files

## Forbidden unless justified

- `frontend/src`
- `backend/app/api/v1/routers`
- Prompt seed content and published prompt version data
