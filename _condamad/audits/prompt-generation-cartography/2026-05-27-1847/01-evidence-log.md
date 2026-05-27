<!-- Commentaire global: journal de preuves reproductibles pour l'audit CS-347. -->

# Evidence Log

| ID | Evidence type | Command / Source | Inspected path or surface | Result | Notes |
|---|---|---|---|---|---|
| E-001 | story-source | `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/00-story.md` | CS-347 contract | PASS | Story is documentation-only. |
| E-002 | story-source | `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md` | audit scope | PASS | Brief does not authorize code changes. |
| E-003 | guardrail-source | `_condamad/stories/regression-guardrails.md` | RG-002 and RG-022 | PASS | No exact post-provider guardrail exists. |
| E-004 | prior-history | `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | CS-345 handoff | PASS | Used only as upstream context. |
| E-005 | prior-history | `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | CS-346 input sources | PASS | Used only as upstream context. |
| E-006 | source-scan | `rg -n -e class ValidationResult -e def parse_json -e def validate_schema -e def normalize_fields -e def sanitize_evidence -e def validate_output backend/app/domain/llm/runtime/output_validator.py` | output validation pipeline | PASS | Static source trace. |
| E-007 | source-scan | `rg -n -e def _validate_and_normalize -e def _handle_repair_or_fallback -e def _build_result -e log_call backend/app/domain/llm/runtime/gateway.py` | post-provider gateway steps | PASS | Static source trace. |
| E-008 | source-scan | `rg -n -e RejectedNarrativeAnswerOutcome -e CONTROLLED_REJECTED_CLIENT_MESSAGE -e build_rejected_narrative_answer_outcome -e emit_rejected_narrative_answer_log backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | rejection workflow | PASS | Static source trace. |
| E-009 | source-scan | `rg -n -e _apply_narrative_answer_audit -e _llm_input_hash_for_audit -e _projection_hash_for_audit -e _grounding_status_for_audit -e _evidence_refs_for_audit backend/app/services/llm_generation/natal/interpretation_service.py` | persistence anchors | PASS | Static source trace. |
| E-010 | source-scan | `rg -n -e answer_id -e projection_hash -e llm_input_hash -e prompt_version -e prompt_ref -e grounding_status -e evidence_refs backend/app/infra/db/models/user_natal_interpretation.py` | narrative audit model | PASS | Model evidence, not a DB migration diff. |
| E-011 | source-scan | `rg -n -e LlmCallLogModel -e tokens_in -e tokens_out -e validation_status -e repair_attempted -e fallback_triggered -e LlmReplaySnapshotModel backend/app/infra/db/models/llm/llm_observability.py` | call logs and replay tables | PASS | Model evidence, not runtime DB data. |
| E-012 | source-scan | `rg -n -e def log_call -e LlmCallLogModel -e ReplaySnapshotV1Service.create_snapshot -e evidence_warnings backend/app/domain/llm/runtime/observability_service.py` | observability persistence | PASS | Static source trace. |
| E-013 | source-scan | `rg -n -e REPLAY_SNAPSHOT_V1 -e def build_replay_snapshot_v1_metadata -e def create_snapshot -e def get_snapshot_metadata -e AuditService.record_event backend/app/services/replay_snapshot_v1_service.py` | replay metadata and audit | PASS | Static source trace. |
| E-014 | source-scan | `rg -n -e AdminReplaySnapshotV1 -e RejectedAnswerReview -e contract_id -e snapshot_id -e replay_attempt_id backend/app/services/api_contracts/admin/audit.py` | admin audit contracts | PASS | Contract evidence only. |
| E-015 | pytest | `pytest -q tests/llm_orchestration/test_output_validator_pipeline.py --tb=short` from `backend` after venv activation | output validation tests | PASS | 8 passed. |
| E-016 | pytest | `pytest -q tests/unit/test_rejected_narrative_answer_workflow.py tests/unit/test_rejected_narrative_answer_logging.py --tb=short` from `backend` after venv activation | rejected workflow tests | PASS | 13 passed. |
| E-017 | pytest | `pytest -q tests/unit/test_evidence_refs_validation.py tests/unit/test_evidence_refs_section_status.py --tb=short` from `backend` after venv activation | evidence refs tests | PASS | 10 passed. |
| E-018 | pytest | `pytest -q tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short --long` from `backend` after venv activation | audit persistence tests | PASS | 2 passed. |
| E-019 | pytest | `pytest -q tests/integration/test_llm_db_invariants.py --tb=short --long` from `backend` after venv activation | LLM DB invariants | PASS | 18 passed. |
| E-020 | pytest | `pytest -q tests/unit/test_replay_snapshot_v1_service_audit.py tests/unit/test_replay_snapshot_v1_service_manual_purge.py --tb=short` from `backend` after venv activation | replay audit tests | PASS | 4 passed. |
| E-021 | pytest | `pytest -q tests/unit/test_admin_endpoint_segmentation_contract.py --tb=short` from `backend` after venv activation | admin segmentation | PASS | 5 passed. |
| E-022 | read-only-guard | `git status --short` | repository root | PASS | Pre-existing untracked `_condamad/run-state.json` only before audit writes. |
| E-023 | source-scan | `rg -n post-provider validation and replay terms backend/app backend/tests` | baseline scan artifact | PASS | Large scan kept as story evidence artifact. |
