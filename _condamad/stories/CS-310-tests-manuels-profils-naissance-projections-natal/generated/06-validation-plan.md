# Validation Plan

## Capsule and evidence checks

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-310-tests-manuels-profils-naissance-projections-natal
python -B -c "<assert CS-310 profile, QA, anomaly, sensitive-surface and validation artifacts>"
```

## Frontend checks

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi
```

## Backend checks

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short
```

## Static guards

```powershell
rg -n "prompt|provider|replay|admin|debug|internal_payload|raw_runtime" frontend/src/pages frontend/src/features frontend/src/components
rg -n "fetch\(.*/v1/astrology/projections|axios\(.*/v1/astrology/projections" frontend/src
rg -n "style=" frontend/src/pages frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"
git diff --check
```

For negative scans, exit code `1` means `PASS: no matches`.

## Rule for skipped commands

Record exact command, reason not run, risk, and compensating evidence.
