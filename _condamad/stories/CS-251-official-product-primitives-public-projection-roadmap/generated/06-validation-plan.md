# Validation Plan

## Targeted checks

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='backend'
python -B -m pytest -q backend\tests\integration\astrology\test_natal_public_contract_compatibility.py backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\architecture\test_api_contract_neutrality.py
```

## Architecture / negative scans

```powershell
rg -n "structured facts|beginner summary|expert technical projection|fixed-star contacts|LLM input" docs\architecture
rg -n "API contract|frontend client|UI component|needs-user-decision" docs\architecture\official-product-primitives-public-projections.md
$env:PYTHONPATH='backend'; python -B -c "from app.main import app; data=str(app.openapi()); assert 'ChartObjectRuntimeData' not in data; assert 'chart_objects' not in data; assert 'interpretation_input' not in data"
$env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert all('chart_objects' not in getattr(r, 'path', '') for r in app.routes); assert all('interpretation-input' not in getattr(r, 'path', '') for r in app.routes)"
```

## Lint / static checks

```powershell
ruff format backend\tests\integration\astrology\test_natal_public_contract_compatibility.py backend\tests\architecture\test_api_contract_neutrality.py
ruff check backend
```

## Full regression checks

```powershell
$env:PYTHONPATH='backend'
python -B -m pytest -q
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
