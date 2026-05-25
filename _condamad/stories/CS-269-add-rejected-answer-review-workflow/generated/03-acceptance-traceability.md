# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Admins can list rejected answers. | `backend/app/api/v1/routers/admin/answer_audit.py`; `RejectedAnswerReviewService.list_rejected_answers`; `RejectedAnswerReviewListResponse`. | `python -B -m pytest -q tests/api/admin/test_rejected_answer_review_workflow.py --tb=short` PASS. | PASS |
| AC2 | Admin detail shows rejection reason. | `get_rejected_answer_detail`; `RejectedAnswerReviewDetailResponse.rejection_reason`. | Targeted pytest checks `rejection_reason.code == evidence_hash_mismatch`. | PASS |
| AC3 | Missing proof indicators are visible. | `RejectedAnswerReviewItem.missing_evidence_refs`; `_as_missing_evidence_refs`. | Targeted pytest checks `missing_evidence_refs`. | PASS |
| AC4 | Version context is visible. | `prompt_version`, `projection_version`, `provider`, `model` fields in admin contracts and service mapper. | Targeted pytest checks all version/provider/model fields. | PASS |
| AC5 | Review statuses are internal. | `RejectedAnswerReviewStatus`; PATCH `/v1/admin/answer-audits/rejected/{answer_id}/review`; no public route or frontend change. | Targeted pytest checks status transition; runtime/OpenAPI forbidden path check PASS. | PASS |
| AC6 | Review actions are logged. | Service records `admin_rejected_answer_review_accessed` and `admin_rejected_answer_reviewed` through `AuditService.record_event` and `audit_events`. | Targeted pytest DB assertions PASS; `rg` action scan PASS. | PASS |
| AC7 | Public clients cannot read rejected content. | Route registered only under `/v1/admin/answer-audits/rejected`; no public router/frontend edits. | Runtime `app.routes`/`app.openapi()` checks PASS; `client-exposure-scan.txt`. | PASS |
| AC8 | Support public surface stays separate. | No `backend/app/api/v1/routers/public/**` edits; doc limits forbid public support workflow. | Forbidden route scan PASS; docs `rg "manual correction|prompt|contract|validation"` PASS. | PASS |
| AC9 | Admin workflow remains protected. | `require_admin_user` dependency on all review routes. | Targeted pytest checks 401 missing auth, 403 non-admin, 200 admin. | PASS |
| AC10 | No parallel audit store is added. | Reuses `AuditEventModel`/`AuditService`; no migration/model/repository added. | Negative `rg` over `backend/app` for parallel store/replay symbols returns exit 1 = PASS no matches. | PASS |
| AC11 | Evidence artifacts are persisted. | `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/*`; generated final evidence. | Capsule validation PASS after evidence update; evidence path checks PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
