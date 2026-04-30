# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `backend/tests/unit/prediction/test_llm_narrator.py`
- `backend/tests/integration/test_llm_governance_registry.py`
- `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`
- `backend/tests/llm_orchestration/test_narrator_migration.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/prediction/llm_narrator.py`

## Required searches before editing

```powershell
rg -n "LLMNarrator|llm_narrator" backend/app backend/tests -g "*.py"
rg -n "generate_horoscope_narration" backend/app backend/tests -g "*.py"
rg -n "from app\.prediction\.llm_narrator import LLMNarrator|LLMNarrator\(|LLMNarrator\.narrate" backend/tests -g "test_*.py"
```

Adapt searches to the story and repository layout.

## Likely modified files

- `backend/tests/unit/prediction/test_llm_narrator.py`
- `backend/tests/integration/test_llm_governance_registry.py`
- `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`
- a new or existing backend architecture guard test
- `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-before.md`
- `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-after.md`
- `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md`

## Forbidden or high-risk files

- `backend/app/api/**` unless a test import proves it is required.
- `frontend/src/**`.
- `requirements.txt`.
- Production LLM runtime behavior outside direct test accommodation.
