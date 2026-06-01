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

## Modified files

- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/**`

## Forbidden or high-risk files

- `backend/**` remains out of scope for CS-439.
- Billing/admin entitlement production code remains out of scope; only one admin prompt test fixture was renamed to avoid positive old-use-case coverage.
