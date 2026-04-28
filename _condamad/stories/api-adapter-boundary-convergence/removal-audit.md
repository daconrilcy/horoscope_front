# Removal Audit - api-adapter-boundary-convergence

## Classification table

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `raise_http_error` | legacy helper | historical-facade | API routeurs publics/admin | `raise_api_error` | delete | Only guard text remains by scan. | Payloads now use canonical `error` envelope only. |
| `legacy_detail` | compatibility field | historical-facade | `ApiHttpError`, error handler | canonical `error.details` | delete | Only guard text remains by scan. | External clients using top-level `detail` would need migration. |
| top-level error `detail` | response compatibility | historical-facade | API error handler | `{"error": ...}` envelope | delete | `build_error_response` no longer writes `content["detail"]`; error tests pass. | Same as above. |
| FastAPI objects under former `app.api.v1.schemas.routers` | boundary leak | replace-consumer | API routers and services | `app.services.api_contracts` | replace-consumer | Old package removed; imports updated. | Broad import move, guarded by tests. |
| Residual `backend/app/api/v1/schemas` package | empty legacy namespace | dead | none | `app.services.api_contracts` | delete | Only tracked file was `backend/app/api/v1/schemas/__init__.py`; old imports have zero hits. | Recreating it would invite wrappers or re-exports to the old API-owned contract path. |
| `backend/app/services` imports from `app.api.*` | boundary leak | replace-consumer | service modules | `app.core.auth_context`, `app.core.api_constants`, `app.services.api_contracts` | replace-consumer | Non-API import scan returns zero hits. | DTO namespace changed for tests/importers. |
| `/api/email/unsubscribe` | public HTTP route | external-active | email unsubscribe links | existing route | keep | Present in OpenAPI; allowlisted in `NON_V1_ROUTE_EXCEPTIONS`. | Deletion still requires explicit migration decision. |
| API v1 router manual list in `main.py` | duplicate registry | historical-facade | app bootstrap | `app.api.v1.routers.registry` | replace-consumer | `main.py` calls `include_api_v1_routers(app)`; architecture guard passes. | Registry must be reviewed when routes are added. |

## OpenAPI evidence

- Before snapshot: not captured before code edits; limitation recorded in final evidence.
- After snapshot command completed successfully.
- After path count: 192.
- Explicit historical non-v1 paths after convergence:
  - `/health`
  - `/api/email/unsubscribe`

## Scan classification

| Pattern | Result | Classification | Action | Status |
|---|---|---|---|---|
| FastAPI imports/symbols in `app/api/v1/schemas` | zero hits | negative evidence | none | PASS |
| `app.api.v1.schemas` imports in `app tests` | zero hits | negative evidence | none | PASS |
| `backend/app/api/v1/schemas` package presence | deleted | dead namespace removed | keep deleted | PASS |
| `app.api` imports in non-API layers | zero hits | negative evidence | none | PASS |
| `raise_http_error|legacy_detail|content["detail"]` in API/tests | one test-guard hit | test_guard_expected_hit | keep guard | PASS |
