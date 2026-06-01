# Validation Plan — CS-433

## Targeted checks

```powershell
pnpm --dir frontend test -- natalInterpretation NatalChartPage natalChartApi component-architecture
```

## Full frontend checks

```powershell
pnpm --dir frontend lint
pnpm --dir frontend test
pnpm --dir frontend build
```

## Guardrail scans

```powershell
rg -n "shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh|force_refresh|useCaseLevel|variantCode" frontend/src/api/natal-chart frontend/src/features/natal-chart/NatalInterpretation.tsx
rg -n "style=\{\{|style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation
rg -n "NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects" frontend/src/pages/NatalChartPage.tsx
rg -n "title=\{item\.evidenceId\}|ni-evidence-tags|ni-projections|LockedSection" frontend/src/components/natal-interpretation
rg -n "natal-narrative-reading__toggle" frontend/src/features/natal-chart/NatalNarrativeReading.tsx
git diff --check -- frontend/src/api/natal-chart/index.ts frontend/src/features/natal-chart/NatalInterpretation.tsx frontend/src/tests/natalChartApi.test.tsx frontend/src/tests/natalInterpretation.test.tsx frontend/src/tests/NatalChartPage.test.tsx frontend/src/tests/component-architecture-guards.test.ts _condamad/stories/CS-433-frontend-product-actions-no-technical-generation-controls
```

## Capsule checks

```powershell
.\.venv\Scripts\Activate.ps1; python -B .\.agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-433-frontend-product-actions-no-technical-generation-controls
.\.venv\Scripts\Activate.ps1; python -B .\.agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-433-frontend-product-actions-no-technical-generation-controls --final
```

## Skipped commands

- `pnpm --dir frontend test:e2e`: not run; this story changes API command wiring and component/unit-covered state handling, not a browser-only navigation or auth flow. Risk mitigated by full Vitest suite, build, lint, and route/component tests.
