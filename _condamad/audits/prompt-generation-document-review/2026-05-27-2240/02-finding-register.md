<!-- Commentaire global: registre des constats pour l'audit CS-352 de concordance code-document prompt LLM. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | runtime-contract-drift | condamad-audit-documentation | E-005, E-009, E-010, E-012 | The document can be read as separating `evidence_refs` into only validation-only or only audit-only roles, while code proves a validation-owned evidence block that is excluded from prompt material and later persisted as audit evidence. | Update only the source document to state that `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may feed audit persistence. | yes |
| F-002 | Low | High | runtime-contract-drift | condamad-audit-documentation | E-005, E-008, E-011 | The phrase `backend-only runtime` for `request_id` and `trace_id` is imprecise because source passes request, trace and use-case identifiers to the provider adapter as headers; they remain not prompt-visible. | Update only the source document to use `runtime/provider-only metadata, not prompt-visible payload` for `request_id`, `trace_id` and `use_case`. | yes |
| F-003 | Info | High | missing-test-coverage | condamad-audit-documentation | E-003, E-005, E-010, E-012 | Existing tests cover prompt-visible exclusions and legacy carriers, but no exact durable guardrail targets code-document concordance of `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`. | Keep the guardrail gap visible; route any future durable guardrail to a dedicated documentation-governance story instead of changing runtime code here. | no |

## F-001 validation-owned evidence fields need one documented dual-role sentence

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: condamad-audit-documentation
- Evidence: E-005, E-009, E-010, E-012
- Expected rule: The cartography document must distinguish prompt-visible, validation-owned and audit-only fields without implying that persisted audit anchors become provider prompt material.
- Actual state: The document lists `evidence` and `evidence_refs` under validation-only and later describes `evidence_refs` with audit persistence. Source shows `LLM_ASTROLOGY_INPUT_DATA_ROLES["validation_only"]`, `_evidence_block`, `_evidence_refs_for_audit`, `_apply_narrative_answer_audit` and tests proving these fields are excluded from prompt-visible material.
- Impact: The document can be read as separating `evidence_refs` into only validation-only or only audit-only roles, while code proves a validation-owned evidence block that is excluded from prompt material and later persisted as audit evidence.
- Recommended action: Update only the source document to state that `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may feed audit persistence.
- Story candidate: yes
- Suggested archetype: documentation-correction

## F-002 request and trace identifiers are provider metadata, not prompt-visible payload

- Severity: Low
- Confidence: High
- Category: runtime-contract-drift
- Domain: condamad-audit-documentation
- Evidence: E-005, E-008, E-011
- Expected rule: Backend-only wording must not imply that provider-bound metadata stays strictly inside backend process memory when source passes it to the provider adapter; the key boundary is that it is not prompt-visible payload.
- Actual state: The document states `backend-only runtime: request_id, trace_id`, while `LLMGateway._call_provider` passes `request_id`, `trace_id` and `use_case` to `ProviderRuntimeManager.execute_with_resilience`; `ResponsesClient.execute` maps them to `x-request-id`, `x-trace-id` and `x-use-case` headers.
- Impact: The phrase `backend-only runtime` for `request_id` and `trace_id` is imprecise because source passes request, trace and use-case identifiers to the provider adapter as headers; they remain not prompt-visible.
- Recommended action: Update only the source document to use `runtime/provider-only metadata, not prompt-visible payload` for `request_id`, `trace_id` and `use_case`.
- Story candidate: yes
- Suggested archetype: documentation-correction

## F-003 exact code-document concordance guardrail is absent

- Severity: Info
- Confidence: High
- Category: missing-test-coverage
- Domain: condamad-audit-documentation
- Evidence: E-003, E-005, E-010, E-012
- Expected rule: Guardrail coverage should distinguish executable prompt-boundary guards from documentation concordance guards.
- Actual state: RG-002 and RG-022 are applicable adjacent guardrails. Boundary tests cover prompt-visible exclusions and legacy carrier extinction, but no exact guardrail verifies that the `_condamad/docs` cartography remains code-concordant.
- Impact: Existing tests cover prompt-visible exclusions and legacy carriers, but no exact durable guardrail targets code-document concordance of `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Recommended action: Keep the guardrail gap visible; route any future durable guardrail to a dedicated documentation-governance story instead of changing runtime code here.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit
