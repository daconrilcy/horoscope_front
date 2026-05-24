# API neutrality evidence

Commands:

- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert 'temporal_technique_selection' not in str(app.openapi())"`: PASS.
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert not any('temporal' in getattr(r, 'path', '') for r in app.routes)"`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py`: PASS, `14 passed`.

Observed runtime snapshot:

- `route_count=221`.
- `temporal_in_routes=False`.
- `transit_in_routes=False`.
- `openapi_has_temporal_selection=False`.
- `openapi_has_transit_chart_v1=False`.
