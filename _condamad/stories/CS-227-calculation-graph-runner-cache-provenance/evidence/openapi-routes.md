## CS-227 API Neutrality Evidence

### Test Evidence
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py`
  - Covered through targeted suite: PASS, included in 21 passed.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests`
  - PASS: 827 passed, 200 deselected.

### Runtime Evidence
Command:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location backend
python -B -c "from app.main import app; from fastapi.testclient import TestClient; routes=sorted({r.path for r in app.routes}); schemas=app.openapi().get('components',{}).get('schemas',{}); response=TestClient(app).get('/openapi.json'); print('routes_count=', len(routes)); print('has_openapi_route=', '/openapi.json' in routes); print('testclient_status=', response.status_code); print('calculation_graph_schemas=', [k for k in schemas if 'CalculationGraph' in k or 'CalculationNode' in k or 'CalculationInput' in k]); print('calculation_graph_routes=', [p for p in routes if 'calculation-graph' in p])"
```

Output:

```text
routes_count= 197
has_openapi_route= True
testclient_status= 200
calculation_graph_schemas= []
calculation_graph_routes= []
```

Conclusion:

- `app.routes` remains inspectable.
- `app.openapi()` does not expose calculation graph schemas.
- `TestClient` can fetch `/openapi.json` with status 200.
- No public calculation graph route was added.
