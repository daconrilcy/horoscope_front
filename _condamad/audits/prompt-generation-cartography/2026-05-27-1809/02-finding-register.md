# Finding Register - prompt-generation-cartography - 2026-05-27-1809

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | CS-344 configuration cartography | E-001, E-002, E-005, E-006, E-007, E-011 | The audit maps owners and separates nominal runtime, bounded fallback and provisioning surfaces for later implementation stories. | Preserve this report as CS-344 baseline and do not use seeds as runtime truth. | no |
| F-002 | Medium | High | duplicate-responsibility | Output schema configuration ownership | E-005, E-010, E-011, E-012, E-017 | Output schema knowledge is split across canonical contracts, assembly UUIDs, fallback catalog schemas, bootstrap schemas and tests. | Produce a bounded convergence story that selects one nominal runtime schema owner and demotes fallback/seed schemas to explicit fallback or provisioning roles. | yes |
| F-003 | Low | High | missing-guard | Evaluation validation surface | E-014, E-018 | The strongest prompt-resolution evaluation test writes a report under `backend/tests`, so it is not a no-delta guard for read-only audits. | Add or split a non-mutating prompt-resolution guard, or make report generation opt-in. | yes |
| F-004 | Info | High | legacy-surface | Bootstrap and bounded fallback classification | E-009, E-010, E-013, E-015 | Bootstrap seeds and bounded fallback paths remain present but are now classified separately from nominal runtime configuration. | Keep fallback and seed rows explicit in CS-345 through CS-350; no application code change is recommended by this audit. | no |

## F-001 Configuration cartography baseline produced

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: CS-344 configuration cartography
- Evidence: E-001, E-002, E-005, E-006, E-007, E-011
- Expected rule: CS-344 must map use-case, assembly, renderer, placeholder, schema, profile and bootstrap owners without runtime edits.
- Actual state: The audit folder contains owner matrices, a resolution diagram, placeholder families, bounded fallback list, test map and file usage classification.
- Impact: The audit maps owners and separates nominal runtime, bounded fallback and provisioning surfaces for later implementation stories.
- Recommended action: Preserve this report as CS-344 baseline and do not use seeds as runtime truth.
- Story candidate: no
- Suggested archetype: no-story

## F-002 Output schema ownership remains split

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: Output schema configuration ownership
- Evidence: E-005, E-010, E-011, E-012, E-017
- Expected rule: Nominal runtime schema resolution should have one explicit owner and fallback/provisioning schemas should not compete with it.
- Actual state: `canonical_use_case_registry.py` declares `output_schema_name`, assemblies carry `output_schema_id`, `gateway.py` resolves snapshot/DB schemas then falls back to `catalog.py`, bootstrap seeds create schemas, and `test_output_contract.py` imports a bootstrap schema for natal premium.
- Impact: Output schema knowledge is split across canonical contracts, assembly UUIDs, fallback catalog schemas, bootstrap schemas and tests.
- Recommended action: Produce a bounded convergence story that selects one nominal runtime schema owner and demotes fallback/seed schemas to explicit fallback or provisioning roles.
- Story candidate: yes
- Suggested archetype: contract-shape-audit

## F-003 Prompt-resolution evaluation is not a no-delta guard

- Severity: Low
- Confidence: High
- Category: missing-guard
- Domain: Evaluation validation surface
- Evidence: E-014, E-018
- Expected rule: Read-only audit validation should be runnable without modifying backend source or test artifacts.
- Actual state: `test_prompt_resolution.py` writes `backend/tests/evaluation/evaluation_report.md` after execution.
- Impact: The strongest prompt-resolution evaluation test writes a report under `backend/tests`, so it is not a no-delta guard for read-only audits.
- Recommended action: Add or split a non-mutating prompt-resolution guard, or make report generation opt-in.
- Story candidate: yes
- Suggested archetype: test-guard-hardening

## F-004 Bootstrap and fallback paths classified

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: Bootstrap and bounded fallback classification
- Evidence: E-009, E-010, E-013, E-015
- Expected rule: Bounded fallback paths and seed/bootstrap files must be classified separately from nominal runtime.
- Actual state: This audit classifies bootstrap files as provisioning inputs and catalogs/gateway fallback paths as bounded fallback behavior.
- Impact: Bootstrap seeds and bounded fallback paths remain present but are now classified separately from nominal runtime configuration.
- Recommended action: Keep fallback and seed rows explicit in CS-345 through CS-350; no application code change is recommended by this audit.
- Story candidate: no
- Suggested archetype: no-story

