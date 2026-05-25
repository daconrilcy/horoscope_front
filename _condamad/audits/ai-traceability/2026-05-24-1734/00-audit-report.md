# Audit Report - Existing Prompt Version And Answer Id Storage

## Scope

- Domain key: `ai-traceability`
- Domain boundary: backend AI traceability storage audit for CS-262.
- Audit archetype: custom `data-model-boundary-audit` plus No Legacy / DRY evidence.
- Read-only mode: application code, tests, migrations and frontend remained unchanged.
- Output folder: `_condamad/audits/ai-traceability/2026-05-24-1734/`

## Domain Closure Status

Status: open

The audited domain has existing partial storage, but no complete `narrative_answer_audit_v1` persistence owner. Follow-up implementation is required for `answer_id`, CS-259 hashes, grounding status, canonical provenance routing and implementation guards.

## Prior Audit And Story History Consulted

| Source | Status | Evidence | Classification |
|---|---|---|---|
| `_condamad/audits/ai-traceability/` | No prior same-domain audit folder before this run. | E-005 | none |
| `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` and `docs/architecture/narrative-answer-audit-v1-contract.md` | Target contract is done and defines required fields. | E-003 | active dependency |
| `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/00-story.md` | This story is audit-only. | E-001 | active request |
| `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md` | Future persistence story depends on this audit. | E-001, E-003 | deferred implementation |
| `_condamad/stories/regression-guardrails.md` | RG-002 and RG-022 apply; no exact AI traceability storage guardrail exists. | E-004, E-019 | active guardrail context |

## CS-259 Field Classification

| cs259_field | current_status | current_owner | storage_shape | runtime_path | gap_to_cs259 | migration_risk | recommended_next_action |
|---|---|---|---|---|---|---|---|
| `answer_id` | absent | none in backend app/tests/migrations | missing surface | none found by negative scan | CS-259 requires a stable generated answer identifier distinct from row or request IDs. | Existing `user_natal_interpretations.id` rows may need backfilled stable IDs. | Create or extend one canonical audit persistence owner. |
| `prompt_version` | partial | `UserNatalInterpretationModel.prompt_version_id`; `LlmCallLogModel.prompt_version_id`; `LlmPromptVersionModel.id` | nullable UUID/reference to `llm_prompt_versions` | `NatalInterpretationService` stores gateway meta prompt version; `observability_service.log_call` stores FK when existing | Current storage has prompt version references but no single answer-audit row with CS-259 semantics. | Nullable and missing-FK cases must be backfilled or explicitly handled. | Reuse existing prompt owners and route references from canonical audit rows. |
| `provider` | partial | `LlmCallLogOperationalMetadataModel.requested_provider/resolved_provider/executed_provider`; runtime gateway meta | nullable operational metadata | `observability_service.log_call` stores provider fields from runtime metadata | Provider provenance exists for LLM calls, not directly attached to persisted narrative answer rows. | Call log retention may outlive or underlive answer audit requirements. | Link or snapshot provider provenance from LLM observability. |
| `model` | partial | `LlmCallLogModel.model`; `GatewayMeta.model`; public response meta includes provider model in some service paths | string on call logs, runtime meta | Gateway sets model from resolved plan; observability stores `result.meta.model` | Model exists on LLM call logs but not in a canonical answer-audit record. | Model backfill requires joining persisted answer to the exact generation call. | Link or snapshot model provenance from LLM observability. |
| `full_prompt` | partial | `LlmPromptVersionModel.developer_prompt`; runtime `rendered_developer_prompt`; encrypted replay input | prompt template text and encrypted input payload, not answer-audit full prompt | Gateway renders prompt; observability stores encrypted user input; normal plan dumps exclude rendered prompt | No selected CS-259 full prompt retention mode for each answer. | Storing rendered prompts can over-retain user context and sensitive prompt payloads. | needs-user-decision before persistence design. |
| `prompt_ref` | partial | `prompt_version_id`, `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id`, `LlmReleaseSnapshotModel.version/manifest` | prompt/release references across existing tables | Gateway and observability carry prompt version and snapshot metadata | References exist but no answer-audit `prompt_ref` contract or variable payload snapshot. | References may become insufficient when call logs expire or prompts are changed. | Define audit-row reference routing and retention/backfill policy. |
| `prompt_payload_snapshot` | partial | `LlmReplaySnapshotModel.input_enc`; `LlmReleaseSnapshotModel.manifest` | encrypted replay input and release manifest snapshot | `observability_service.log_call` writes encrypted replay input | Existing snapshots are operational/replay-oriented, not named CS-259 prompt payload snapshots. | Replay snapshots expire quickly and may not cover audit retention. | Decide whether to reuse encrypted replay input or persist a separate audit payload snapshot. |

## Findings Summary

