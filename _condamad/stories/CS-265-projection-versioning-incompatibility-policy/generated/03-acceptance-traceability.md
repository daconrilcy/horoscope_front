# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `projection_version` is documented as mandatory. | Policy states `projection_version` is mandatory and required for contracts, requests and persisted projections. | Targeted `rg`; architecture test PASS. | PASS |
| AC2 | Breaking changes force a v2 contract. | Policy defines breaking taxonomy and forbids silent breaking mutation of v1. | Targeted `rg`; architecture test PASS. | PASS |
| AC3 | Unknown versions are blocking. | Policy states unknown projection versions are blocking and cannot fallback. | Targeted `rg`; architecture test PASS. | PASS |
| AC4 | Deprecated versions are blocking. | Policy states deprecated / `dépréciée` versions are blocking and never silent aliases to v2. | Targeted `rg`; architecture test PASS. | PASS |
| AC5 | Incompatible `source_versions` block use. | Policy defines incompatible `source_versions` as blocking for read, reuse and derived persistence. | Targeted `rg`; architecture test PASS. | PASS |
| AC6 | Recalculation requires authorization. | Policy allows recalculation / `recalcul` only when the projection contract explicitly authorizes approved canonical sources. | Targeted `rg`; architecture test PASS. | PASS |
| AC7 | Strong compatibility is not promised. | Policy states no strong backward compatibility promise before stable public API or public B2B commitments. | Targeted `rg`; architecture test PASS. | PASS |
| AC8 | Existing runtime API surface stays unchanged. | No runtime implementation was added; test guard checks route and OpenAPI absence. | OpenAPI/routes Python checks PASS; architecture pytest PASS. | PASS |
| AC9 | Application source roots stay unchanged. | Story-owned edits avoided `backend/app`, `frontend/src`, DB and migrations. Pre-existing dirty app-root files from other stories remain. | Negative `rg` in `backend/app frontend/src` PASS; scoped status recorded in `evidence/app-surface-status.txt`. | PASS_WITH_LIMITATIONS |
| AC10 | Evidence artifacts are persisted. | Evidence folder and generated traceability/final evidence were completed. | Evidence files exist and capsule validation rerun after implementation. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
