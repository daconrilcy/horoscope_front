## CS-225 API Neutrality Evidence

### TestClient Smoke

Command:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location backend
python -B -c 'from fastapi.testclient import TestClient; from app.main import app; client=TestClient(app); response=client.get("/openapi.json"); schemas=app.openapi().get("components", {}).get("schemas", {}); print(f"routes={len(app.routes)} status={response.status_code} schemas={len(schemas)}")'
```

Result:

```text
routes=221 status=200 schemas=544
```

### Automated Test

- `python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py`: PASS, 2 passed.
- OpenAPI schemas do not expose `CalculationGraphDefinition`,
  `CalculationNodeDefinition` or `CalculationInputDefinition`.
