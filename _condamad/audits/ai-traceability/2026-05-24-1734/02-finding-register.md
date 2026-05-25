# Finding Register - AI Traceability Audit

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | backend-ai-traceability-audit | E-003, E-006, E-008, E-009, E-016 | `narrative_answer_audit_v1` cannot use a stable narrative `answer_id`; current persisted answers use table `id` only and LLM call logs have request/call IDs without answer linkage. | Create or extend one canonical persistence owner that stores a stable `answer_id` and maps it to persisted answer rows and related LLM trace records. | yes |
| F-002 | High | High | data-integrity-risk | backend-ai-traceability-audit | E-003, E-007, E-008, E-009, E-011, E-012 | Mandatory `projection_hash`, `llm_input_hash` and `grounding_status` are absent from backend storage, so later audits cannot prove factual grounding or rejected-answer state. | Extend the selected canonical owner to persist CS-259 hashes and grounding status for generated and rejected answers. | yes |
| F-003 | Medium | High | missing-canonical-owner | backend-ai-traceability-audit | E-003, E-011, E-012, E-013, E-014, E-015 | Prompt provenance is split across answer rows, call logs, prompt versions and release snapshots; the current state is usable evidence but not one `narrative_answer_audit_v1` record. | Reuse existing prompt and LLM observability owners as source records, then define exact foreign-key/reference routing from answer audit persistence. | yes |
| F-004 | Medium | High | data-integrity-risk | backend-ai-traceability-audit | E-003, E-011, E-012, E-013, E-015, E-016 | Full prompt retention and `prompt_ref` plus payload snapshot are only partially covered: versioned developer prompts and encrypted replay input exist, but no per-answer prompt evidence mode is selected. | Require a product/retention decision before implementation chooses full prompt retention versus `prompt_ref` plus payload snapshot. | needs-user-decision |
| F-005 | Medium | High | missing-test-coverage | backend-ai-traceability-audit | E-003, E-016, E-017, E-018 | Existing tests prove adjacent prompt/version/log behavior, but no guard enforces complete CS-259 field coverage or prevents duplicate audit storage. | Add implementation-story guards for no duplicate storage, required CS-259 fields, migration backfill behavior and public-proof masking. | yes |

## F-001 Missing Stable Answer Id Storage

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: backend-ai-traceability-audit
- Evidence: E-003, E-006, E-008, E-009, E-016
- Expected rule: CS-259 requires `answer_id` as the stable identifier of each generated or rejected narrative answer.
- Actual state: `UserNatalInterpretationModel.id` is the row primary key and LLM call logs provide request/call IDs, but backend app/tests/migrations have no `answer_id` storage symbol.
- Impact: `narrative_answer_audit_v1` cannot use a stable narrative `answer_id`; current persisted answers use table `id` only and LLM call logs have request/call IDs without answer linkage.
- Recommended action: Create or extend one canonical persistence owner that stores a stable `answer_id` and maps it to persisted answer rows and related LLM trace records.
- Story candidate: yes
- Suggested archetype: data-model-boundary-convergence

## F-002 Missing CS-259 Hash And Grounding Storage

- Severity: High
- Confidence: High
- Category: data-integrity-risk
- Domain: backend-ai-traceability-audit
- Evidence: E-003, E-007, E-008, E-009, E-011, E-012
- Expected rule: CS-259 requires `projection_hash`, `llm_input_hash`, and `grounding_status` for auditable generated and rejected answers.
- Actual state: Existing LLM observability has `input_hash`, but backend storage has no `projection_hash`, no `llm_input_hash` name, and no `grounding_status` field.
- Impact: Mandatory `projection_hash`, `llm_input_hash` and `grounding_status` are absent from backend storage, so later audits cannot prove factual grounding or rejected-answer state.
- Recommended action: Extend the selected canonical owner to persist CS-259 hashes and grounding status for generated and rejected answers.
- Story candidate: yes
- Suggested archetype: data-model-boundary-convergence

## F-003 Split Prompt Provider And Model Provenance

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: backend-ai-traceability-audit
- Evidence: E-003, E-011, E-012, E-013, E-014, E-015
- Expected rule: The audit record must retain prompt version, provider and model provenance for each narrative answer.
- Actual state: `prompt_version_id` is stored on persisted answers and call logs, `model` and provider metadata are stored on LLM observability, and prompt text/release snapshots live in prompt/release tables.
- Impact: Prompt provenance is split across answer rows, call logs, prompt versions and release snapshots; the current state is usable evidence but not one `narrative_answer_audit_v1` record.
- Recommended action: Reuse existing prompt and LLM observability owners as source records, then define exact foreign-key/reference routing from answer audit persistence.
- Story candidate: yes
- Suggested archetype: repository-ownership-refactor

## F-004 Prompt Evidence Mode Is Not Decided

- Severity: Medium
- Confidence: High
- Category: data-integrity-risk
- Domain: backend-ai-traceability-audit
- Evidence: E-003, E-011, E-012, E-013, E-015, E-016
- Expected rule: CS-259 permits either full prompt retention or `prompt_ref` plus payload snapshot.
- Actual state: Versioned `developer_prompt` and encrypted replay input exist, and rendered prompts are runtime-only by default. No repository source selects the final retention mode for narrative answer audit rows.
- Impact: Full prompt retention and `prompt_ref` plus payload snapshot are only partially covered: versioned developer prompts and encrypted replay input exist, but no per-answer prompt evidence mode is selected.
- Recommended action: Require a product/retention decision before implementation chooses full prompt retention versus `prompt_ref` plus payload snapshot.
- Story candidate: needs-user-decision
- Suggested archetype: retention-policy-decision

## F-005 Missing Reintroduction Guard For Complete Audit Storage

- Severity: Medium
- Confidence: High
- Category: missing-test-coverage
- Domain: backend-ai-traceability-audit
- Evidence: E-003, E-016, E-017, E-018
- Expected rule: Future implementation should prove complete CS-259 coverage and no duplicate storage owner before adding persistence.
- Actual state: Tests cover prompt version propagation, LLM DB invariants and adjacent persisted answers, but not complete `narrative_answer_audit_v1` field coverage or duplicate-owner prevention.
- Impact: Existing tests prove adjacent prompt/version/log behavior, but no guard enforces complete CS-259 field coverage or prevents duplicate audit storage.
- Recommended action: Add implementation-story guards for no duplicate storage, required CS-259 fields, migration backfill behavior and public-proof masking.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
