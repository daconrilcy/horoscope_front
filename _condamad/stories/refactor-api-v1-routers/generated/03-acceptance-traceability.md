# Acceptance Traceability — refactor-api-v1-routers

| AC | Status | Implementation | Validation |
|---|---|---|---|
| AC1 | PASS | Route-by-route audit in `router-audit.md`. | Audit includes file, prefix, endpoints, schemas, helpers, backend/frontend refs, decision. |
| AC2 | PASS | Routers classified under canonical domain packages. | Architecture tests pass. |
| AC3 | PASS | Flat wrappers/re-exports removed. | Negative import and root package tests pass. |
| AC4 | PASS | Schemas extracted to `app/api/v1/schemas/routers`. | No `BaseModel` classes in routers; architecture guard added. |
| AC5 | PASS | Private helper logic extracted to `app/api/v1/router_logic`. | No private helper defs in routers; architecture guard added. |
| AC6 | NOT_APPLICABLE | No HTTP routes deleted. | Audit records preservation decision. |
| AC7 | PASS | URLs/tags/OpenAPI preserved through canonical imports. | OpenAPI contract tests pass. |
| AC8 | PASS | Ruff and backend tests run in activated venv. | `ruff`, targeted tests, `app/tests/integration`, and `tests/integration` pass. |
