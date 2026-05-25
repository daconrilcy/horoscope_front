# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Existing projection owners are audited. | `client_interpretation_projection_v1_builder.py` imports `STRUCTURED_FACTS_V1_PROJECTION_ID` and reuses beginner disclaimer constants; no API/infra imports. | `test_builder_consumes_structured_facts_and_reuses_existing_owners`; targeted AST/import scan PASS. | PASS |
| AC2 | Free projection is generated. | Builder emits `free` sections `orientation_generale`, `points_forts`, `limite_de_lecture`, `upgrade_hint`. | `test_free_projection_is_short_and_client_safe`; `evidence/free-sample.json`. | PASS |
| AC3 | Basic projection is generated. | Builder emits basic sections plus audit-ready input. | `test_basic_projection_adds_audit_ready_content`; `evidence/basic-sample.json`. | PASS |
| AC4 | Premium projection is generated. | Builder emits premium-only deep sections and richer support elements. | `test_premium_projection_is_deepest_without_expert_payload`; `evidence/premium-sample.json`. | PASS |
| AC5 | Plan depth avoids raw runtime. | Builder consumes `Mapping` payload from `structured_facts_v1`, not natal runtime classes; active payload contains labels/signals only. | Forbidden import scan PASS (`rg` exit 1 for API/infra/provider imports); payload tests PASS. | PASS |
| AC6 | Entitlement denial is controlled. | `plan_insufficient` payload includes stable error fields, no technical payload. | `test_plan_insufficient_is_controlled`; `evidence/plan-insufficient-sample.json`. | PASS |
| AC7 | Disclaimer references are attached. | Builder reuses `BEGINNER_SUMMARY_V1_DISCLAIMER_CODES` and no-time disclaimer codes. | `test_disclaimer_codes_follow_application_policy`. | PASS |
| AC8 | Audit input is present. | `audit_input` exists only for basic/premium with section, support and signal identifiers. | `test_basic_projection_adds_audit_ready_content`; `test_premium_projection_is_deepest_without_expert_payload`. | PASS |
| AC9 | Public API surface stays unchanged. | No route/router/OpenAPI file modified; builder is domain-only. | `test_client_interpretation_projection_v1_stays_out_of_public_api_surface`; Python loaded-app guard PASS. | PASS |
| AC10 | Evidence artifacts are persisted. | `evidence/free-sample.json`, `basic-sample.json`, `premium-sample.json`, `plan-insufficient-sample.json`; generated evidence files updated. | Capsule validation PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
