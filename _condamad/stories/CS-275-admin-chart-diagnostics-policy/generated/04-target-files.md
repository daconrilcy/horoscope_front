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

## Likely modified files

- `docs/architecture/admin-chart-diagnostics-v1-policy.md`
- `backend/tests/unit/test_admin_chart_diagnostics_policy.py`
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/generated/10-final-evidence.md`
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/validation.txt`
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/app-surface-status.txt`
- `_condamad/stories/story-status.md` exact `CS-275` row only

## Forbidden or high-risk files

- `frontend/src/**`
- `backend/app/api/**`
- `backend/app/services/**`
- `backend/app/infra/db/**`
- `backend/migrations/**`
- generated OpenAPI clients
- public B2C projection contracts
