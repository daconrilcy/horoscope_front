# Validation Plan

## Targeted checks

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx AdminPromptsCatalogFlow.test.tsx
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```powershell
rg -n "natal_long_free|natal_interpretation_short|use_case_level|forceRefresh|force_refresh|shouldRefreshShortAfterBasicUpgrade" frontend/src
rg -n "NatalInterpretationResult|mapProductActionDataToInterpretation|isNatalInterpretationResult" frontend/src/api/natal-chart frontend/src/features/natal-chart frontend/src/components/natal-interpretation
rg -n "variant_code|variantCode" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/api/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "style=\\{\\{" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages/NatalChartPage.tsx
git diff --check
```

## Lint / static checks

```powershell
pnpm --dir frontend lint
```

## Full regression checks

Not required for this frontend-only story. Backend pytest is out of scope because no backend files, routes, schemas, or migrations were modified.

## Local startup check

```powershell
frontend/node_modules/.bin/vite.cmd --host 127.0.0.1 --port 5174
Invoke-WebRequest http://127.0.0.1:5174
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
