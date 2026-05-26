# Validation Plan

## Targeted checks

```bash
cd frontend
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```bash
rg -n "plausible\(|window\.plausible|_paq" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api
rg -n "VITE_ANALYTICS_PROVIDER|VITE_ANALYTICS_DOMAIN|VITE_ANALYTICS_API_HOST|VITE_ANALYTICS_ENABLED" .env.example frontend docs
rg -n "matomo|MATOMO|_paq" .env.example docs frontend/src/config frontend/src/hooks frontend/src/tests
git diff --check
```

## Lint / static checks

```bash
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run inline-style-policy
rg -n "style=" src -g "*.tsx"
```

## Full regression checks

```bash
cd frontend
pnpm test
pnpm build
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
