# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Existing storage is classified before creation. | `evidence/storage-decision.md`; `UserNatalInterpretationModel` chosen over a new table after inspecting answer, LLM log and prompt owners. | `tests/architecture/test_narrative_answer_audit_persistence_boundary.py`; full pytest PASS. | PASS |
| AC2 | Audit records are persisted. | `NarrativeAnswerAuditRepository.create`; runtime write enrichment in `NatalInterpretationService`. | `tests/integration/test_narrative_answer_audit_repository.py`; full pytest PASS. | PASS |
| AC3 | Audit records are readable. | `NarrativeAnswerAuditRepository.get_by_answer_id`. | `tests/integration/test_narrative_answer_audit_repository.py`; full pytest PASS. | PASS |
| AC4 | CS-259 identity fields are stored. | `user_natal_interpretations` columns `answer_id`, `answer_type`, `chart_id`, `user_id`, `plan`, `created_at`. | `tests/unit/test_narrative_answer_audit_model.py`; `tests/integration/test_narrative_answer_audit_schema.py`. | PASS |
| AC5 | CS-259 hash fields are stored. | `projection_hash` and `llm_input_hash` columns; runtime hashes via `compute_projection_hash`. | `tests/unit/test_narrative_answer_audit_model.py`; full pytest PASS. | PASS |
| AC6 | LLM provenance fields are stored. | `llm_input_version`, `prompt_version`, `prompt_ref`, `prompt_snapshot_ref`, `provider`, `model`. | `tests/unit/test_narrative_answer_audit_model.py`; full pytest PASS. | PASS |
| AC7 | `answer_type` values are constrained. | `ALLOWED_NARRATIVE_ANSWER_TYPES`; DB check constraint. | `tests/unit/test_narrative_answer_audit_model.py`; repository invalid-value test. | PASS |
| AC8 | `grounding_status` values are constrained. | `ALLOWED_NARRATIVE_GROUNDING_STATUSES`; DB check constraint. | `tests/unit/test_narrative_answer_audit_model.py`; schema test. | PASS |
| AC9 | `evidence_refs` linkage is persisted. | JSON `evidence_refs` column and repository payload. | `tests/integration/test_narrative_answer_audit_repository.py`. | PASS |
| AC10 | Sensitive fields follow policy. | `sensitive_data.OPERATIONAL_FIELDS` covers refs/hashes/provider/model; raw `prompt` remains forbidden. | `tests/unit/test_narrative_answer_audit_sensitive_data.py`. | PASS |
| AC11 | Duplicate storage is blocked. | No audit table/model; repository uses existing owner. | `evidence/duplicate-owner-scan.txt`; architecture guard. | PASS |
| AC12 | Schema migration is validated. | Migration `20260525_0139` extends `user_natal_interpretations`; `schema-before.json` and `schema-after.json`. | `tests/integration/test_narrative_answer_audit_schema.py`; full pytest PASS. | PASS |
| AC13 | Evidence artifacts are persisted. | `evidence/storage-decision.md`, `schema-before.json`, `schema-after.json`, `validation.txt`, `duplicate-owner-scan.txt`. | Capsule validation PASS after evidence update. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
