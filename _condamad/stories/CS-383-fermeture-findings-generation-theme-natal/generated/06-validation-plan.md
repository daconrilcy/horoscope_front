# Validation Plan

## Targeted checks

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff check .
python -B -m pytest -q tests --tb=short -k "natal_chart or traditional_conditions or theme_astral or llm_astrology_input"
Pop-Location
```

```powershell
pnpm --dir frontend lint
pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage natalChartApi
pnpm --dir frontend build
```

## Runtime checks

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='backend'
python -B -c "from app.main import app; assert any('/v1/users/me/natal-chart' == getattr(r, 'path', '') for r in app.routes)"
python -B -c "from app.main import app; assert '/v1/users/me/natal-chart' in app.openapi()['paths']"
```

## Guard scans

```powershell
rg -n "style=" frontend/src/features/natal-chart/NatalExpertPanel.tsx
rg -n "sun\.house|sun_house|planet\.house|house_number\s*[<>=]|planet_code\s+in|includes\(planet_code\)|isHayz|hayz\s*=" frontend/src/features/natal-chart/NatalExpertPanel.tsx
rg -n "traditional_conditions|chart_json|natal_data|llm_astrology_input_v1|theme_astral_llm_input_v1" backend/app backend/tests frontend/src
```

## Rule for skipped commands

Record the exact command, reason not run, risk created, and compensating evidence.
