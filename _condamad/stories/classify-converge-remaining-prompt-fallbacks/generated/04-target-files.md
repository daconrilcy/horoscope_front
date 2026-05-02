# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/ops/llm/bootstrap/seed_29_prompts.py`
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`

## Required searches before editing

| Purpose | Command |
|---|---|
| Fallback runtime surface | `rg -n "PROMPT_FALLBACK_CONFIGS|build_fallback_use_case_config" app tests` from `backend/` |
| Story keys and consumers | `rg -n "natal_long_free|natal_interpretation_short|guidance_daily|guidance_weekly|event_guidance|astrologer_selection_help|test_natal|test_guidance" backend\app backend\tests _condamad\audits _condamad\stories` |
| Gateway behavior | `rg -n "missing_assembly|_allows_nominal_bootstrap_fallback|build_fallback_use_case_config" backend\app\domain\llm\runtime\gateway.py` |

## Likely modified files

- `backend/app/domain/llm/prompting/catalog.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `_condamad/stories/classify-converge-remaining-prompt-fallbacks/fallback-classification.md`
- `_condamad/stories/classify-converge-remaining-prompt-fallbacks/generated/*.md`

## Forbidden or high-risk files

- `frontend/`
- `backend/app/api/v1/routers`
- `backend/pyproject.toml`
- `backend/app/domain/llm/runtime/gateway.py` unless production `missing_assembly` behavior requires a fix
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` unless classification proves a registry defect
