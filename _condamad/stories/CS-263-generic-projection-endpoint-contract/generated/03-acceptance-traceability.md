# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `POST /v1/astrology/projections` is documented. | Added `docs/architecture/generic-projection-endpoint-contract.md`. | `rg -n "/v1/astrology/projections|projection_type|projection_version|birth_input|chart_id|persist" .\docs .\_story_briefs`; evidence file `evidence/validation.txt`. | PASS |
| AC2 | Request payload fields are explicit. | Contract payload table defines `chart_id`, `birth_input`, `projection_type`, `projection_version`, `persist`. | Targeted `rg` found every field in the contract. | PASS |
| AC3 | `projection_version` is mandatory. | Contract states `projection_version` is obligatoire and no implicit/fallback version is allowed. | Targeted `rg` for mandatory version wording. | PASS |
| AC4 | Chart source selection is explicit. | Contract defines exactly one accepted source: `chart_id` or `birth_input`, with invalid ambiguous/missing cases. | Targeted `rg` for `chart_id`/`birth_input` rules. | PASS |
| AC5 | Service ownership stays separated. | Contract separates existing chart lookup, chart calculation, projection construction and authorization responsibilities. | Targeted `rg` for calculation/projection separation wording. | PASS |
| AC6 | Controlled error cases are explicit. | Contract defines 200, 201, 400, 401, 403, 404, 409 and 422 outcomes; unavailable dependencies are blocking and logged. | Targeted `rg` for `dependency_unavailable`, `unauthorized`, invalid payload and blocking/logged wording. | PASS |
| AC7 | B2C access rules are explicit. | Contract gates access by `projection_type`, plan or entitlement and names B2C eligible projection families. | Targeted `rg` for B2C access, plan and entitlement wording. | PASS |
| AC8 | Internal projections are denied to clients. | Contract denies `astrologer_debug_data`, `llm_input`, raw runtime/debug/prompt/provider/audit surfaces to B2C clients. | Targeted `rg` for internal technical projection denial wording. | PASS |
| AC9 | Public runtime API surface stays unchanged. | No backend or frontend runtime file changed. | `app.openapi()` route absence PASS; `app.routes` route absence PASS; `TestClient` POST returns 404; `rg` no runtime/frontend match. | PASS |
| AC10 | B2B API remains out of scope. | Contract explicitly excludes B2B, `/v1/b2b`, `/v1/partners`, partner payloads and enterprise integration guarantees. | Targeted `rg` for B2B exclusion wording and runtime route absence checks. | PASS |
| AC11 | Evidence artifacts are persisted. | Added `evidence/validation.txt`, `evidence/app-surface-status.txt`, `evidence/source-checklist.md`; completed generated evidence. | `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-263-generic-projection-endpoint-contract` PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
