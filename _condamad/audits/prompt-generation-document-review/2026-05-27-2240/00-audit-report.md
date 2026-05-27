<!-- Commentaire global: rapport compagnon CONDAMAD pour l'audit CS-352 de concordance code-document de la generation des prompts LLM. -->

# CS-352 Domain Audit Report

## Domain Closure Status

Status: `open`.

Reason: the audited runtime code and tests confirm the nominal prompt-generation flow, but two documentation-only concordance corrections remain. No backend, frontend, migration or test implementation file is in scope.

## Audited Domain

- Domain key: `prompt-generation-document-review`
- Domain type: `condamad-audit-documentation`
- Audit archetype: custom code-document concordance audit, with `contract-shape-audit`, `legacy-surface-audit`, `test-guard-coverage-audit`, DRY and No Legacy dimensions.
- Explicit story deliverable: `_condamad/audits/prompt-generation-document-review/2026-05-27-2240/02-code-document-concordance-audit.md`
- Primary reviewed artifact: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- Runtime source surface: backend LLM configuration, renderer, gateway, natal LLM input builder, natal orchestration service, provider adapter and listed boundary tests.
- Read-only implementation mode: yes for `backend/app/**`, `backend/tests/**`, `frontend/src/**`, migrations and `_condamad/docs/**`.

## Prior Audit And Story History Consulted

| Source | Path | Classification | Current status | Evidence |
|---|---|---|---|---|
| CS-351 adversarial review | `_condamad/audits/prompt-generation-document-review/2026-05-27-2305/00-audit-report.md` | prior same-domain audit | still-active; F-001/F-002 align with current code evidence | E-004 |
| CS-343 surface inventory | `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | prior source-map audit | still-active source inventory | E-006 |
| CS-344 configuration audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` | prior configuration audit | still-active for assembly, placeholders and output-schema split | E-006, E-007 |
| CS-345 gateway handoff audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | prior runtime audit | still-active for provider handoff and no-real-provider-call limitation | E-006, E-008, E-011 |
| CS-346 natal input audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | prior boundary audit | still-active for prompt-visible blocks and backend-only exclusions | E-006, E-009, E-010 |
| CS-347 validation persistence audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` | prior validation/persistence audit | still-active for audit persistence and semantic grounding limits | E-006, E-009 |
| Guardrails registry | `_condamad/stories/regression-guardrails.md` | governance | RG-022 applies; exact CS-352 code-document guardrail gap remains | E-003 |

## Closure Analysis

- Prior same-domain active findings consulted: CS-351 F-001 and F-002 are still active under current code evidence; F-003 remains an adjacent guardrail gap and does not block this domain.
- Findings closed by current evidence: none; this audit is read-only and intentionally does not edit the source document.
- Active findings after current evidence: F-001 and F-002, both documentation-only.
- Complete in-domain implementation surface for active findings: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` only.
- Application files to modify for active findings: none.
- Governance/test files to modify for active findings: none.
- Review correction: CS-352 persistent evidence artifacts were missing at review start and were reconstructed under `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/` with an explicit baseline limitation (E-014, E-015).
- Deferred non-domain context: output schema ownership decision, provider privacy policy, real provider-call validation and CI policy for long guards.

## Mandatory Audit Dimensions

