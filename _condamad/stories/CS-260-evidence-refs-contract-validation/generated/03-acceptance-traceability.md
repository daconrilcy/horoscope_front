# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `evidence_refs` is documented as a versioned contract. | `docs/architecture/evidence-refs-contract.md` defines `contract_id`, `contract_version`, owner and role. | `evidence/contract-rg.txt`; `evidence/contract-shape-rg.txt`; `evidence/git-diff-check.txt`. | PASS |
| AC2 | Each audited section can carry proof references. | Contract defines stable audited `section_id` and section-level proof linkage. | `evidence/contract-shape-rg.txt` lines for `section_id` and section audit wording. | PASS |
| AC3 | Proof reference fields are explicit. | Contract table defines `evidence_ref_id`, `section_id`, `source_type`, `source_id`, `source_version`, `source_hash`, `validation_state`, `grounding_status`. | `evidence/contract-shape-rg.txt`. | PASS |
| AC4 | Authorized source kinds are explicit. | Contract limits `source_type` to `structured_fact`, `interpretive_signal`, `projection_version` and ties them to CS-256/CS-259 vocabulary. | `evidence/contract-shape-rg.txt`; source files inspected: structured facts, narrative audit, AI narrative input, projection governance. | PASS |
| AC5 | Source validation is mandatory. | Contract requires validated source, version and stable hash; invalid states include missing source, unsupported type, missing hash, hash mismatch. | `evidence/contract-shape-rg.txt`; `evidence/contract-rg.txt`. | PASS |
| AC6 | Missing proof can mark a section unfounded. | Contract defines `grounded`, `partial`, `unfounded`, `not_checked`; invalid or missing expected proof can drive `unfounded`. | `evidence/contract-shape-rg.txt`. | PASS |
| AC7 | Client support wording is separated from admin technical proof. | Contract separates `admin_proof` from `client_support` and forbids hashes/audit rows/provider internals in client-facing support. | `evidence/contract-shape-rg.txt`; `evidence/contract-rg.txt`. | PASS |
| AC8 | Public API surface stays unchanged. | No backend route, OpenAPI schema, serializer or frontend source was added for `evidence_refs`. | `evidence/openapi-routes.txt` reports `contains_evidence_refs=False`; `evidence/pytest.txt` reports 3236 passed, 1 skipped, 1182 deselected. | PASS |
| AC9 | Application source surfaces remain unchanged. | Intended delta is the architecture contract plus CS-260 evidence/capsule artifacts. | `evidence/app-surface-status.txt`; `git status --short -- backend/app frontend/src backend/migrations frontend` had no application-surface output before evidence append. | PASS |
| AC10 | Evidence artifacts are persisted. | Evidence folder contains validation, OpenAPI/routes, lint, pytest, diff and scoped status outputs. | `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/**`; capsule validation PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
