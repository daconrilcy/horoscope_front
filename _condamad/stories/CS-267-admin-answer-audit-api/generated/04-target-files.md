# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Required searches before editing

```bash
rg "<main symbol or feature name>" .
rg "legacy|compat|shim|fallback|deprecated|alias" .
git diff --stat -- <story paths>
git diff --name-only -- <story paths>
```

Adapt searches to the story and repository layout.

## Modified files for CS-267

- `docs/architecture/admin-answer-audit-api.md` - canonical `admin_answer_audit_v1` API contract document.
- `backend/app/tests/integration/test_admin_answer_audit_contract.py` - targeted contract, route-neutrality and forbidden-path tests.
- `_condamad/stories/CS-267-admin-answer-audit-api/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-267-admin-answer-audit-api/evidence/app-surface-status.txt` - scoped app/frontend status evidence.
- `_condamad/stories/CS-267-admin-answer-audit-api/evidence/source-checklist.md` - source and dependency coverage evidence.
- `_condamad/stories/CS-267-admin-answer-audit-api/generated/03-acceptance-traceability.md` - AC validation mapping.
- `_condamad/stories/CS-267-admin-answer-audit-api/generated/10-final-evidence.md` - implementation handoff evidence.
- `_condamad/stories/CS-267-admin-answer-audit-api/generated/11-code-review.md` - implementation review evidence.

## Forbidden or high-risk files

- `backend/app/**` - no runtime route, model, repository, service or auth behavior is authorized by this contract story.
- `frontend/src/**` - no admin UI or generated client is authorized.
- `backend/migrations/**` - no persistence schema is authorized before CS-288.
- `backend/app/api/v1/routers/public/**` - no public/client route is authorized.
