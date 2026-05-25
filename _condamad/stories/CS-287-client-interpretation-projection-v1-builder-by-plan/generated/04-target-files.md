# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Required searches before editing

```bash
rg -n "client_interpretation_projection_v1|ClientInterpretationProjectionV1Builder" backend\app\domain\astrology\interpretation backend\tests\unit\domain\astrology
rg -n "structured_facts_v1|BEGINNER_SUMMARY_V1_DISCLAIMER_CODES|plan_insufficient" backend\app\domain\astrology\interpretation docs\architecture
git diff --stat -- <story paths>
git diff --name-only -- <story paths>
```

Adapt searches to the story and repository layout.

## Likely modified files

- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`
- `_condamad/stories/CS-287-client-interpretation-projection-v1-builder-by-plan/evidence/**`
- `_condamad/stories/CS-287-client-interpretation-projection-v1-builder-by-plan/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-287-client-interpretation-projection-v1-builder-by-plan/generated/10-final-evidence.md`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `frontend/src/**`
- `backend/app/api/**`
- `backend/app/infra/db/**`
- `backend/migrations/**`
- provider, prompt template, generated OpenAPI client or public serializer files
