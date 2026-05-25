# CS-289 Acceptance Traceability

| AC | Requirement | Status | Code evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | Decorative `evidence_ref` values are rejected. | PASS | `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`; `test_decorative_evidence_ref_is_rejected`. | Targeted pytest PASS; full pytest PASS. |
| AC2 | Hash-backed projection sources are accepted. | PASS | `EvidenceSourceProof` + `projection_version`; `test_hash_backed_projection_source_is_accepted`. | Targeted pytest PASS; full pytest PASS. |
| AC3 | Hash-backed LLM input sources are accepted. | PASS | `llm_input` proof anchor via `build_audit_source_proofs`; `test_hash_backed_llm_input_source_is_accepted`. | Targeted pytest PASS; full pytest PASS. |
| AC4 | Missing proof requirements stay distinct. | PASS | `EvidenceSectionRequirement(requires_evidence=False)` returns `not_required`. | `tests/unit/test_evidence_refs_section_status.py` PASS. |
| AC5 | Invalid section proof is classified. | PASS | `missing_source`, `unsupported_source_type`, `missing_hash`, `hash_mismatch` states. | Unit tests include decorative, missing and hash mismatch cases; full pytest PASS. |
| AC6 | `grounded` status is produced. | PASS | Section aggregation in `validate_evidence_refs_by_section`. | `test_grounded_partial_and_ungrounded_statuses_are_produced` PASS. |
| AC7 | `partial` status is produced. | PASS | Mixed valid/invalid refs aggregate to `partial`. | `test_grounded_partial_and_ungrounded_statuses_are_produced` PASS. |
| AC8 | `ungrounded` status is produced. | PASS | Missing/invalid required refs aggregate to `ungrounded`. | Unit tests PASS. |
| AC9 | Audit persists results. | PASS | `NarrativeAnswerAuditRepository.create` validates section requirements and stores section results in `evidence_refs`. | `tests/integration/test_narrative_answer_audit_evidence_refs.py` PASS. |
| AC10 | API runtime surface stays unchanged. | PASS | No route/schema added; runtime check asserts no `evidence_refs` route and no validator schema exposure. | `python -B -c "from app.main import app; ..."` PASS. |
| AC11 | Parallel validators are blocked. | PASS | Architecture guard finds one definition of `validate_evidence_refs_by_section`. | `tests/architecture/test_evidence_refs_validation_boundary.py` PASS; targeted rg recorded. |
| AC12 | Evidence artifacts are persisted. | PASS | `evidence/validation.txt`, `evidence/source-decision.md`, `evidence/app-surface-status.txt`, final evidence updated. | Capsule validation PASS after evidence update. |
