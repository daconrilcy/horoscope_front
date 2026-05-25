# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | CS-295 through CS-298 evidence is reviewed. | `evidence/source-checklist.md` records final evidence, review and validation artifacts for CS-295, CS-296, CS-297 and CS-298. | Artifact existence check PASS; tracker rows for CS-295..CS-298 are `done`. | PASS |
| AC2 | CS-278 final evidence records closure. | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` rewritten as runtime closure evidence. | Runtime routes/OpenAPI checks PASS in `evidence/runtime-surface-status.txt`. | PASS |
| AC3 | CS-278 status changes only after proof. | `story-status.md` updates CS-278 to `done` only after CS-295..CS-298 evidence review and local validation. | Full backend pytest, lint, OpenAPI/routes and scans PASS before tracker update. | PASS |
| AC4 | The delivery report reflects final replay state. | `_condamad/reports/CS-256-CS-291-delivery-report.md` updated from pending replay runtime to delivered replay runtime. | `rg -n "CS-278\|replay_snapshot_v1\|runtime\|residual" _condamad/reports/CS-256-CS-291-delivery-report.md` PASS. | PASS |
| AC5 | Backend lint passes. | No app code changed by CS-299; full backend lint validates the current runtime candidate. | `ruff check .` from `backend`: PASS in `evidence/validation.txt`. | PASS |
| AC6 | Full backend pytest passes. | No new test needed for CS-299; existing CS-295..CS-298 tests prove runtime behavior. | `python -B -m pytest -q --tb=short` from `backend`: 3421 passed, 1 skipped, 1216 deselected. | PASS |
| AC7 | Runtime OpenAPI replay exposure is approved. | Approved exposure is only `/v1/admin/audit/replay_snapshot_v1/{snapshot_id}` and `/replay-attempt`. | `app.openapi()` assertion PASS in `evidence/runtime-surface-status.txt`. | PASS |
| AC8 | Runtime routes expose no public replay path. | FastAPI routes contain only the approved admin audit replay path family. | Corrected `app.routes` assertion PASS; public/root/support/client replay paths absent. | PASS |
| AC9 | Forbidden replay data is absent. | Replay runtime owner files do not contain raw prompt, birth data, coordinates, passwords or API keys. | `rg` negative scan PASS; replay redaction/audit safety pytest set PASS in `evidence/forbidden-data-scan.txt`. | PASS |
| AC10 | Persistent closure artifacts exist. | CS-278 final evidence, CS-299 evidence files, delivery report and tracker rows are updated. | Capsule validation and final diff checks PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
