# Target Files

## Inspected Before Implementation

- `AGENTS.md`
- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `_condamad/stories/story-status.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md`
- `_condamad/stories/CS-255-product-architecture-current-state/00-story.md`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/natal_calculation.py`

## Searches Run

```powershell
rg -n "structured_facts|structured_facts_v1|AINarrativeInputContract|ChartObjectRuntimeData|chart_objects" docs backend _condamad _story_briefs
rg -n "legacy|compat|shim|fallback|deprecated|alias" docs\architecture\structured-facts-v1-contract.md _condamad\stories\CS-256-structured-facts-v1-contract
git status --short -- backend\app frontend\src
```

## Modified Files

- `docs/architecture/structured-facts-v1-contract.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/source-checklist.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/validation.txt`
- `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/app-surface-status.txt`
- `_condamad/stories/CS-256-structured-facts-v1-contract/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/generated/04-target-files.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/generated/06-validation-plan.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/generated/10-final-evidence.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/generated/11-code-review.md`
- `_condamad/stories/story-status.md`

## Forbidden Or High-Risk Files Kept Unchanged

- `frontend/src/**`
- `backend/app/**`
- `backend/tests/**`
- `backend/migrations/**`
- generated OpenAPI clients
- prompt template files
