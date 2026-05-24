# Target Files

## Inspected

- `AGENTS.md`
- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md`
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md`
- `_condamad/stories/regression-guardrails.md` scoped IDs RG-100, RG-102, RG-143, RG-144
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/app/domain/astrology/interpretation/chart_object_interpretation_projector.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- Existing unit and architecture tests near the affected files

## Modified

- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`
- `backend/tests/architecture/test_ai_narrative_input_boundary.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/**`
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/generated/**`
- `_condamad/stories/story-status.md`

## Forbidden / Not Modified

- `frontend/src/**`
- `backend/app/api/**`
- `backend/app/infra/db/**`
- `backend/migrations/**`
- Prompt template or provider gateway modules
