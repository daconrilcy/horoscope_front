<!-- Commentaire global: rapport d'audit adversarial CS-351 du document final de cartographie de generation des prompts LLM. -->

# CS-351 Domain Audit Report

## Domain Closure Status

Status: `open`.

Reason: the audited documentation is broadly source-aligned, but F-001 and F-002 require a documentation-only correction candidate. No application implementation file remains in scope.

## Audited Domain

- Domain key: `prompt-generation-document-review`
- Domain type: `condamad-audit-documentation`
- Audit archetype: custom documentation review, with `contract-shape-audit`, `legacy-surface-audit` and `test-guard-coverage-audit` dimensions applied where relevant.
- Primary reviewed artifact: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- Explicit deliverable: `_condamad/audits/prompt-generation-document-review/2026-05-27-2305/01-adversarial-document-review-audit.md`
- Read-only implementation mode: yes for `backend/app/**`, `backend/tests/**`, `frontend/src/**`, migrations and source document edits.

## Prior Audit And Story History Consulted

| Source | Path | Classification | Current status | Evidence |
|---|---|---|---|---|
| CS-343 surface inventory | `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | prior audit | still-active as source map baseline | E-005 |
| CS-344 configuration audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` | prior audit | still-active for output schema split and fallback classification | E-005, E-007 |
| CS-345 provider handoff audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | prior audit | still-active for no-real-provider-call limitation | E-005, E-007 |
| CS-346 natal input audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | prior audit | still-active for prompt-visible block ownership | E-005, E-008 |
| CS-347 output validation audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` | prior audit | still-active for validation, audit persistence and semantic limit | E-005, E-007 |
| CS-348 architecture | `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` | architecture | still-active source of blockers and boundary vocabulary | E-006 |
| CS-349 report | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md` | report | still-active source of evidence gaps | E-006 |
| Guardrails registry | `_condamad/stories/regression-guardrails.md` | governance | RG-042 adjacent, exact documentation-review guardrail gap remains | E-003 |

## Closure Analysis

- Active findings after current evidence: F-001 and F-002 require a future documentation correction only.
- Closed findings: none closed by this audit because it is read-only and does not edit the reviewed source document.
- Superseded findings: none.
- Non-domain residuals: runtime provider behavior, provider privacy policy, persistence schema and semantic verifier implementation.
- Complete in-domain implementation surface for active findings: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` only.
- Governance/test surface for active findings: none.
- Application surface for active findings: none.

## Mandatory Audit Dimensions

| Dimension | Verdict | Evidence | Notes |
|---|---|---|---|
| DRY | PASS | E-004, E-005, E-006 | No second cartography document was created; this audit references existing CS-343 to CS-349 sources. |
| No Legacy | PASS with watchpoint | E-004, E-005, E-007 | Fallback, legacy, seed and bootstrap terms remain classified as non-nominal or non-runtime in the reviewed document. |
| Mono-domain ownership | PASS | E-001, E-002, E-004 | The audit stays in `_condamad/audits` and does not modify runtime code or `_condamad/docs`. |
| Dependency direction | PASS | E-009, E-010, E-011 | Code was read only to verify documentation claims; no dependency changes were made. |
| Contract shape | PASS with findings | E-004, E-006, E-007, E-008 | Required sections and boundary labels exist, but two wording corrections are recommended. |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/00-story.md` | used | E-001 | Scope and acceptance contract for this audit. | none |
| `_story_briefs/cs-351-audit-revue-adversariale-document-cartographie-prompt-llm.md` | used | E-002 | Source brief for objective and non-goals. | file was untracked in baseline status |
| `_condamad/stories/regression-guardrails.md` / RG-042 | used | E-003 | Adjacent guardrail and registry gap evidence. | RG-042 is adjacent, not exact for `_condamad/docs`. |
| `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | used | E-004 | Document under adversarial review. | file was already modified before this audit |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | used | E-005 | CS-343 source map and surface classifications. | none |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` | used | E-005, E-007 | CS-344 configuration, fallback and output schema owner split evidence. | none |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | used | E-005, E-007 | CS-345 provider handoff and no-real-provider-call limitation. | no provider call executed |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | used | E-005, E-008 | CS-346 prompt-visible versus validation/audit-only block evidence. | none |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` | used | E-005, E-007 | CS-347 validation, audit persistence and semantic grounding limit evidence. | none |
| `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` | used | E-006 | CS-348 boundary vocabulary, blockers and decision records. | none |
| `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md` | used | E-006 | CS-349 report conclusions and evidence gaps. | none |
| `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/evidence-sources.md` | used | E-006 | Source matrix for CS-343 to CS-349 claims. | none |
| `backend/app/domain/llm/runtime/gateway.py` / `LLMGateway` | used | E-009 | Source-backed verification of message composition, exclusions, provider metadata and fallback handling. | read-only inspection only |
| `backend/app/domain/llm/runtime/provider_runtime_manager.py` / `execute_with_resilience` | used | E-010 | Source-backed verification of provider manager handoff. | read-only inspection only |
| `backend/app/infra/providers/llm/openai_responses_client.py` / `ResponsesClient.execute` | used | E-010 | Source-backed verification of request, trace and use-case header mapping. | read-only inspection only |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` / `LLMAstrologyInputV1Builder` | used | E-011 | Source-backed verification of prompt-visible blocks, evidence and provenance. | read-only inspection only |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / audit helpers | used | E-011 | Source-backed verification of persistence audit anchors. | read-only inspection only |

## Findings Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 1 |
| Low | 2 |
| Info | 0 |

## Active Implementation Findings

No application implementation finding remains. Active findings are documentation-only:

- F-001: clarify validation-owned fields that may feed audit persistence.
- F-002: clarify runtime/provider-only metadata wording for request and trace identifiers.

## Deferred Non-Domain Concerns

- Provider privacy policy and external provider behavior are outside this audit.
- Runtime code changes, migrations, API/frontend changes and test implementation are outside this audit.
- Canonical output schema owner selection remains the CS-344/CS-348 blocker and is not resolved here.
- Full semantic verifier implementation remains outside this audit.

## Final Decision

Decision: `acceptable with corrections`.

The document preserves the main runtime truth: nominal natal flow, prompt-visible blocks, fallback/legacy/seed non-nominal status, output schema owner split and bounded semantic grounding. Corrections are required to avoid misleading future agents on validation/audit role overlap and provider metadata boundaries.
