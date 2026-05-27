<!-- Commentaire global: carte des symboles sources utilises pour l'audit CS-347. -->

# Output Validation Symbol Map

| Responsibility | Canonical owner | Symbols | Evidence |
|---|---|---|---|
| Output schema validation | `backend/app/domain/llm/runtime/output_validator.py` | `validate_output`, `ValidationResult`, `parse_json`, `validate_schema`, `normalize_fields`, `sanitize_evidence` | E-006, E-015 |
| Gateway post-provider sequence | `backend/app/domain/llm/runtime/gateway.py` | `_validate_and_normalize`, `_handle_repair_or_fallback`, `_build_result`, `log_call` | E-007 |
| Rejected answer workflow | `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | `RejectedNarrativeAnswerOutcome`, `build_rejected_narrative_answer_outcome_from_payload`, `emit_rejected_narrative_answer_log` | E-008, E-016 |
| Narrative audit persistence | `backend/app/services/llm_generation/natal/interpretation_service.py` | `_apply_narrative_answer_audit`, `_llm_input_hash_for_audit`, `_projection_hash_for_audit`, `_grounding_status_for_audit`, `_evidence_refs_for_audit` | E-009, E-018 |
| Narrative audit model | `backend/app/infra/db/models/user_natal_interpretation.py` | `UserNatalInterpretationModel`, `prompt_version`, `prompt_ref`, `projection_hash`, `llm_input_hash`, `evidence_refs`, `grounding_status` | E-010 |
| LLM call logs and replay models | `backend/app/infra/db/models/llm/llm_observability.py` | `LlmCallLogModel`, `LlmCallLogOperationalMetadataModel`, `LlmReplaySnapshotModel` | E-011, E-019 |
| Observability persistence | `backend/app/domain/llm/runtime/observability_service.py` | `compute_input_hash`, `log_call`, `count_evidence_warnings`, `purge_expired_logs` | E-012 |
| Replay lifecycle | `backend/app/services/replay_snapshot_v1_service.py` | `build_replay_snapshot_v1_metadata`, `create_snapshot`, `get_snapshot_metadata`, `start_replay_attempt`, `purge_snapshot` | E-013, E-020 |
| Admin audit contracts | `backend/app/services/api_contracts/admin/audit.py` | `AdminReplaySnapshotV1MetadataResponse`, `RejectedAnswerReviewItem`, `RejectedAnswerReviewDetailResponse` | E-014, E-021 |
