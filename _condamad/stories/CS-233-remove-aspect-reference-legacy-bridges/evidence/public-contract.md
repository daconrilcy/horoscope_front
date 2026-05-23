# CS-233 Public Contract Evidence

## API Neutrality

Command:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from fastapi.testclient import TestClient; from app.main import app; paths=sorted({route.path for route in app.routes}); schemas=app.openapi().get('components',{}).get('schemas',{}); response=TestClient(app).get('/openapi.json'); print('routes_count=', len(paths)); print('openapi_status=', response.status_code); print('has_openapi_route=', '/openapi.json' in paths); print('aspect_schema_props=', sorted(schemas.get('AspectResult',{}).get('properties',{}))); print('legacy_props_present=', bool({'default_valence','interpretive_valence','energy_type'} & set(schemas.get('AspectResult',{}).get('properties',{}))))"
```

Result:

```text
routes_count= 197
openapi_status= 200
has_openapi_route= True
aspect_schema_props= ['angle', 'aspect_code', 'family', 'is_major', 'is_minor', 'orb', 'orb_max', 'orb_used', 'planet_a', 'planet_b']
legacy_props_present= False
```

Fresh brief-alignment review result on 2026-05-23 after story status correction: same output, run from repository root after `.\.venv\Scripts\Activate.ps1`.

## Public JSON

- `interpretive_valence` and `energy_type` remain public chart JSON keys.
- Source is now only `AspectResult.aspect_interpretive_hints`.
- Missing hints raise `ValueError("public aspect projection requires aspect_interpretive_hints")`.
- `backend/app/tests/unit/test_chart_json_builder.py` covers both public keys and missing-hints failure.

## Frontend Search

Command:

```powershell
rg -n "interpretive_valence|energy_type" frontend/src
```

Result: PASS: no matches.

## TestClient

- `backend/tests/architecture/test_api_contract_neutrality.py` verifies `app.routes`, `app.openapi()` and `TestClient(app).get("/openapi.json")`.
- Targeted run passed as part of the 86-test AC suite.
