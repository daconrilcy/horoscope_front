# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The admin diagnostic route is registered. | `backend/app/api/v1/routers/admin/chart_diagnostics.py`; `backend/app/api/v1/routers/registry.py`. | `VC1 route registered` in `evidence/validation.txt`; `routes-after.txt`. | PASS |
| AC2 | OpenAPI exposes the admin contract. | `AdminChartDiagnosticsResponse` in `backend/app/services/api_contracts/admin/chart_diagnostics.py`. | `VC2 openapi exposes contract`; `VC3 not public path`; `openapi-after.json`. | PASS |
| AC3 | Admin access succeeds. | Route uses an admin-only dependency with `AdminChartDiagnosticsService`. | `test_admin_chart_diagnostics_route_openapi_and_success_payload`. | PASS |
| AC4 | Non-admin access is denied. | Route dependency rejects authenticated non-admin users and logs the denied consultation. | `test_admin_chart_diagnostics_rejects_non_admin_user`. | PASS |
| AC5 | Sensitive diagnostic fields are masked. | `chart_reference` is hashed via `redact_value(..., PolicyAction.HASHED)`; raw source fields omitted. | `test_admin_chart_diagnostics_redaction.py`; raw source-field negative scan. | PASS |
| AC6 | Each consultation is logged. | Service records successful and denied `admin_chart_diagnostics_consulted` events with sanitized metadata only. | `test_admin_chart_diagnostics_logs_consultation`; denied assertion in `test_admin_chart_diagnostics_rejects_non_admin_user`. | PASS |
| AC7 | Missing source errors are typed. | `AdminChartDiagnosticsSourceMissingError` maps to `admin_chart_diagnostics_source_missing`. | `test_admin_chart_diagnostics_missing_source_is_typed`. | PASS |
| AC8 | Replay stays separate. | No replay owner/import in diagnostic service; limits declare replay excluded. | `test_diagnostic_service_keeps_replay_and_answer_audit_separate`; replay/import negative scan. | PASS |
| AC9 | Narrative answer audit stays separate. | Diagnostic route/service do not import answer-audit routers or rejected-answer services. | `test_diagnostic_service_keeps_replay_and_answer_audit_separate`; replay/import negative scan. | PASS |
| AC10 | Duplicate diagnostic owners are absent. | One canonical route owner, one service owner, one contract owner. | `test_canonical_owners_are_unique`; owner scan in `validation.txt`. | PASS |
| AC11 | Evidence artifacts are persisted. | `evidence/openapi-before.json`, `openapi-after.json`, `routes-after.txt`, `validation.txt`, `source-checklist.md`. | Evidence path checks implied by files present; capsule validation PASS before implementation and final evidence updated. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
