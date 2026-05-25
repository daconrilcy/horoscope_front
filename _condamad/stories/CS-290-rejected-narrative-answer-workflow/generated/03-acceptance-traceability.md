# Acceptance Traceability - CS-290

| AC | Requirement | Status | Implementation evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | Ungrounded answers become rejected. | PASS | `rejected_answer_workflow.py` builds a rejected outcome when CS-289 returns `ungrounded`. | Unit workflow test PASS. |
| AC2 | Rejected records are persisted. | PASS | `NarrativeAnswerAuditRepository.create` persists `grounding_status="rejected"` on `UserNatalInterpretationModel`. | Integration audit test PASS. |
| AC3 | `rejection_reason` is stored. | PASS | Rejected payload requires and stores structured `rejection_reason.code`. | Integration audit test PASS. |
| AC4 | Validation context is stored. | PASS | Rejected payload stores CS-289 `validation_context`. | Integration audit test PASS. |
| AC5 | Client response is controlled. | PASS | Outcome client payload and natal service mapping use controlled wording. | Response masking test PASS. |
| AC6 | Raw AI answer stays internal. | PASS | Raw output is retained only under internal `raw_answer_storage`. | Response test and negative raw sentinel scan PASS. |
| AC7 | Internal log is emitted. | PASS | `emit_rejected_narrative_answer_log` emits event/request/trace/answer/use-case/reason fields. | Logging unit test PASS. |
| AC8 | Retry is not introduced. | PASS | No retry queue/worker/manual publish path; persisted `retry_policy` is `out_of_scope`. | Architecture guard and negative retry scan PASS. |
| AC9 | Public API runtime surface is unchanged. | PASS | No public/admin route added; OpenAPI excludes rejected answer internals. | Runtime `app.openapi()` and `app.routes` checks PASS. |
| AC10 | One workflow owner exists. | PASS | Single workflow owner is `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`. | Architecture guard PASS. |
| AC11 | Evidence artifacts are persisted. | PASS | Required CS-290 evidence files exist under `evidence/`. | Evidence path checks and capsule validation PASS. |

## Validation Summary

- `ruff format` on changed backend Python files: PASS.
- `ruff check .`: PASS.
- Targeted CS-290 pytest files: PASS (`7 passed, 2 deselected`).
- Full backend pytest: PASS (`3365 passed, 1 skipped, 1211 deselected`).
