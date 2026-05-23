# CS-232 Public Contract Evidence

## API

Commande:

```powershell
.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from fastapi.testclient import TestClient; from app.main import app; routes=sorted({r.path for r in app.routes}); schemas=app.openapi().get('components',{}).get('schemas',{}); print('routes_count=', len(routes)); print('has_openapi=', '/openapi.json' in routes); print('aspect_runtime_schema=', 'AspectRuntimeData' in schemas); print('structural_schema=', 'AspectStructuralRuntimeData' in schemas); print('openapi_status=', TestClient(app).get('/openapi.json').status_code)"
```

Résultat:

- `routes_count= 197`
- `has_openapi= True`
- `aspect_runtime_schema= False`
- `structural_schema= False`
- `openapi_status= 200`
- review-fix alignment: `AspectResult` schema properties now remain structural only:
  `aspect_code`, `planet_a`, `planet_b`, `angle`, `orb`, `orb_used`, `orb_max`, `family`, `is_major`, `is_minor`.

Commande:

```powershell
.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py
```

Résultat après correction d'alignement brief: inclus dans `30 passed in 1.41s` avec `test_structural_runtime_boundary.py` et `test_chart_json_builder.py`.

## Frontend

Commande:

```powershell
rg -n "planet_positions|houses|advanced_conditions|fixed_star_conjunctions|interpretive_valence|energy_type" frontend/src -g "*.ts" -g "*.tsx"
```

Résultat:

- usages publics confirmés pour `planet_positions`, `houses` et `advanced_conditions` dans les types, pages et tests natal chart.
- aucun usage frontend de `interpretive_valence` ou `energy_type` dans `frontend/src`.
- delta OpenAPI volontaire et borne: retrait des aliases plats `default_valence`, `interpretive_valence`, `energy_type` du schema public `AspectResult`; la clé JSON publique `aspects[].interpretive_valence` / `energy_type` reste fournie par `json_builder`.
- pas d'adaptation frontend nécessaire.

## TestClient

`TestClient(app).get("/openapi.json")` retourne `200` et un payload OpenAPI avec `paths`.