| Dimension | Verdict | Evidence | Notes |
|---|---|---|---|
| DRY | PASS | E-001, E-005, E-006 | The audit creates a concordance report only; it does not create a second canonical cartography document. |
| No Legacy | PASS with watchpoints | E-005, E-008, E-010, E-012 | Legacy carriers `chart_json`, `natal_data` and `evidence_catalog` remain separated from the modern natal prompt path by source and tests. |
| Mono-domain ownership | PASS | E-001, E-002, E-005 | Audit artifacts stay under `_condamad/audits`; source docs and runtime code are read-only. |
| Dependency direction | PASS | E-007, E-008, E-009, E-011 | Code was read and scanned only; no dependency edge was added or changed. |
| Contract shape | PASS with findings | E-005, E-007, E-008, E-009, E-010 | Required matrices and gap categories are present in `02-code-document-concordance-audit.md`. |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/00-story.md` | used | E-001 | Defines CS-352 scope, acceptance criteria and explicit output path. | none |
| `_story_briefs/cs-352-audit-concordance-code-document-generation-prompt-llm.md` | used | E-002 | Source brief for code-document concordance objective and mandatory sources. | none |
| `_condamad/stories/regression-guardrails.md` / RG-002, RG-022 | used | E-003 | Existing invariants consulted before findings and candidates. | exact CS-352 guardrail remains absent |
| `_condamad/audits/prompt-generation-document-review/2026-05-27-2305/00-audit-report.md` | used | E-004 | Latest same-domain audit used for closure ledger. | CS-351 is adversarial-document, not code-document |
| `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | used | E-005 | Document under concordance audit. | current workspace state only |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` / `CanonicalUseCaseContract` | used | E-007 | Canonical use-case contract and `llm_astrology_input_v1` schema owner evidence. | read-only inspection |
| `backend/app/domain/llm/configuration/assembly_resolver.py` / `resolve_assembly`, `assemble_developer_prompt` | used | E-007 | Assembly and developer-prompt source evidence. | read-only inspection |
| `backend/app/domain/llm/prompting/prompt_renderer.py` / `PromptRenderer.render`, `extract_placeholders` | used | E-007 | Placeholder rendering owner evidence. | read-only inspection |
| `backend/app/domain/llm/runtime/gateway.py` / `LLMGateway`, `_resolve_plan`, `_build_messages`, `_call_provider`, `execute_request` | used | E-008, E-010 | Gateway flow, prompt-visible filtering, validation, repair and provider handoff evidence. | no real provider call |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` / `LLMAstrologyInputV1Builder` | used | E-009, E-010 | Prompt-visible block roles and audit/validation field ownership evidence. | read-only inspection |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / `_build_llm_astrology_input_v1`, `_apply_narrative_answer_audit` | used | E-009, E-011 | Natal orchestration and persistence audit anchor evidence. | read-only inspection |
| `backend/app/domain/llm/runtime/provider_runtime_manager.py` / `execute_with_resilience` | used | E-011 | Provider manager handoff evidence. | read-only inspection |
| `backend/app/infra/providers/llm/openai_responses_client.py` / `ResponsesClient.execute` | used | E-011 | Provider metadata header evidence. | no external provider call |
| `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | test-only | E-010, E-012 | Architecture guard for prompt-visible exclusions. | none |
| `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | test-only | E-010, E-012 | Handoff guard for rich input versus legacy carriers. | none |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` | test-only | E-010, E-012 | Unit guard for LLM input contract and data roles. | none |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` | test-only | E-010, E-012 | Unit guard for prompt-visible hash material. | none |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` | test-only | E-010, E-012 | Unit guard for evidence refs. | none |
| `backend/tests/integration/test_llm_legacy_extinction.py` | test-only | E-010, E-012 | Integration guard for legacy carrier extinction. | 7 long tests deselected by default pytest selection |
| `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/concordance-baseline.txt` | test-only | E-014, E-015 | Review-time baseline reconstruction for missing CS-352 persistent evidence. | not a contemporaneous pre-implementation baseline |
| `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/concordance-after.txt` | test-only | E-014, E-015 | After-review evidence confirming required persistent artifacts and report markers. | none |
| `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/validation.txt` | test-only | E-015 | Persisted validation output for audit validate/lint and targeted CS-352 checks. | none |

## Findings Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 1 |
| Low | 1 |
| Info | 1 |

## Active Implementation Findings

No application implementation finding remains. Active findings are documentation-only:

- F-001: clarify validation-owned evidence fields that may also feed audit persistence.
- F-002: clarify provider-bound metadata wording for `request_id`, `trace_id` and `use_case`.

## Deferred Non-Domain Concerns

- Selecting one final output-schema owner remains outside this audit and belongs to the existing CS-344/CS-348 blocker.
- Real external provider behavior was not tested; this audit validates source handoff only.
- Long legacy extinction variants remain CI-policy context and do not change the current code-document concordance result.

## Final Decision

Decision: `acceptable with documentation-only corrections`.

The final cartography document is source-aligned on the nominal modern natal flow and correctly separates prompt-visible blocks from legacy carriers. It needs two wording corrections so future agents do not confuse validation-owned audit anchors with prompt material, or runtime/provider metadata with strictly backend-only data.
