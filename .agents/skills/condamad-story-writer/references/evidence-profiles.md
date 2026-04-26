# Evidence Profiles

<!-- Profils de preuves reutilisables pour les archetypes CONDAMAD. -->

Use evidence profiles to make acceptance evidence consistent and hard to
reinterpret. AC evidence may reference `Evidence profile: <name>` plus concrete
commands.

## `route_removed`

Required evidence:

- router registration absence;
- route path absence in app routes;
- OpenAPI absence;
- negative backend scan;
- tests updated.

Example:

```bash
pytest -q backend/app/tests/unit/test_api_router_architecture.py
python -c "from backend.app.main import app; assert all('/v1/ai' not in r.path for r in app.routes)"
python -c "from backend.app.main import app; assert '/v1/ai/generate' not in app.openapi()['paths']"
rg -n "/v1/ai|ai_engine_router" backend/app backend/tests
```

## `python_module_removed`

Required evidence:

```bash
python -c "import backend.app.api.v1.routers.public.ai"
# must fail
rg -n "routers.public.ai|public.ai" backend/app backend/tests
```

## `frontend_route_removed`

Required evidence:

```bash
rg -n "/admin/prompts/legacy" frontend/src
npm run test -- --run <targeted tests>
npm run typecheck
```

## `no_legacy_contract`

Required evidence:

```bash
rg -n "legacy|compat|shim|fallback|alias" <target paths>
pytest -q <architecture guard tests>
```

## `field_removed`

Required evidence:

```bash
rg -n "<removed field>" backend/app backend/tests frontend/src
pytest -q <targeted backend tests>
npm run typecheck
```

## `namespace_converged`

Required evidence:

```bash
rg -n "<old namespace>|<old import>" backend/app backend/tests
python -c "import <old namespace>"
# must fail when the namespace is removed
pytest -q <architecture guard tests>
```

