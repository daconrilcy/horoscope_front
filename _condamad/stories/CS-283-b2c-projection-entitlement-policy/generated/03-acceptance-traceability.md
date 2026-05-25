# Acceptance Traceability

| AC | Requirement | Code / artifact evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The B2C entitlement policy is documented. | `docs/architecture/b2c-projection-entitlement-policy.md`; registry reference in `docs/architecture/official-product-primitives-public-projections.md`. | `evidence/validation.txt` VC2, VC3; `condamad_validate.py` PASS. | PASS |
| AC2 | Plan access is mapped per projection. | `Projection Matrix` maps `free`, `basic`, `premium` by projection. | `evidence/validation.txt` VC3. | PASS |
| AC3 | Client projection coverage is explicit. | `authorized_projections` names `structured_facts_v1`, `beginner_summary_v1`, `client_interpretation_projection_v1`. | `evidence/validation.txt` VC4. | PASS |
| AC4 | Internal projections are denied to B2C. | `Denied Internal Projections` blocks expert, admin, debug, raw runtime, prompt, provider and audit payload surfaces. | `evidence/validation.txt` VC5. | PASS |
| AC5 | Plan-insufficient errors are controlled. | `Plan Insufficient Error` defines `plan_insufficient`, `current_plan`, `required_plan`, `projection_id`, `upgrade_hint`. | `evidence/validation.txt` VC6. | PASS |
| AC6 | AI audit triggers are defined. | `Audit Trigger Policy` requires `narrative_answer_audit_v1` for basic, premium, long and sensitive outputs. | `evidence/validation.txt` VC7. | PASS |
| AC7 | Quota linkage follows existing decisions. | `Quota Policy` references existing quota/limit owners and requires a `separate product decision` for new quotas. | `evidence/validation.txt` VC8. | PASS |
| AC8 | Public API surface stays unchanged. | No route/schema code changed by this story; policy remains documentation-only. | `evidence/validation.txt` VC9, VC10, VC11. | PASS |
| AC9 | Application source surfaces remain unchanged. | This story changed docs and CONDAMAD artifacts only; scoped app dirty files were already present in initial `git status --short`. | `evidence/app-surface-status.txt`; fresh review diff of CS-283 paths; architecture pytest PASS. | PASS |
| AC10 | Evidence artifacts are persisted. | `evidence/validation.txt`, `evidence/app-surface-status.txt`, `evidence/source-checklist.md`, generated traceability and final evidence. | `evidence/validation.txt` VC13; capsule validation PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
