# API Neutrality Evidence

- `app.openapi()` does not contain `transit_chart_v1`.
- `app.routes` contains no route path with `transit`.
- `TestClient(app).get('/openapi.json')` returns HTTP 200.
- `rg -n "transit_chart_v1|TransitChartRuntime|TransitToNatal" backend/app/api frontend/src backend/migrations` returned no matches.
- `rg -n "(/transit|/transits|/temporal|/forecast)" backend/app/api frontend/src` returned no matches.

The runtime is implemented only under `backend/app/domain/astrology/runtime/transit_chart_runtime.py`.