| Severity | Count | Findings |
|---|---:|---|
| Critical | 0 | none |
| High | 2 | F-001, F-002 |
| Medium | 3 | F-003, F-004, F-005 |
| Low | 0 | none |
| Info | 0 | none |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/00-story.md` | used | E-001 | Governing audit story. | none |
| `_story_briefs/cs-262-audit-existing-prompt-version-answer-id-storage.md` | used | E-002 | Source brief for audit scope. | none |
| `docs/architecture/narrative-answer-audit-v1-contract.md` | intentional-public-export | E-003 | Canonical documentation contract for `narrative_answer_audit_v1`. | Documentation contract only, not runtime storage. |
| `_condamad/stories/regression-guardrails.md` | used | E-004, E-019 | Required guardrail registry consulted; no update justified by this read-only audit. | Registry is large; targeted applicable guardrails were used. |
| `backend/app/infra/db/models/user_natal_interpretation.py::UserNatalInterpretationModel` | used | E-008, E-009, E-017 | Persists current natal interpretation rows and prompt version IDs. | Does not prove complete answer-audit semantics. |
| `backend/app/services/llm_generation/natal/interpretation_service.py::NatalInterpretationService` | used | E-009 | Writes and reads persisted natal interpretation payloads and prompt version metadata. | Source snippets were targeted to storage paths. |
| `backend/app/services/api_contracts/public/natal_interpretation.py::InterpretationMeta` | out-of-domain | E-010 | Public response metadata was inspected only to bound exposure; CS-262 does not implement public API changes. | Public contract is not the audit persistence owner. |
| `backend/app/infra/db/models/llm/llm_observability.py::LlmCallLogModel` | used | E-011, E-012, E-016, E-017 | Stores LLM prompt version, model, request/trace IDs and input hash. | Retention window may differ from answer audit retention. |
| `backend/app/infra/db/models/llm/llm_observability.py::LlmCallLogOperationalMetadataModel` | used | E-011, E-012, E-016 | Stores requested/resolved/executed provider metadata and active snapshot references. | Provider fields are linked to call logs, not answer rows. |
| `backend/app/infra/db/models/llm/llm_observability.py::LlmReplaySnapshotModel` | used | E-011, E-012, E-016 | Stores encrypted replay input (`input_enc`) for controlled replay. | Expiry and contents are not proven equivalent to CS-259 prompt payload snapshot. |
| `backend/app/domain/llm/runtime/observability_service.py::log_call` | used | E-012 | Runtime write path for LLM call log provenance and replay snapshot. | Runtime execution was not started; evidence is source/test inventory. |
| `backend/app/infra/db/models/llm/llm_prompt.py::LlmPromptVersionModel` | used | E-013, E-016, E-017 | Canonical prompt version table with `developer_prompt`. | Stores prompt template, not per-answer rendered prompt. |
| `backend/app/infra/db/repositories/llm/prompting_repository.py` | used | E-013 | Repository reads active/latest prompt versions and release snapshots. | No direct answer-audit storage responsibility. |
| `backend/app/infra/db/models/llm/llm_release.py::LlmReleaseSnapshotModel` | used | E-014 | Stores versioned release manifests referenced by runtime observability. | Manifest shape does not define CS-259 prompt payload snapshot. |
| `backend/app/domain/llm/runtime/gateway.py` | used | E-015 | Runtime carries prompt version, model, provider and rendered prompt metadata. | Gateway is not a persistence owner. |
| `backend/app/domain/llm/runtime/contracts.py::ResolvedExecutionPlan/GatewayMeta` | used | E-015 | Runtime contracts carry prompt/provenance metadata and intentionally exclude rendered prompt from dumps. | Contract fields are runtime only unless persisted elsewhere. |
| `backend/migrations/versions/**` | used | E-016 | Schema history proves existing tables and absence of `narrative_answer_audit_v1` migration. | Broad inventory; no migration files changed. |
| `backend/tests/**`, `backend/app/tests/**` selected LLM/natal tests | test-only | E-017 | Tests prove adjacent existing behavior for prompt version, call logs and persisted natal interpretations. | Existing tests do not cover CS-259 completeness. |
| `backend/app`, `backend/tests`, `frontend/src`, `backend/migrations` worktree status | out-of-domain | E-018 | Scoped status proves no forbidden application/test/frontend/migration changes occurred. | Only status at audit completion, not historical state before every command. |

## Closure Analysis

Active in-domain findings remain: F-001, F-002, F-003, F-004 and F-005.

Closed findings: none; this is the first same-domain audit and no implementation was performed.

Implementation files for active findings are not modified by this audit. Exhaustive implementation surfaces are listed in `03-story-candidates.md`:

- F-001: chosen canonical persistence owner for stable `answer_id`.
- F-002: chosen persistence owner plus deterministic hash/grounding source integrations.
- F-003: provenance routing from LLM prompt/observability owners.
- F-004: blocked by user/product retention decision.
- F-005: backend guard tests and no-duplicate-owner checks.

Governance/test files remain separate from application surfaces. Deferred non-domain concerns include admin API reads, rejected-answer workflow behavior and frontend exposure.

## DRY / No Legacy / Dependency Direction Assessment

- DRY: Existing prompt and LLM observability storage must be reused as evidence and source owners; creating a second prompt/provider/model store would duplicate active responsibility.
- No Legacy: No aliases, shims, fallback storage paths or compatibility documents were added by this audit.
- Mono-domain ownership: The audit keeps storage findings in backend AI traceability; public API/admin/front concerns are deferred.
- Dependency direction: No application dependency was changed; the future persistence owner should depend on DB/repository/domain contracts, not on API or frontend surfaces.

## Guardrail Decision

No update to `_condamad/stories/regression-guardrails.md` was made. The audit found a candidate invariant for future implementation, but no durable runtime guard exists yet. SC-004 records the guard candidate for story-writer handling.
