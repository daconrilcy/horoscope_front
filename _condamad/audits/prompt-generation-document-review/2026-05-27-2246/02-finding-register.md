<!-- Commentaire global: registre des findings CS-353 pour les processus paralleles LLM. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | runtime-contract-drift | prompt-generation-document-review | E-010, E-011, E-012, E-013 | Future agents can treat the modern natal flow as the only provider-capable process and miss guidance, chat and daily horoscope prompt generation. | Add a documentation correction that includes a parallel-process matrix and marks non-natal provider-capable flows explicitly. | yes |
| F-002 | Medium | High | legacy-surface | prompt-generation-document-review | E-014, E-015, E-018 | `event_guidance` keeps a `chart_json` prompt seed/contract surface that is not public-triggered in the audited routes but can be confused with nominal guidance. | Require a product/architecture decision to migrate, delete, or explicitly retain `event_guidance` as debt. | needs-user-decision |
| F-003 | Medium | Medium | needs-user-decision | prompt-generation-document-review | E-017, E-018 | Admin manual execution can hand sample payload context to the gateway, while natal sample payloads require `chart_json`; future docs can understate admin-only provider capability. | Decide whether CS-350 should document admin manual execution as admin-only provider-capable, and whether additional guard wording is needed. | needs-user-decision |
| F-004 | Low | High | missing-guard | prompt-generation-document-review | E-003, E-010 | Existing guardrails cover adjacent prompt-generation risks but not the exact requirement to keep parallel processes classified by provider capability. | Add a guardrail only when a documentation correction story creates a durable invariant. | yes |
| F-005 | Info | High | missing-test-coverage | prompt-generation-document-review | E-008, E-018 | Existing tests already protect modern natal carrier extinction; future docs should cite them instead of rediscovering the boundary. | Reference existing carrier guards in the next documentation amendment; no implementation story needed here. | no |

## Finding Details

### F-001 Non-Natal Provider-Capable Processes Missing From One Matrix

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: prompt-generation-document-review
- Evidence: E-010, E-011, E-012, E-013
- Expected rule: CS-353 requires every parallel prompt process to state trigger, owner, configuration source, prompt-visible input, renderer or assembly, provider handoff and modern natal boundary.
- Actual state: CS-350 mentions fallback/repair/seeds and the modern natal flow, but the audited source evidence confirms provider-capable guidance, chat and daily horoscope processes that are not represented in one explicit matrix.
- Impact: Future agents can treat the modern natal flow as the only provider-capable process and miss guidance, chat and daily horoscope prompt generation.
- Recommended action: Add a documentation correction that includes a parallel-process matrix and marks non-natal provider-capable flows explicitly.
- Story candidate: yes
- Suggested archetype: documentation-correction

### F-002 `event_guidance` Legacy Carrier Decision Is Missing

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: prompt-generation-document-review
- Evidence: E-014, E-015, E-018
- Expected rule: Legacy carriers and fallback/debt paths must be classified without promoting them to nominal runtime truth.
- Actual state: `seed_guidance_prompts.py` still provisions an `event_guidance` prompt with `chart_json`; the actual fallback catalog owner is `prompting/catalog.py`, and no public `event_guidance` trigger was found in the audited guidance routes.
- Impact: `event_guidance` keeps a `chart_json` prompt seed/contract surface that is not public-triggered in the audited routes but can be confused with nominal guidance.
- Recommended action: Require a product/architecture decision to migrate, delete, or explicitly retain `event_guidance` as debt.
- Story candidate: needs-user-decision
- Suggested archetype: legacy-surface-decision

### F-003 Admin Manual Execution Provider Capability Needs Product Classification

- Severity: Medium
- Confidence: Medium
- Category: needs-user-decision
- Domain: prompt-generation-document-review
- Evidence: E-017, E-018
- Expected rule: Admin, test, seed, archival and runtime-active processes must stay distinct, and provider capability must be proven from trigger plus handoff evidence.
- Actual state: `execute_admin_catalog_sample_payload` constructs an `LLMExecutionRequest` and calls `LLMGateway.execute_request`; natal sample payload validation requires `chart_json`. This is admin-only, not public nominal runtime, but it is provider-capable.
- Impact: Admin manual execution can hand sample payload context to the gateway, while natal sample payloads require `chart_json`; future docs can understate admin-only provider capability.
- Recommended action: Decide whether CS-350 should document admin manual execution as admin-only provider-capable, and whether additional guard wording is needed.
- Story candidate: needs-user-decision
- Suggested archetype: admin-policy-classification

### F-004 Exact Parallel-Process Guardrail Is Absent

- Severity: Low
- Confidence: High
- Category: missing-guard
- Domain: prompt-generation-document-review
- Evidence: E-003, E-010
- Expected rule: Durable prompt-generation invariants should be encoded in regression guardrails when they become stable.
- Actual state: RG-017 to RG-022 cover adjacent direct-provider, fallback, narration assembly and validation-path risks; no exact guardrail requires guidance/chat/horoscope/fallback/repair/admin/seed/carrier paths to stay provider-capability-classified.
- Impact: Existing guardrails cover adjacent prompt-generation risks but not the exact requirement to keep parallel processes classified by provider capability.
- Recommended action: Add a guardrail only when a documentation correction story creates a durable invariant.
- Story candidate: yes
- Suggested archetype: governance-guardrail-hardening

### F-005 Existing Modern Natal Carrier Guards Are Active

- Severity: Info
- Confidence: High
- Category: missing-test-coverage
- Domain: prompt-generation-document-review
- Evidence: E-008, E-018
- Expected rule: Existing guards should be reused rather than duplicated.
- Actual state: Tests and audits already prove `chart_json` and `natal_data` are excluded from modern natal prompt material when `llm_astrology_input_v1` is present.
- Impact: Existing tests already protect modern natal carrier extinction; future docs should cite them instead of rediscovering the boundary.
- Recommended action: Reference existing carrier guards in the next documentation amendment; no implementation story needed here.
- Story candidate: no
- Suggested archetype: none
