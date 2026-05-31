# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Basic complete uses `natal_interpretation`. | `backend/tests/integration/test_natal_basic_complete_v3_runtime.py::test_basic_complete_runtime_uses_natal_v3_and_persists_narrative` captures `NatalExecutionInput.use_case_key`. | `pytest --long ... test_natal_basic_complete_v3_runtime.py` PASS. | PASS |
| AC2 | Basic complete uses the basic assembly. | Adapter test builds `natal/interpretation/basic/fr-FR` and preserves plan `basic`; admin catalog test proves published Basic snapshot exposure. | `test_adapter_maps_basic_complete_to_natal_interpretation_assembly` PASS; `test_admin_llm_catalog_exposes_basic_natal_assembly_from_active_snapshot` PASS. | PASS |
| AC3 | Basic complete runtime uses schema V3. | Fake gateway returns `AstroResponse_v3`; service meta asserts `schema_version == "v3"`. | Backend targeted suite PASS. | PASS |
| AC4 | Accepted Basic complete persists narrative. | Runtime test verifies persisted JSON contains `narrative_natal_reading_v1` with non-empty `used_astrological_elements`. | Backend targeted suite PASS. | PASS |
| AC5 | Injected short V1/V2 output is rejected. | Existing schema guard asserts V2 payload becomes audited rejection with `natal_complete_schema_mismatch`. | `test_natal_interpretation_service_v3_schema_guard.py` PASS. | PASS |
| AC6 | Rejected short output stays private. | Existing public boundary tests keep rejected/audit rows out of public get/list. | `test_natal_interpretation_rejected_public_boundary.py` PASS. | PASS |
| AC7 | Public metas expose expected V3 status fields. | Runtime test asserts `use_case`, `schema_version`, `validation_status`, `repair_attempted`, `fallback_triggered`. | Backend targeted suite PASS. | PASS |
| AC8 | Quota is consumed only after acceptance. | Existing quota gate tests cover deferred debit, corrective regeneration and rejection path. | `test_natal_chart_long_quota_on_acceptance.py` PASS. | PASS |
| AC9 | `/natal` renders modern narrative. | Existing `NatalNarrativeReading` component tests render accessible narrative accordions. | `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard` PASS. | PASS |
| AC10 | `/natal` public DOM has no leak. | Existing public DOM guard asserts denylist absence and no legacy evidence/projection blocks in public branch. | `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard` PASS. | PASS |
| AC11 | Authenticated QA evidence is recorded. | QA report addendum records controlled local proof and test account context from existing natal QA report; no real provider call used. | Report path and evidence JSON persisted. | PASS_WITH_LIMITATIONS |
| AC12 | QA report names the root cause. | `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md` addendum names the Basic V3 runtime proof gap. | Evidence file path exists; final capsule validation PASS. | PASS |
| AC13 | App runtime contracts remain loadable. | Structured route/OpenAPI test and command check `app.routes` and `app.openapi()`. | `routes_openapi_ok` PASS; backend runtime test PASS. | PASS |
| AC14 | Story evidence artifacts are persisted. | `evidence/basic-complete-before.json`, `evidence/basic-complete-after.json`, generated traceability/final evidence. | Capsule validation PASS. | PASS |
| AC15 | QA report names changed files. | QA report addendum lists backend test, evidence artifacts and capsule files. | Final evidence consistency check PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
