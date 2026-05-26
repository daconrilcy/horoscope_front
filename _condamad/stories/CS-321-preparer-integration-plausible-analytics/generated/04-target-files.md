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

- `.env.example`
- `frontend/src/config/analytics.ts`
- `frontend/src/tests/useAnalytics.test.tsx`
- `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/**`
- `_condamad/stories/CS-321-preparer-integration-plausible-analytics/generated/**`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `backend/**` is out of scope.
- `frontend/src/features/**`, `frontend/src/pages/**`, and `frontend/src/api/**` must not receive direct provider calls.
- No Matomo configuration, dashboard, alerting, persistence, or provider account setup is authorized.
