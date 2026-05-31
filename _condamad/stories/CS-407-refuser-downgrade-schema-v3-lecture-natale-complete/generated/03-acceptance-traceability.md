# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Non-fallback complete V2/V1 output is rejected. | `interpretation_service.py` routes non-fallback complete Basic/Premium V3 failure to `v3_schema_mismatch`, not V2/V1. | `python -B -m pytest -q tests/unit/test_natal_interpretation_service_v3_schema_guard.py --tb=short` PASS. | PASS |
| AC2 | Cause is `natal_complete_schema_mismatch`. | `NATAL_COMPLETE_SCHEMA_MISMATCH` populates `rejection_reason.code`. | Schema guard unit test PASS. | PASS |
| AC3 | The rejection audit records `request_id`. | Rejection reason and validation context include `request_id`. | Schema guard unit test and updated legacy unit test PASS. | PASS |
| AC4 | Rejected payloads stay private. | Rejected mismatch uses `NarrativeAnswerAuditRepository`, not accepted user interpretation persistence. | `python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short --long` PASS. | PASS |
| AC5 | V3 error payloads remain accepted. | Non-fallback helper still accepts `AstroErrorResponseV3`. | Schema guard unit test PASS. | PASS |
| AC6 | Valid V3 complete payloads remain accepted. | Non-fallback helper returns `AstroResponseV3` with schema `v3`. | Schema guard unit test and stored-payload tests PASS. | PASS |
| AC7 | Gateway fallback remains explicitly observable. | Existing fallback path remains V1 and `GatewayMeta.fallback_triggered=True` is preserved. | Schema guard unit test PASS. | PASS |
| AC8 | The local generation path has no V3-to-V2/V1 conversion. | Downgrade constructors removed from non-fallback complete path. | Bounded `rg` anti-downgrade scan PASS: no matches. | PASS |
| AC9 | Mismatch rejection uses the narrative audit workflow. | `_persist_rejected_narrative_answer_audit` is reused for mismatch outcomes. | Stored-payload tests and updated legacy unit test PASS. | PASS |
| AC10 | Accepted persistence excludes rejected V2/V1. | Rejection returns before accepted `UserNatalInterpretationModel` persistence. | Stored-payload tests PASS. | PASS |
| AC11 | `natal_chart_long` is not consumed on rejection. | Rejection happens before accepted persistence; quota gate remains acceptance-scoped. | `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short` PASS. | PASS |
| AC12 | `free_short` keeps its short-schema behavior. | `free_short` branch is unchanged and still exits through `_generate_free_short`. | Schema guard unit test PASS for short/fallback shape. | PASS |
| AC13 | Public OpenAPI stays unchanged for natal routes. | No router or public schema files changed. | `python -B -c "from app.main import app; ..."` PASS. | PASS |
| AC14 | Story evidence artifacts are persisted. | Evidence files created under this story capsule. | Final capsule validation PASS after evidence sync. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
