# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The diagnostics policy exists. | `docs/architecture/admin-chart-diagnostics-v1-policy.md` created with French global file comment. | `test_admin_chart_diagnostics_policy_exists_with_required_contract_fields`; policy path read by pytest. | PASS |
| AC2 | Diagnostic data categories are defined. | `retained_diagnostic_data` defines calculation facts, graph node status, source versions, proof references and diagnostic timings. | `rg -n "admin_chart_diagnostics_v1\|retention\|DPO-open\|redaction\|replay..." docs/architecture/admin-chart-diagnostics-v1-policy.md`. | PASS |
| AC3 | Birth data is sensitive. | `sensitive_data` and `redaction_policy` classify birth date, birth time, birth place, coordinates, user id and chart id. | `python -B -m pytest -q tests/unit/test_admin_chart_diagnostics_policy.py --tb=short` PASS; test reuses `FIELD_CLASSIFICATION`. | PASS |
| AC4 | Retention has a decision state. | `retention_policy` is explicitly `DPO-open` and lists blocked implementation surfaces. | Targeted `rg` found `DPO-open`, retention target and blocked surfaces in the policy. | PASS |
| AC5 | Replay is separate from diagnostics. | `replay_boundary` states current diagnostics are not replay snapshots and separates calculation replay, LLM replay and narrative answer audit. | Targeted pytest PASS; policy `rg` confirms replay boundary. | PASS |
| AC6 | Replay prerequisites are explicit. | `replay_prerequisites` lists storage owner, input reconstruction, version identity, retention approval and purge rules. | Targeted `rg` found all prerequisite terms. | PASS |
| AC7 | Admin consultations are logged. | `admin_access_log_fields` requires actor, role, action, decision, timestamp, subject reference and correlation id. | Targeted `rg` found the required log fields. | PASS |
| AC8 | Client surfaces are denied. | `denied_surfaces` denies clients, public OpenAPI, frontend, generated clients and B2C projection contracts. | Targeted pytest PASS. | PASS |
| AC9 | Public runtime exposure is absent. | No backend route, service, DB, migration or frontend file was added. Test asserts absence in `app.openapi()` and `app.routes`. | `python -B -c "from app.main import app; assert 'admin_chart_diagnostics' not in str(app.openapi())"` PASS; route command PASS. | PASS |
| AC10 | Application source surfaces remain unchanged. | Scoped git status shows only policy doc, targeted test and CS-275 evidence/status surfaces for this story. | `rg -n "admin_chart_diagnostics" backend/app/api backend/app/services backend/app/infra/db backend/migrations frontend/src ...` returned exit 1, treated as PASS: no matches. | PASS |
| AC11 | Evidence artifacts are persisted. | `generated/03-acceptance-traceability.md`, `generated/10-final-evidence.md`, `evidence/validation.txt`, `evidence/app-surface-status.txt`, `evidence/source-checklist.md`. | `condamad_validate.py _condamad/stories/CS-275-admin-chart-diagnostics-policy` PASS after updates. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
