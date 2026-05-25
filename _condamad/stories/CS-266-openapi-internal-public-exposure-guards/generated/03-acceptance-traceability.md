# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Public OpenAPI omits forbidden internal tokens. | `backend/tests/architecture/test_api_contract_neutrality.py` adds `FORBIDDEN_PUBLIC_OPENAPI_PROJECTION_TOKENS` and checks serialized `app.openapi()`. | `python -B -m pytest -q tests\architecture\test_api_contract_neutrality.py --tb=short` PASS; runtime `ChartObjectRuntimeData` OpenAPI assertion PASS. | PASS |
| AC2 | Internal routes stay protected. | `backend/app/tests/integration/test_api_openapi_contract.py` exercises protected `admin`, `ops`, and `b2b` samples with `TestClient`; `/v1/internal` is asserted absent until explicitly mounted. | `python -B -m pytest -q app\tests\integration\test_api_openapi_contract.py --long --tb=short` PASS. | PASS |
| AC3 | Public route inventory is mapped. | Integration test maps public prefixes and protected route families from `app.routes` and `app.openapi()["paths"]`. | Targeted integration suite PASS; `/openapi.json` route inventory command PASS. | PASS |
| AC4 | Public OpenAPI schema is snapshot-checked. | `evidence/openapi-before.json` and `evidence/openapi-after.json` persisted from `app.openapi()`; comparison command asserted equality. | Snapshot write/compare command PASS. | PASS |
| AC5 | Forbidden token scan is automated. | Runtime OpenAPI token set is centralized in the architecture test; targeted `rg` scan covers public router/API-contract surfaces. | `rg` public-surface scan returned exit 1 with no matches, recorded as PASS. Broad backend scan has expected internal-domain/doc/test hits and is not a public exposure failure. | PASS |
| AC6 | Public/internal OpenAPI separation is documented. | Added `backend/docs/openapi-public-internal-boundary.md` and registered it in `backend/docs/ownership-index.md`. | Architecture test doc assertion PASS; `app/tests/unit/test_backend_docs_ownership.py` PASS. | PASS |
| AC7 | Story evidence artifacts are persisted. | `evidence/openapi-before.json`, `evidence/openapi-after.json`, `evidence/validation.txt`, traceability, final evidence, and story status are present. | Capsule validation PASS; story-status row set to `done` after clean implementation review. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
