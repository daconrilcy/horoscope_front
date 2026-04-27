# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Non-v1 API route exceptions are exact. | `app.api.route_exceptions` owns `/health`, `/api/email/unsubscribe`, and conditional internal QA metadata; runtime tests consume it. | `pytest -q app\tests\unit\test_api_router_architecture.py`; `route-exception-register.md`; runtime route snapshots. | PASS |
| AC2 | `main.py` cannot mount ad hoc API v1 routers. | `main.py` calls `include_api_v1_routers` and `include_registered_route_exceptions`; no direct v1 exception router import remains in `main.py`. | Architecture AST test `test_api_v1_router_registry_is_main_registration_source`. | PASS |
| AC3 | SQL/session/model use has before/after inventory. | Persisted `router-sql-inventory-before.md`, `router-sql-inventory-after.md`, and exact `router-sql-allowlist.md`. | Comparable scanner scope: before 852 entries; after 848 entries; architecture SQL allowlist test. | PASS |
| AC4 | New router DB usage fails outside allowlist. | AST guard detects SQLAlchemy/model/session imports, `db/session` calls, and positional/keyword `Depends(get_db_session)` in routers and API dependencies. | `test_api_sql_boundary_debt_matches_exact_allowlist`; SQL rg evidence. | PASS |
| AC5 | One dense-router DB flow moves to a service. | `PATCH /v1/admin/content/texts/{key}` persistence moved from router to `services.ops.admin_content.update_config_text_value`. | `test_admin_content_text_update_flow_delegates_persistence_to_service`; `pytest -q app\tests\integration\test_admin_content_api.py`. | PASS |
| AC6 | OpenAPI route surface is preserved. | No schema/path code change intended; before/after snapshots persisted. | `openapi-contract-diff.md` shows 0 missing, 0 added, 0 changed operations. | PASS |
| AC7 | F-001 observability ownership remains fixed. | Existing owner guard remains in architecture test. | `test_admin_llm_observability_routes_are_registered_once_from_canonical_router`; full architecture test passed. | PASS |
| AC8 | SQL allowlist rows require exact metadata. | Allowlist parser rejects wildcards, stale rows, missing reason, or missing decision. | `test_api_sql_boundary_debt_matches_exact_allowlist`; persisted allowlist table. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
