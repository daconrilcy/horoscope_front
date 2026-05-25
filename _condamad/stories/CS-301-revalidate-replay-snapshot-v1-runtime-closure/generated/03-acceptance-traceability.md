# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | The real replay path is proven. | No code change; proof story only. | `evidence/targeted-pytest.txt`: 21 passed, 1 deselected; CS-300 final evidence names `log_call -> create_snapshot -> replay`. | PASS |
| AC2 | Fabricated-only replay proof is rejected. | No fabricated fixture retained as closure proof. | `evidence/fabricated-proof-scan.txt`; only historical CS-300 evidence text mentions `encrypt_input(user_input)` as removed, not as success proof. | PASS |
| AC3 | CS-278 closure cites CS-300 repair proof. | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` updated. | Text check in final evidence; closure now references CS-300 and CS-301. | PASS |
| AC4 | CS-299 closure is corrected or superseded. | `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/generated/10-final-evidence.md` updated. | Text check in final evidence; CS-299 marked superseded by CS-300/CS-301. | PASS |
| AC5 | Delivery report states the repaired closure. | `_condamad/reports/CS-256-CS-291-delivery-report.md` updated. | Report now states CS-278 closure is valid after CS-300 repair and CS-301 revalidation. | PASS |
| AC6 | Replay targeted validations pass. | No code change. | `evidence/targeted-pytest.txt`: replay unit/integration/API/architecture set PASS. | PASS |
| AC7 | Backend lint passes. | No code change. | `evidence/ruff-check.txt`: `ruff check .` PASS from `backend`. | PASS |
| AC8 | Full backend pytest status is recorded. | No code change. | `evidence/full-backend-pytest.txt`: 3422 passed, 1 skipped, 1216 deselected. | PASS |
| AC9 | Runtime exposure stays internal. | No route or OpenAPI change. | `evidence/runtime-surface-status.txt`: only `/v1/admin/audit/replay_snapshot_v1/...` paths present. | PASS |
| AC10 | Forbidden replay data stays absent. | No DPO/security model change. | `evidence/forbidden-data-scan.txt` classified hits plus replay redaction tests in targeted pytest. | PASS |
| AC11 | Story evidence artifacts are persisted. | `CS-301/evidence/**`, final evidence, traceability, report and tracker updated. | Capsule validation PASS after evidence completion. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
