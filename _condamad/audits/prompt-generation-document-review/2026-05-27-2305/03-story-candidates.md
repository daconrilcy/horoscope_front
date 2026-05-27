<!-- Commentaire global: propositions de stories documentaires issues de l'audit adversarial CS-351. -->

# Story Candidates

## SC-001 clarify validation-audit-provider metadata wording

- Source finding: F-001
- Suggested story title: Clarifier les roles validation et audit dans la cartographie prompt LLM
- Suggested archetype: documentation-correction
- Primary domain: condamad-audit-documentation
- Required contracts: Runtime Source of Truth; Ownership Routing; Reintroduction Guard; Persistent Evidence
- Draft objective: Update only `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` so it states that `evidence`, `evidence_refs`, `grounding_status` and `validation_owner` are excluded from prompt material, validation-owned, and may feed audit persistence.
- Closure intent: full-closure
- Must include: cite CS-346, CS-347, CS-348 and code owners; avoid any runtime code edit; preserve the blocker wording for output schema ownership and bounded semantic grounding; no wildcard allowlist; no promotion of fallback, legacy, seed, test or audit-only paths to runtime truth.
- Validation hints: run targeted `rg` scans for `validation-only`, `audit-only`, `runtime/provider-only`, `request_id`, `trace_id`, `evidence_refs`, `prompt-visible`, `fallback`, `legacy`, `seed`, `LLMGateway`, `PromptRenderer`, and `llm_astrology_input_v1` under `_condamad/docs/prompt-generation-cartography`.
- Blockers: stop if product wants complete semantic proof, provider privacy policy changes, or a new canonical owner for output schemas; those are out of scope for a wording-only documentation story.

## SC-002 clarify provider metadata wording

- Source finding: F-002
- Suggested story title: Clarifier les metadonnees provider non prompt-visible
- Suggested archetype: documentation-correction
- Primary domain: condamad-audit-documentation
- Required contracts: Runtime Source of Truth; Ownership Routing; Reintroduction Guard; Persistent Evidence
- Draft objective: Update only `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` so `request_id`, `trace_id` and `use_case` are described as runtime/provider-only metadata rather than strictly backend-only runtime data.
- Closure intent: full-closure
- Must include: cite `LLMGateway._call_provider`, `ProviderRuntimeManager.execute_with_resilience` and `ResponsesClient.execute`; state that these values are not prompt-visible payload; avoid runtime, frontend, migration, test and source-code changes.
- Validation hints: run targeted `rg` scans for `backend-only runtime`, `runtime/provider-only`, `request_id`, `trace_id`, `x-request-id`, `x-trace-id`, `prompt-visible` and `provider`.
- Blockers: stop if privacy policy or provider-header behavior must change; that would be a separate runtime/security story, not a documentation correction.

## Exhaustive Files To Modify

### F-001

- Application files: none.
- Governance/test files: none.
- Documentation files: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Before evidence: targeted line scan for `validation-only`, `audit-only`, `evidence_refs`, `grounding_status`.
- After evidence: same scan plus source references to CS-346/CS-347/CS-348.
- Stop condition: source document distinguishes validation-owned fields from persisted audit anchors and still says they are not prompt-visible.

### F-002

- Application files: none.
- Governance/test files: none.
- Documentation files: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Before evidence: targeted line scan for `backend-only runtime`, `request_id`, `trace_id`, `provider-only`.
- After evidence: targeted scan proving `request_id` and `trace_id` are described as runtime/provider-only metadata and not prompt-visible payload.
- Stop condition: the document no longer implies trace identifiers stay strictly inside backend-only state.

## Deferred Non-Domain Context

- Runtime provider behavior, OpenAI headers, persistence schema, output validation and semantic verifier implementation are non-domain for this documentation-review audit.
- No implementation story is proposed for F-003 because it records an already-visible guardrail gap rather than a defect in the audited document.
