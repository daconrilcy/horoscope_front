# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md`
- `_story_briefs/cs-263-define-generic-projection-endpoint-contract.md`
- `_condamad/stories/story-status.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `docs/architecture/structured-facts-v1-contract.md`
- `docs/architecture/beginner-summary-v1-contract.md`
- `docs/architecture/client-interpretation-projection-v1-contract.md`
- `docs/architecture/narrative-answer-audit-v1-contract.md`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `backend/app/api/v1/routers/` by targeted `rg` only
- `_condamad/stories/regression-guardrails.md` targeted IDs `RG-002`, `RG-003`, `RG-022`

## Required searches before editing

```bash
rg -n "/v1/astrology/projections|projection_type|projection_version|birth_input|chart_id|persist" .\docs .\_story_briefs
rg -n "/v1/astrology/projections" backend\app frontend\src
git diff --stat -- docs/architecture/generic-projection-endpoint-contract.md _condamad/stories/CS-263-generic-projection-endpoint-contract
git diff --name-only -- docs/architecture/generic-projection-endpoint-contract.md _condamad/stories/CS-263-generic-projection-endpoint-contract
```

Adapt searches to the story and repository layout.

## Likely modified files

- `docs/architecture/generic-projection-endpoint-contract.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/generated/*.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/*.txt`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `backend/app/api/**`
- `backend/app/infra/db/**`
- `backend/migrations/**`
- `frontend/src/**`
- generated OpenAPI clients
- duplicate endpoint contract documents
