# Validation Plan

## Targeted checks

```powershell
cd frontend
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi
```

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short
```

## Frontend quality gate

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run
```

## Static guards

```powershell
rg -n "free.*basic.*premium|basic.*premium|plan_code.*===" frontend/src/features/natal-chart frontend/src/components/natal-interpretation
rg -n "fetch\(.*/v1/astrology/projections|axios\(.*/v1/astrology/projections" frontend/src
rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"
git diff --check
```

Exit 1 is PASS for negative `rg` scans when no match is the expected result.
