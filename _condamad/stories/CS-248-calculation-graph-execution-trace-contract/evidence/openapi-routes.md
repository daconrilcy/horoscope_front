# CS-248 API Neutrality Evidence

Command:

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='backend'
python -B -c "from app.main import app; assert 'ExecutionTrace' not in str(app.openapi())"
python -B -c "from app.main import app; assert not any('execution-trace' in getattr(r, 'path', '') for r in app.routes)"
```

Result: PASS.

Additional evidence:

- `python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py`: PASS as part of targeted validation.
- `TestClient` smoke remains covered by `test_calculation_graph_execution_trace_is_not_public_api_contract`.
- `app.routes` inventory contains no `execution-trace` route.
- `app.openapi()` contains no `ExecutionTrace` schema.
