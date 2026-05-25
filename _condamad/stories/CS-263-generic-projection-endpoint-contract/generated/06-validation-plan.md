# Validation Plan

## Targeted checks

```bash
rg -n "/v1/astrology/projections|projection_type|projection_version|birth_input|chart_id|persist" .\docs .\_story_briefs
rg -n "projection_version.*obligatoire|obligatoire.*projection_version|chart_id.*birth_input|birth_input.*chart_id|calcul.*projection|projection.*calcul|dependency_unavailable|unauthorized|B2B|hors scope|techniques internes|interdites" docs\architecture\generic-projection-endpoint-contract.md
rg -n "/v1/astrology/projections" backend\app frontend\src
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```bash
git status --short -- backend/app frontend/src docs/architecture/generic-projection-endpoint-contract.md _condamad/stories/CS-263-generic-projection-endpoint-contract
git diff --check
```

## Lint / static checks

```bash
.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff check .; Pop-Location
.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -c "from app.main import app; assert '/v1/astrology/projections' not in app.openapi().get('paths', {})"; Pop-Location
.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -c "from app.main import app; assert all(getattr(route, 'path', '') != '/v1/astrology/projections' for route in app.routes)"; Pop-Location
.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -c "from fastapi.testclient import TestClient; from app.main import app; response = TestClient(app).post('/v1/astrology/projections', json={}); assert response.status_code == 404"; Pop-Location
```

## Full regression checks

```bash
.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q --tb=short; Pop-Location
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-263-generic-projection-endpoint-contract
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
