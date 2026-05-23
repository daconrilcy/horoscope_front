# CS-229 API Neutrality Evidence

Command:

```powershell
.\.venv\Scripts\Activate.ps1; python -B -c "from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); spec=c.get('/openapi.json'); data=spec.json(); print('routes', len(app.routes)); print('openapi_status', spec.status_code); print('paths', len(data.get('paths', {}))); print('schemas', len(data.get('components', {}).get('schemas', {}))); print('has_aspect_structural_schema', 'AspectStructuralRuntimeData' in data.get('components', {}).get('schemas', {})); print('has_aspect_hints_schema', 'AspectInterpretiveHintsRuntimeData' in data.get('components', {}).get('schemas', {}));"
```

Result:

```text
routes 221
openapi_status 200
paths 193
schemas 544
has_aspect_structural_schema False
has_aspect_hints_schema False
```

Additional guard:

```powershell
.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py
```

Covered tokens: `app.routes`, `app.openapi()`, `TestClient`.

Public API result: no new aspect runtime schema, no interpretive hints schema and no aspect-runtime route.
