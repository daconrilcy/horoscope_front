<!-- Commentaire global: registre des constats pour l'audit CS-347 post-provider. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | runtime-contract-drift | backend-domain | E-006, E-007, E-015 | The post-provider shape validation pipeline is traceable and test-backed. | Preserve `output_validator.py` as schema validation owner. | no |
| F-002 | Info | High | data-integrity-risk | backend-domain | E-008, E-009, E-010, E-016, E-018 | Rejected narrative answers are mapped to controlled client output and internal audit payloads. | Preserve rejection through `rejected_answer_workflow.py` and persistence through natal service. | no |
| F-003 | Info | High | observability-gap | backend-domain | E-011, E-012, E-013, E-019, E-020 | Call logs, token usage, operational metadata, and replay snapshots are source-backed. | Keep replay metadata redacted and audit-bound. | no |
| F-004 | Medium | High | data-integrity-risk | deferred non-domain | E-008, E-009, E-017 | Semantic grounding remains bounded to evidence refs plus policy checks; it is not a general semantic verifier. | Route architecture and reporting closure to CS-348 and CS-350; no CS-347 implementation change. | yes |
| F-005 | Info | High | missing-guard | backend-domain | E-003, E-021 | Existing RG-002/RG-022 apply indirectly; no exact registry guard exists for post-provider output audit cartography. | Record as registry gap only; story forbids guardrail edits. | no |

## F-001 - Output Shape Validation Is Traceable

- Severity: Info
- Confidence: High
- Category: runtime-contract-drift
- Domain: backend-domain
- Evidence: E-006, E-007, E-015
- Expected rule: raw provider output must pass a separate post-provider validation pipeline.
- Actual state: `LLMGateway._validate_and_normalize` delegates to `validate_output`, which parses JSON, validates the schema, normalizes fields, sanitizes evidence, and records validation counters.
- Impact: The post-provider shape validation pipeline is traceable and test-backed.
- Recommended action: Preserve `output_validator.py` as schema validation owner.
- Story candidate: no
- Suggested archetype: audit-observation

## F-002 - Rejection And Narrative Audit Persistence Are Separated

- Severity: Info
- Confidence: High
- Category: data-integrity-risk
- Domain: backend-domain
- Evidence: E-008, E-009, E-010, E-016, E-018
- Expected rule: non-grounded narrative output must not leak raw LLM content to clients.
- Actual state: `RejectedNarrativeAnswerOutcome` exposes a controlled client message, while `_apply_narrative_answer_audit` persists prompt, input, projection, evidence, provider, model, and rejection context fields.
- Impact: Rejected narrative answers are mapped to controlled client output and internal audit payloads.
- Recommended action: Preserve rejection through `rejected_answer_workflow.py` and persistence through natal service.
- Story candidate: no
- Suggested archetype: audit-observation

## F-003 - Observability And Replay Metadata Are Mapped

- Severity: Info
- Confidence: High
- Category: observability-gap
- Domain: backend-domain
- Evidence: E-011, E-012, E-013, E-019, E-020
- Expected rule: call logs, usage, gateway metadata, and replay readiness must be inspectable without exposing raw payloads.
- Actual state: `log_call` writes `llm_call_logs`, operational metadata, usage, validation status, evidence warning count, and creates a redacted encrypted replay snapshot.
- Impact: Call logs, token usage, operational metadata, and replay snapshots are source-backed.
- Recommended action: Keep replay metadata redacted and audit-bound.
- Story candidate: no
- Suggested archetype: audit-observation

## F-004 - Semantic Grounding Is Bounded, Not Fully Proven

- Severity: Medium
- Confidence: High
- Category: data-integrity-risk
- Domain: deferred non-domain
- Evidence: E-008, E-009, E-017
- Expected rule: the audit must distinguish schema validation from semantic grounding.
- Actual state: evidence refs and policy checks can reject missing, unsupported, or ungrounded sections, but the repository evidence does not prove a complete semantic verifier for every generated claim.
- Impact: Semantic grounding remains bounded to evidence refs plus policy checks; it is not a general semantic verifier.
- Recommended action: Route architecture and reporting closure to CS-348 and CS-350; no CS-347 implementation change.
- Story candidate: yes
- Suggested archetype: prompt-generation-architecture-closure

## F-005 - Exact Registry Guardrail Is Absent

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: backend-domain
- Evidence: E-003, E-021
- Expected rule: applicable guardrails must be mapped and registry edits must respect story authorization.
- Actual state: RG-002 and RG-022 apply indirectly, but no exact post-provider output validation persistence guardrail exists. CS-347 explicitly forbids registry enrichment.
- Impact: Existing RG-002/RG-022 apply indirectly; no exact registry guard exists for post-provider output audit cartography.
- Recommended action: Record as registry gap only; story forbids guardrail edits.
- Story candidate: no
- Suggested archetype: no-story
