<!-- Commentaire global: registre des constats de l'audit adversarial CS-351 du document de cartographie prompt LLM. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | runtime-contract-drift | condamad-audit-documentation | E-004, E-006, E-007, E-008, E-011 | The document can make a future agent treat `evidence_refs` as only validation-only in one section and backend/audit-only in another, while sources show a validation-owned block that is also persisted as audit evidence. | Clarify in the source document that `evidence` and `evidence_refs` are excluded from provider prompt material, owned by validation, and may be persisted as audit-only anchors. | yes |
| F-002 | Low | High | runtime-contract-drift | condamad-audit-documentation | E-004, E-009, E-010 | The phrase `backend-only runtime` for `request_id` and `trace_id` is imprecise because those values are not prompt-visible but are passed through the provider adapter as headers. | Replace or nuance `backend-only runtime` with `runtime/provider-only metadata, not prompt-visible payload` for request, trace and use-case identifiers. | yes |
| F-003 | Low | High | missing-guard | condamad-audit-documentation | E-003, E-004, E-006, E-007 | The document cites an exact provider/post-provider guardrail registry gap but the closest durable guardrail is adjacent RG-042 for LLM docs source-of-truth under `backend/docs`, not an exact `_condamad/docs` or provider-handoff invariant. | Keep the gap visible in the document and route any future guardrail creation to a dedicated documentation or handoff guardrail story. | no |

## F-001 validation-audit evidence role needs stronger wording

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: condamad-audit-documentation
- Evidence: E-004, E-006, E-007, E-008, E-011
- Expected rule: A critical cartography document must keep prompt-visible, validation-only and audit-only roles distinct without implying that a persisted audit anchor is prompt material.
- Actual state: The document states `validation-only: evidence, grounding_status, validation_owner, evidence_refs` in the boundary list, then later states that `evidence_refs` and `grounding_status` are backend-only and audit-only persistence fields. CS-346 and CS-347 source artifacts show the intended nuance: validation-owned evidence data is excluded from provider prompt material and may be persisted as audit evidence.
- Impact: The document can make a future agent treat `evidence_refs` as only validation-only in one section and backend/audit-only in another, while sources show a validation-owned block that is also persisted as audit evidence.
- Recommended action: Clarify in the source document that `evidence` and `evidence_refs` are excluded from provider prompt material, owned by validation, and may be persisted as audit-only anchors.
- Story candidate: yes
- Suggested archetype: documentation-correction

## F-002 request and trace identifiers are not prompt-visible but are provider metadata

- Severity: Low
- Confidence: High
- Category: runtime-contract-drift
- Domain: condamad-audit-documentation
- Evidence: E-004, E-009, E-010
- Expected rule: Runtime-only wording must not imply that provider-bound metadata remains strictly inside the backend when code sends it as provider request metadata.
- Actual state: The document classifies `request_id` and `trace_id` as `backend-only runtime`, while `LLMGateway._call_provider` passes them to `ProviderRuntimeManager.execute_with_resilience`, and `ResponsesClient.execute` maps them to `x-request-id` and `x-trace-id` headers. The document later calls them runtime/provider-only parameters, which is more precise.
- Impact: The phrase `backend-only runtime` for `request_id` and `trace_id` is imprecise because those values are not prompt-visible but are passed through the provider adapter as headers.
- Recommended action: Replace or nuance `backend-only runtime` with `runtime/provider-only metadata, not prompt-visible payload` for request, trace and use-case identifiers.
- Story candidate: yes
- Suggested archetype: documentation-correction

## F-003 exact guardrail remains a documented gap

- Severity: Low
- Confidence: High
- Category: missing-guard
- Domain: condamad-audit-documentation
- Evidence: E-003, E-004, E-006, E-007
- Expected rule: A source-of-truth document should not imply that an adjacent guardrail fully protects a distinct documentation or provider-handoff boundary.
- Actual state: RG-042 exists for LLM source-of-truth docs under `backend/docs`. The CS-351 story and the reviewed document correctly mention an exact guardrail registry gap for provider/post-provider handoff, but no exact `_condamad/docs` guardrail was found during this audit.
- Impact: The document cites an exact provider/post-provider guardrail registry gap but the closest durable guardrail is adjacent RG-042 for LLM docs source-of-truth under `backend/docs`, not an exact `_condamad/docs` or provider-handoff invariant.
- Recommended action: Keep the gap visible in the document and route any future guardrail creation to a dedicated documentation or handoff guardrail story.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit
