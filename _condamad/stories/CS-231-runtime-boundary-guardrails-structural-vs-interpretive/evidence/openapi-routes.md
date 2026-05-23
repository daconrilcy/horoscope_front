# CS-231 API Neutrality Evidence

## TestClient / OpenAPI

Command:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from fastapi.testclient import TestClient; from app.main import app; routes=sorted({route.path for route in app.routes}); openapi=app.openapi(); response=TestClient(app).get('/openapi.json'); paths=openapi.get('paths', {}); schemas=openapi.get('components', {}).get('schemas', {}); print('routes=%s openapi_paths=%s schemas=%s testclient_status=%s has_openapi=%s' % (len(routes), len(paths), len(schemas), response.status_code, '/openapi.json' in routes))"
```

Result:

```text
routes=197 openapi_paths=193 schemas=544 testclient_status=200 has_openapi=True
```

## Architecture Test

Command:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -m pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Covered by targeted suite:

```text
20 passed in 3.52s
```

## Public Surface Diff

Command:

```powershell
git diff -- backend/app/api backend/alembic frontend/src
```

Result:

```text
No diff.
```

## Local Startup Smoke

Command:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Result after requesting `http://127.0.0.1:8765/openapi.json`:

```text
status=200 bytes=543969
```
