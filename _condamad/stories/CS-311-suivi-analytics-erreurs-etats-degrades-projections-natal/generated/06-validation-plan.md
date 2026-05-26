# Validation Plan - CS-311

## Targeted Frontend Tests

```powershell
cd frontend
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
```

## Frontend Quality Gate

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run
```

## Static Guards

```powershell
rg -n "birth_date|birth_time|birth_place|latitude|longitude|provider_response|raw_runtime|replay_snapshot|prompt|api_key|password" src
rg -n 'plausible\(|_paq\.push|console\.debug\(' frontend\src\features frontend\src\components frontend\src\api
rg -n "fetch\(.*/v1/astrology/projections|axios\(.*/v1/astrology/projections" frontend\src
rg -n "style=" frontend\src\features\natal-chart frontend\src\components\natal-interpretation -g "*.tsx"
git diff --check -- <CS-311 story paths>
```

## Local Startup

```powershell
cd frontend
pnpm dev -- --host 127.0.0.1
Invoke-WebRequest http://127.0.0.1:5173
```

## Not Required

- Backend pytest: no backend code or API contract changed.
- Playwright E2E: no route, auth, navigation, layout, or CSS behavior changed.
