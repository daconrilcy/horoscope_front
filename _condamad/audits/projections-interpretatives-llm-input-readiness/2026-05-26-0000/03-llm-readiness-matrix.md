# LLM Readiness Matrix

| contract | producer | consumer | current-llm-use | readiness | ready parts | missing / limit |
|---|---|---|---|---|---|---|
| `structured_facts_v1` | `StructuredFactsV1Builder` | Projection endpoint and client builders | available-not-injected | partial | factuel; hashable; provenance; excluded surfaces | No narrative readiness flags, masking policy or prompt-specific grouping. |
| `beginner_summary_v1` | `BeginnerSummaryV1Builder` | B2C projection endpoint | product-only | missing | Client-safe reduced display | Too reduced and editorial; excludes `evidence_refs` and full facts. |
| `client_interpretation_projection_v1` | `ClientInterpretationProjectionV1Builder` | B2C projection endpoint | product-only | partial | Plan granularity, shaping, section skeletons, exclusion list | Product shaping can mask facts; not injected and not canonical. |
| `AINarrativeInputContract` | `AINarrativeInputBuilder` | Future scoring/narration owner by contract intent; tests today | available-not-injected | ready | factuel; signal interpretatif; readiness_flags; source_versions; masking_policy; projection links | Needs architecture decision and wiring into `NatalExecutionInput`/prompt path before `injected`. |
| `narrative_answer_audit_v1` | `UserNatalInterpretationModel`, audit helpers | Persistence/rejection workflow | audit-only | ready | hashes, prompt refs, provider/model, evidence_refs, grounding status | Post-generation evidence; not prompt context. |

## Current LLM Use

current-llm-use classifications:

- `injected`: none of the five audited recent contracts under current evidence.
- `available-not-injected`: `structured_facts_v1`, `AINarrativeInputContract`.
- `product-only`: `beginner_summary_v1`, `client_interpretation_projection_v1`.
- `audit-only`: `narrative_answer_audit_v1`.

## Readiness Verdict

recommended-target: `AINarrativeInputContract`.

Required future proof before changing status to `injected`:

- before/after evidence that `NatalExecutionInput` or a replacement runtime contract consumes the target.
- no prompt payload or provider response added to domain builders.
- test evidence preserving public projection behavior.
- hash evidence for `projection_hash` and `llm_input_hash`.

