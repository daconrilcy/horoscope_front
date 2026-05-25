# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `narrative_answer_audit_v1` is documented. | `docs/architecture/narrative-answer-audit-v1-contract.md` created with exact `contract_id` and role. | `validation.txt`: VC2, VC3, VC17. | PASS |
| AC2 | Mandatory identity fields are explicit. | Contract documents `answer_id`, `answer_type`, `chart_id`, `user_id`, `plan`, `projection_version`. | `validation.txt`: VC3, VC4. | PASS |
| AC3 | Mandatory hashes are explicit. | Contract requires `projection_hash` and `llm_input_hash` as non-optional audit anchors. | `validation.txt`: VC4, VC17. | PASS |
| AC4 | LLM provenance fields are explicit. | Contract documents `llm_input_version`, `llm_input_hash`, `prompt_version`, `provider`, `model`. | `validation.txt`: VC4, VC5. | PASS |
| AC5 | Grounding statuses are defined. | Contract defines `grounded`, `partial`, `ungrounded`, `rejected`, `not_checked`. | `validation.txt`: VC6. | PASS |
| AC6 | Answer categories are defined. | Contract defines `basic`, `premium`, `long`, `sensitive`, `free_short`. | `validation.txt`: VC7. | PASS |
| AC7 | Prompt evidence storage is defined. | Contract defines `full prompt` or `prompt_ref` plus `payload snapshot`. | `validation.txt`: VC5. | PASS |
| AC8 | Client proof exposure is forbidden. | Contract forbids technical proof, provider internals, prompt payloads and audit rows in client-facing payloads. | `validation.txt`: VC8. | PASS |
| AC9 | Public API surface stays unchanged. | No API, route, serializer or OpenAPI schema added. | `validation.txt`: VC9, VC10, VC11. | PASS |
| AC10 | Application source surfaces remain unchanged. | `app-surface-status.txt` records no status output for scoped app roots. | `validation.txt`: VC15, VC16; `app-surface-status.txt`. | PASS |
| AC11 | Evidence artifacts are persisted. | `evidence/validation.txt`, `evidence/app-surface-status.txt`, `evidence/source-checklist.md`. | Final capsule validation and file existence checks. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
