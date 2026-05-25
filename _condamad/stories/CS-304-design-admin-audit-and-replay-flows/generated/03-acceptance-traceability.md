# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Admin flows are fully described. | `docs/architecture/admin-audit-replay-flows.md` defines list, detail, review status, audit review, replay metadata, replay attempt and purge confirmation screens with common states. | `evidence/doc-contract-check.txt`; `evidence/doc-before.txt`; `evidence/doc-after.txt`. | PASS |
| AC2 | Sensitive admin actions name audit events. | The contract maps answer reads, audit-log reads, review updates, replay metadata reads, replay attempts and purges to named audit events or blocking expectations. | `evidence/validation.txt` with `python -B -m pytest -q tests/api/admin/test_rejected_answer_review_workflow.py --tb=short` PASS plus review-fix contract scan. | PASS |
| AC3 | Forbidden sensitive fields are excluded. | The contract lists raw prompts, raw provider/model payloads, raw AI answer, birth data, exact coordinates, secrets and direct identifiers as excluded or masked. | `evidence/sensitive-field-scan.txt` PASS. | PASS |
| AC4 | Backend endpoints are named from runtime. | The contract names only consumed runtime endpoints from `app.routes` and `app.openapi()` for answer audits, audit logs and replay snapshot flows. | `evidence/route-inventory.txt`; `evidence/openapi-admin-paths.txt`. | PASS |
| AC5 | Internal admin access is a hard gate. | The contract blocks future UI work unless AuthN/AuthZ admin, audit logs and redaction are proved, and forbids public/support/B2C route families. | `evidence/route-absence.txt`; `evidence/validation.txt` with `python -B -m pytest -q tests/api/admin/test_replay_snapshot_v1_api.py --tb=short` PASS. | PASS |
| AC6 | Story evidence artifacts are persisted. | Capsule generated files and `evidence/*.txt`/`source-alignment.md` are persisted under the story directory. | `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-304-design-admin-audit-and-replay-flows` PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
