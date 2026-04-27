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

## `runtime_openapi_contract`

Required evidence:

- command using `app.openapi()` or equivalent runtime app object;
- validates path, method, operationId, tags, status, or schema when applicable;
- static scans are secondary only.

Acceptable command:

```bash
python -c "from backend.app.main import app; schema = app.openapi(); assert '/v1/ai/generate' not in schema['paths']"
```

## `openapi_before_after_snapshot`

Required evidence:

- OpenAPI baseline artifact path before implementation;
- OpenAPI artifact path after implementation;
- explicit diff command or test;
- expected allowed differences.

## `route_absence_runtime`

Required evidence:

- runtime route table assertion;
- OpenAPI absence assertion when the app exposes OpenAPI;
- targeted static scan as secondary evidence.

## `python_import_absence`

Required evidence:

- import attempt that must fail;
- repo-wide scan for nominal import references;
- guard test when the import is architectural.

## `ast_architecture_guard`

Required evidence:

- AST-based or parser-based guard test;
- exact forbidden import/module/symbol list;
- allowlist register when exceptions exist.

## `repo_wide_negative_scan`

Required evidence:

- targeted symbol scan with exact tokens;
- zero-result expectation;
- paths intentionally excluded, if any.

## `targeted_forbidden_symbol_scan`

Required evidence:

- exact forbidden symbol, route, field, or import;
- bounded scan roots;
- command that fails on any match outside the allowlist.

## `allowlist_register_validated`

Required evidence:

- persisted allowlist or exception register;
- no wildcard or folder-wide exception;
- test or scan proving every exception is exact.

## `json_contract_shape`

Required evidence:

- JSON shape assertion for required and forbidden fields;
- status code assertion when HTTP is involved;
- generated schema or OpenAPI check when available.

## `api_error_shape_contract`

Required evidence:

- HTTP error envelope assertion;
- mapped and unmapped error cases;
- guard against local ad hoc error responses when centralized.

## `frontend_typecheck_no_orphan`

Required evidence:

- frontend typecheck;
- targeted tests for affected component/hook/client;
- negative scan for removed type or field.

## `baseline_before_after_diff`

Required evidence:

- baseline artifact path before implementation;
- after artifact path after implementation;
- explicit comparison command or test;
- expected allowed differences.

## `batch_migration_mapping`

Required evidence:

- mapping old surface to canonical surface;
- per-batch changed consumers;
- no-shim proof for each batch.

## `reintroduction_guard`

Required evidence:

- deterministic guard test or script;
- exact forbidden examples;
- proof that guard is run in validation plan.

## `external_usage_blocker`

Required evidence:

- external usage audit source;
- explicit blocker condition;
- user decision artifact when deletion is blocked or approved.
