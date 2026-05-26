# Validation Plan

## Targeted checks

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c '<provider/blocker and ledger/catalog contract check>'
rg -n "<CS-311 forbidden field pattern>" _condamad\stories\CS-318-valider-ingestion-analytics-provider-cs316\evidence
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```powershell
rg -n "plausible\(|_paq\.push|window\.plausible|matomo" frontend\src\features
rg -n "<CS-311 forbidden field pattern>" _condamad\stories\CS-318-valider-ingestion-analytics-provider-cs316\evidence
git diff --check
```

## Lint / static checks

```powershell
cd frontend
pnpm lint
```

## Full regression checks

```powershell
cd frontend
node .\scripts\run-vite-logged.mjs vitest vitest run
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
