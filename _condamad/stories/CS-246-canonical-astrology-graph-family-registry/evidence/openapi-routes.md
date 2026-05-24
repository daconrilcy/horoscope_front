# CS-246 API Neutrality Evidence

The story introduced no public route, serializer, schema, frontend type, or DB migration.

## Runtime checks

- `app.openapi()` does not contain `AstrologyGraphFamily`.
- `app.routes` contains no route path with `graph-family` or `graph_family`.
- `TestClient(app).get("/openapi.json")` returns HTTP 200 in `backend/tests/architecture/test_api_contract_neutrality.py`.

## Guard test

- `backend/tests/architecture/test_api_contract_neutrality.py::test_astrology_graph_family_registry_is_not_public_api_contract` asserts:
  - `AstrologyGraphFamilyMetadata` is absent from OpenAPI schemas.
  - `AstrologyGraphFamilyStatus` is absent from OpenAPI schemas.
  - no route path exposes `graph-family` or `graph_family`.

## No-drift scan

- `rg -n "graph-family|graph_family|AstrologyGraphFamily" backend\app\api frontend backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"` - PASS, no matches.
