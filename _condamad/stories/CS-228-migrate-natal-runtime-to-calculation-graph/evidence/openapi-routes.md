# CS-228 API Neutrality Evidence

## TestClient / OpenAPI

- `python -B -m pytest -q backend/tests/architecture/test_api_contract_neutrality.py` -> `2 passed`.
- `TestClient(app).get("/openapi.json")` returns HTTP 200 in `test_app_routes_remain_available_for_openapi_smoke`.
- `app.routes` count: `221`.
- `app.openapi()["paths"]` count: `193`.
- `/v1/astrology-engine/natal/calculate` remains registered: `True`.

## Public Contract

- No API router file was intentionally modified by CS-228.
- No frontend file was intentionally modified by CS-228.
- `rg -n "chart_objects" backend/app/api frontend/src` -> PASS: no matches.
- Existing public compatibility tests pass in the full backend suite: `833 passed, 201 deselected`.
