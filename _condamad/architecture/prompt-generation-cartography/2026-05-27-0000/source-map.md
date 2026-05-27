<!-- Commentaire global: cartographie des sources d'audit utilisees pour la synthese CS-348. -->

# Source Map - CS-348 Prompt Generation LLM Architecture

## Audit availability

Observed: the five mandatory audit deliverables are available under `_condamad/audits/prompt-generation-cartography/**`.

| Story | Audit | Path | Companion bundle | Used as |
| --- | --- | --- | --- | --- |
| CS-343 | Surface Inventory Audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | `00-audit-report.md`, `01-evidence-log.md`, `02-finding-register.md`, `03-story-candidates.md`, `04-risk-matrix.md`, `05-executive-summary.md` | Surface baseline and boundary taxonomy |
| CS-344 | Configuration Assembly Placeholder Audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` | `00-audit-report.md`, `01-evidence-log.md`, `02-finding-register.md`, `03-story-candidates.md`, `04-risk-matrix.md`, `05-executive-summary.md` | Configuration registry, placeholder and schema ownership decisions |
| CS-345 | Runtime Gateway Handoff Audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | `00-audit-report.md`, `01-evidence-log.md`, `02-finding-register.md`, `03-story-candidates.md`, `04-risk-matrix.md`, `05-executive-summary.md` | Provider handoff and message boundary decisions |
| CS-346 | Natal Astrology Input Audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | `00-audit-report.md`, `01-evidence-log.md`, `02-finding-register.md`, `03-story-candidates.md`, `04-risk-matrix.md`, `05-executive-summary.md` | `llm_astrology_input_v1` object, block, hash and evidence decisions |
| CS-347 | Output Validation Persistence Audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` | `00-audit-report.md`, `01-evidence-log.md`, `02-finding-register.md`, `03-story-candidates.md`, `04-risk-matrix.md`, `05-executive-summary.md` | Post-provider validation, persistence, observability, replay and semantic limits |

## Evidence and findings used

| Source | Evidence IDs used | Finding IDs used | Story candidate IDs used | Material claims |
| --- | --- | --- | --- | --- |
| CS-343 | E-003, E-004, E-005, E-006, E-007, E-010, E-011, E-012 | F-001, F-002, F-003 | none | Observed: runtime, configuration, seed, test, audit, historical and debt surfaces are classified; `llm_astrology_input_v1` is centered for modern natal; legacy text hits must not become active prompt ownership. |
| CS-344 | E-005, E-006, E-007, E-010, E-011, E-012, E-013, E-014, E-017, E-018 | F-001, F-002, F-003, F-004 | SC-001, SC-002 | Observed: nominal runtime is canonical use case -> assembly -> renderer -> gateway schema resolution; blocker: output schema ownership is split; seed/bootstrap are provisioning, not runtime truth. |
| CS-345 | E-004, E-005, E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-015, E-016, E-017 | F-001, F-002, F-003, F-004 | none | Observed: the last gateway-owned provider payload is `messages`; audit-only and validation-only fields are excluded; repair and fallback are non-nominal. |
| CS-346 | E-004, E-005, E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-014 | F-001, F-002, F-003, F-004 | none | Observed: prompt-visible blocks are `facts`, `signals`, `limits`, `shaping`; `evidence` and `provenance` are not prompt-visible; hash policy is source-backed. |
| CS-347 | E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-015, E-016, E-017, E-018, E-019, E-020, E-021 | F-001, F-002, F-003, F-004, F-005 | SC-001 | Observed: output validation, rejection, persistence, observability and replay are mapped; blocker: semantic grounding is bounded, not a full semantic verifier. |

## Assumptions and limitations

| Type | Statement | Source |
| --- | --- | --- |
| assumption | The output folder is fixed to `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/` because the story target state names that exact folder. | CS-348 story |
| blocker | If product expects complete semantic truth verification for every generated claim, implementation must stop for owner decision; audits only prove bounded evidence refs and policy checks. | CS-347 F-004, SC-001 |
| blocker | If product treats catalog fallback schemas as supported public behavior, the schema ownership convergence story needs product decision before implementation. | CS-344 SC-001 |
| inferred | The output schema owner split is treated as a contradiction/owner decision because current evidence names several competing schema sources without one nominal authority. | CS-344 F-002 |
| open question | Whether missing exact guardrail registry entries should become a separate governance story. | CS-345 F-004, CS-347 F-005 |

## Boundary vocabulary

Decision: CS-348 uses the shared boundary vocabulary `prompt-visible`, `runtime-only`, `validation-only`, and `audit-only`.

| Boundary | Source definition |
| --- | --- |
| prompt-visible | rendered developer prompts, filtered `llm_astrology_input_v1` blocks, selected context summaries; CS-343, CS-345, CS-346 |
| runtime-only | route triggers, use-case selection, provider/profile metadata, DB carriers, request IDs; CS-343, CS-345, CS-346 |
| validation-only | input/output validation, evidence refs, grounding status, tests; CS-343, CS-345, CS-347 |
| audit-only | hashes, prompt refs, persisted answer audit, observability, replay/admin metadata, CONDAMAD archives; CS-343, CS-347 |
