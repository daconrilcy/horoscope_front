# Acceptance Traceability

| AC | Requirement | Status |
|---|---|---|
| AC1 | `structured_facts_v1` is documented. | PASS |
| AC2 | Authorized fact families are explicit. | PASS |
| AC3 | Hashability rules are explicit. | PASS |
| AC4 | Narrative content is forbidden. | PASS |
| AC5 | AI input linkage is explicit. | PASS |
| AC6 | B2C direct consumption is not required. | PASS |
| AC7 | Raw runtime surfaces remain outside public scope. | PASS |
| AC8 | Application source surfaces remain unchanged. | PASS |
| AC9 | Evidence artifacts are persisted. | PASS |

## AC1 - `structured_facts_v1` Is Documented

- Implementation: `docs/architecture/structured-facts-v1-contract.md` is the canonical documentation-only contract.
- Validation: path existence check and capsule validation PASS.
- Status: PASS.

## AC2 - Authorized Fact Families Are Explicit

- Implementation: contract lists `positions`, `houses`, `major aspects`, `dominants` and `source metadata`.
- Validation: required-family `rg` scan PASS.
- Status: PASS.

## AC3 - Hashability Rules Are Explicit

- Implementation: contract defines stable ordering, deterministic serialization, hash input boundary and AI audit purpose.
- Validation: hash-rule `rg` scan PASS.
- Status: PASS.

## AC4 - Narrative Content Is Forbidden

- Implementation: contract marks `structured_facts_v1` as non narrative and excludes prompt/prose/advice/LLM output.
- Validation: non-narrative `rg` scan PASS.
- Status: PASS.

## AC5 - AI Input Linkage Is Explicit

- Implementation: `AINarrativeInputContract` may consume/reference the projection downstream without owning calculation truth.
- Validation: AI-linkage `rg` scan PASS.
- Status: PASS.

## AC6 - B2C Direct Consumption Is Not Required

- Implementation: `consumer_policy` says future consumers are optional and B2C direct consumption is not mandatory.
- Validation: B2C/consumer-policy `rg` scan PASS.
- Status: PASS.

## AC7 - Raw Runtime Surfaces Remain Outside Public Scope

- Implementation: contract excludes `ChartObjectRuntimeData`, raw `chart_objects`, debug traces and internal payloads.
- Validation: OpenAPI/routes assertions and raw-surface `rg` scan PASS.
- Status: PASS.

## AC8 - Application Source Surfaces Remain Unchanged

- Implementation: no `backend/app/**` or `frontend/src/**` edits.
- Validation: `git status --short -- backend/app frontend/src` returned no output.
- Status: PASS.

## AC9 - Evidence Artifacts Are Persisted

- Implementation: evidence folder contains validation, app-surface status and source checklist.
- Validation: evidence path checks PASS.
- Status: PASS.

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
