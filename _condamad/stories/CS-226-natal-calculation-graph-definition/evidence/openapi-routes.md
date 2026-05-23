## CS-226 API Neutrality Evidence

### TestClient / OpenAPI
- Command: `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests\architecture\test_api_contract_neutrality.py`.
- Result: `2 passed`.
- Smoke uses `TestClient(app).get("/openapi.json")` and asserts status `200`.

### Runtime Snapshot
- `route_count= 221`.
- `openapi_paths= 193`.
- `has_calculation_graph_schema= False`.
- `has_calculation_graph_route= False`.

### Contract Neutrality
- `CalculationGraphDefinition`, `CalculationNodeDefinition`, and `CalculationInputDefinition` are absent from OpenAPI schemas.
- No route path containing `calculation-graph` is exposed.
- No frontend, API router, DB model, or migration file was modified for CS-226.
