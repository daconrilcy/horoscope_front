<!-- Commentaire global: registre des constats issus de l'audit CS-345 du handoff runtime provider LLM. -->

# Finding Register - prompt-generation-cartography - 2026-05-27-1822

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | runtime-contract-drift | CS-345 runtime handoff cartography | E-001, E-005, E-007, E-008, E-009, E-010, E-011 | The final provider payload is now identified from runtime source rather than inferred from prompt configuration. | Preserve this audit as the runtime handoff source for CS-348 to CS-350. | no |
| F-002 | Info | High | boundary-violation | Prompt-visible versus audit-only payload boundary | E-006, E-012, E-013, E-015 | Current runtime keeps audit-only and validation-only `llm_astrology_input_v1` fields outside provider prompt material. | Keep existing payload boundary tests in future prompt-generation validation plans. | no |
| F-003 | Info | High | legacy-surface | Repair, fallback and non-nominal runtime paths | E-004, E-016 | Repair, use-case fallback, test fallback and provider fallback paths are classified as non nominal and are not treated as the normal handoff. | Route any behavioral change to CS-347 or a later implementation story; do not change runtime in this audit. | no |
| F-004 | Info | High | missing-guard | Runtime provider handoff guardrail registry coverage | E-004, E-011, E-017 | The repository has targeted tests and AST evidence for this handoff, but no exact durable registry guardrail for runtime provider handoff cartography. | Record the registry gap in CS-345 evidence only; registry enrichment is not authorized by this story. | no |

## F-001 Runtime handoff payload identified

- Severity: Info
- Confidence: High
- Category: runtime-contract-drift
- Domain: CS-345 runtime handoff cartography
- Evidence: E-001, E-005, E-007, E-008, E-009, E-010, E-011
- Expected rule: The audit must identify the last provider payload from executed gateway source, not from prompt configuration.
- Actual state: `_build_messages` returns the `messages` list, `_call_provider` passes that list to `ProviderRuntimeManager.execute_with_resilience`, and the manager forwards it to `ResponsesClient.execute`.
- Impact: The final provider payload is now identified from runtime source rather than inferred from prompt configuration.
- Recommended action: Preserve this audit as the runtime handoff source for CS-348 to CS-350.
- Story candidate: no
- Suggested archetype: no-story

## F-002 Prompt boundary is currently enforced

- Severity: Info
- Confidence: High
- Category: boundary-violation
- Domain: Prompt-visible versus audit-only payload boundary
- Evidence: E-006, E-012, E-013, E-015
- Expected rule: Audit-only and validation-only fields must not be prompt material.
- Actual state: Gateway projection uses canonical prompt-visible roles and recursively excludes provenance, evidence refs, validation-only and audit-only keys before serialization.
- Impact: Current runtime keeps audit-only and validation-only `llm_astrology_input_v1` fields outside provider prompt material.
- Recommended action: Keep existing payload boundary tests in future prompt-generation validation plans.
- Story candidate: no
- Suggested archetype: no-story

## F-003 Recovery paths classified as non nominal

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: Repair, fallback and non-nominal runtime paths
- Evidence: E-004, E-016
- Expected rule: Recovery and fallback behavior must not be documented as nominal provider handoff.
- Actual state: Repair and fallback happen after output validation failure, set repair/fallback metadata, and are separated from the normal `execute_request` handoff path.
- Impact: Repair, use-case fallback, test fallback and provider fallback paths are classified as non nominal and are not treated as the normal handoff.
- Recommended action: Route any behavioral change to CS-347 or a later implementation story; do not change runtime in this audit.
- Story candidate: no
- Suggested archetype: no-story

## F-004 Exact runtime handoff guardrail is absent from registry

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: Runtime provider handoff guardrail registry coverage
- Evidence: E-004, E-011, E-017
- Expected rule: Existing guardrails must be consulted, and new registry edits must only occur when authorized.
- Actual state: RG-002 and RG-022 apply indirectly, but no exact runtime-provider-handoff guardrail exists and CS-345 explicitly forbids registry enrichment.
- Impact: The repository has targeted tests and AST evidence for this handoff, but no exact durable registry guardrail for runtime provider handoff cartography.
- Recommended action: Record the registry gap in CS-345 evidence only; registry enrichment is not authorized by this story.
- Story candidate: no
- Suggested archetype: no-story

