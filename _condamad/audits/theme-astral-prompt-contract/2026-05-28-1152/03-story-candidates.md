# Story Candidates

## SC-001 CS-363 target contract architecture

- Source finding: F-001
- Suggested story title: CS-363 Define Theme Astral LLM Input V1 Architecture
- Suggested archetype: contract-shape-audit / architecture-contract
- Primary domain: theme-astral-prompt-contract
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard
- Draft objective: Define the backend-only `theme_astral_llm_input_v1` target with explicit `interpretation_material`, source ownership, allowed provider-visible blocks and excluded runtime/audit fields.
- Closure intent: full-closure for F-001 contract ambiguity, prerequisite for F-002 and F-003.
- Exact files or selection rule: documentation and architecture artifacts only unless the CS-363 story explicitly authorizes implementation; must cite `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/00-audit-report.md`, `01-audit-usage-tables-textes-interpretation.md`, `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`, and the existing `llm_astrology_input_v1`/gateway owners.
- Before evidence required: CS-361 source matrix, provider comparison for `free`, `basic`, `premium`, and scans proving current `facts/signals/limits/shaping` handoff.
- After evidence required: target contract artifact defining `interpretation_material`, excluded fields, ownership routing, and plan-specific provider visibility without changing runtime behavior.
- Ownership routing decisions expected: choose the canonical architecture owner for `theme_astral_llm_input_v1`; keep source classification in audit/architecture artifacts; keep runtime implementation for CS-365/CS-366.
- Mandatory no-wildcard allowlist and No Legacy checks: explicitly forbid `chart_json`, `natal_data`, `provider_response`, hash/provenance fields, wildcard prompt-visible carriers, fallback prompt carriers and compatibility prompt carriers.
- Reintroduction guard requirements: targeted scans must prove the target contract does not endorse legacy prompt carriers or audit-only provenance in prompt-visible payloads.
- Must include: exact source families from CS-361, current builders, provider examples, no `chart_json`/`natal_data` prompt-visible promotion, no wildcard allowlist, No Legacy checks.
- Validation hints: scan report for `birth_context`, `astrological_facts`, `interpretation_material`, `selected_themes`, `limits`, `output_contract`, and verify CS-361 sources are cited.
- Blockers: stop if CS-361 or CS-362 audit artifacts are missing or contradict the target scope.
- Expected file/surface classification changes: none in CS-361; after CS-363, the new architecture artifact should be `used`, while runtime files remain classified by evidence only.

## SC-002 CS-364 versioned persistence contract

- Source finding: F-003
- Suggested story title: CS-364 Define Versioned Theme Astral Prompt Contract Persistence
- Suggested archetype: data-contract-persistence
- Primary domain: theme-astral-prompt-contract
- Required contracts: Persistence Versioning, Ownership Routing, No Legacy, Runtime Source of Truth
- Draft objective: Decide where prompt contract versions, material-source references and output contract metadata live without editing seed/reference rows opportunistically.
- Closure intent: full-closure for F-003 persistence/ownership ambiguity.
- Exact files or selection rule: persistence decision artifacts first; any later schema/model files must be selected only by the CS-364 story after deciding whether existing owners such as `llm_prompt_versions`, `llm_output_schemas`, `llm_assembly_configs`, or a new explicit contract owner apply.
- Before evidence required: CS-361 inventory of DB models, repositories, seeds and admin/reference sources, plus scans for existing prompt version/config/schema tables.
- After evidence required: one versioned owner decision with rejected alternatives, migration impact statement, and source-owner references for `interpretation_material`.
- Ownership routing decisions expected: do not store prompt contract metadata inside seed JSON or reference prose files; route persistence to an explicit contract/config owner.
- Mandatory no-wildcard allowlist and No Legacy checks: prove no broad serialized source dump, no legacy prompt carrier persistence, and no duplicate source registry.
- Reintroduction guard requirements: tests or scans must distinguish source metadata from prompt-visible prose material.
- Must include: exact table/model owners, migration decision points, before/after evidence for DB schema if implemented later, no duplicated source registry.
- Validation hints: targeted scans for `llm_assembly_configs`, `llm_prompt_versions`, `llm_output_schemas`, `llm_personas`, source owner IDs and version fields.
- Blockers: stop if persistence owner is a product decision rather than repository-evidenced.
- Expected file/surface classification changes: CS-361 seed/admin/reference sources remain `used`, `seed-only`, `admin-only`, or `unused` by reachability; no source may move to prompt-visible `used` without before/after reachability evidence.

## SC-003 CS-365 interpretation material builder

- Source finding: F-001
- Suggested story title: CS-365 Implement Interpretation Material Builder For Theme Astral
- Suggested archetype: service-boundary-refactor
- Primary domain: backend/app/domain/astrology/interpretation
- Required contracts: Runtime Source of Truth, Ownership Routing, No Legacy, DRY, Reintroduction Guard
- Draft objective: Build one canonical material builder that selects table-derived sign, planet, house, aspect, dignity, dominance, rulership and condition material for the target contract.
- Closure intent: full-closure for rich-source material construction after CS-363/CS-364.
- Exact files or selection rule: one canonical domain builder plus tests; include every CS-361 source family that CS-363 marks in scope, and exclude reference-only docs unless CS-363 explicitly promotes them through a repository-backed owner.
- Before evidence required: CS-361 matrix rows for signs, planets, houses, aspects, dominance, dignity/rulership, advanced conditions and docs/reference prose.
- After evidence required: unit tests showing selected material is sourced from declared owners, negative tests for absent/fallback material, and a source-to-output matrix proving each family is selected, intentionally excluded, or blocked by a named decision.
- Ownership routing decisions expected: material selection belongs to the domain interpretation layer; repositories provide data; services and prompts must not embed prose selection logic.
- Mandatory no-wildcard allowlist and No Legacy checks: no fallback prose, no inline prompt prose in orchestration services, no compatibility adapter that silently fills missing material.
- Reintroduction guard requirements: targeted scans for duplicate material builders, inline interpretation prose in prompt services, and unsupported source-family promotion.
- Must include: exact selection rule for DB/reference/static catalog sources, source-to-output evidence, no fallback material, no prompt text hidden in services.
- Validation hints: unit tests proving selected material comes from declared source owners and negative scans for duplicate builders or inline prompt prose.
- Blockers: stop if CS-363 has not defined `interpretation_material` shape.
- Expected file/surface classification changes: source families selected by the builder may move from `seed-only` or `unknown` to `used` only with repository/runtime evidence; excluded families must keep an explicit `unused`, `admin-only`, `seed-only`, or `needs-user-decision` classification.

## SC-004 CS-366 stable provider payload builder

- Source finding: F-002
- Suggested story title: CS-366 Implement Stable Theme Astral Provider Payload Builder
- Suggested archetype: provider-payload-builder-convergence
- Primary domain: backend/app/domain/llm/runtime and natal LLM generation
- Required contracts: Contract Shape, Runtime Source of Truth, No Legacy, Reintroduction Guard
- Draft objective: Compose provider payloads from the new backend-only contract without leaking audit/runtime fields and without reintroducing old prompt carriers.
- Closure intent: full-closure for F-002 after CS-365 supplies material.
- Exact files or selection rule: gateway/payload-builder files selected by CS-366 plus tests and regenerated provider examples; do not edit source material owners except through the canonical builder contract.
- Before evidence required: CS-361 provider comparison, `LLMGateway.build_user_payload` filtering evidence, and exclusion scan for audit/runtime fields.
- After evidence required: `free`, `basic`, `premium` provider payload examples proving expected `interpretation_material` visibility by plan and tests proving excluded fields remain absent.
- Ownership routing decisions expected: provider payload composition belongs to the provider payload builder/gateway boundary; material selection remains owned by CS-365 builder.
- Mandatory no-wildcard allowlist and No Legacy checks: no wildcard prompt-visible serialization, no legacy `chart_json`/`natal_data` carrier, no provider metadata or provenance in prompt-visible user content.
- Reintroduction guard requirements: tests around prompt-visible filtering and scans for old carrier names in provider payload construction.
- Must include: free/basic/premium payload rules, filtered prompt-visible blocks, no wildcard allowlist, tests for excluded `chart_json`, `natal_data`, hashes and provider metadata.
- Validation hints: provider payload examples for free/basic/premium, tests around `_prompt_visible_llm_astrology_input`, scans for `chart_json.*prompt-visible`.
- Blockers: stop if material builder or target contract is absent.
- Expected file/surface classification changes: provider examples become `used` evidence of final handoff; old provider carrier surfaces can become `delete-candidate` only after negative scans prove they are not registered entrypoints, tests, or public contracts.

## SC-005 CS-367 bigbang legacy removal

- Source finding: F-002
- Suggested story title: CS-367 Bigbang Theme Astral Prompt Contract
- Suggested archetype: legacy-surface-removal
- Primary domain: theme-astral-prompt-contract runtime integration
- Required contracts: No Legacy, DRY, Runtime Source of Truth, Reintroduction Guard
- Draft objective: Replace old provider prompt contract surfaces with the stable theme astral contract in one nominal path.
- Closure intent: full-closure for residual legacy carrier risk after CS-366.
- Exact files or selection rule: all old prompt carrier surfaces identified by CS-366 scans, plus tests and examples that still reference old carriers; stop if the scan returns a public/exported surface without an owner decision.
- Before evidence required: old carrier scan for `chart_json`, `natal_data`, fallback prompt carriers, compatibility prompt carriers and provider payload examples.
- After evidence required: negative scans for removed carriers, passing boundary tests, regenerated examples, and a deletion/classification register for each removed or retained surface.
- Ownership routing decisions expected: migrate nominal runtime path to the stable contract; classify any retained legacy reference as `test-only`, `intentional-public-export`, `needs-user-decision`, or `delete-candidate` with evidence.
- Mandatory no-wildcard allowlist and No Legacy checks: no compatibility branch, no fallback prompt carrier, no alias that preserves old semantics under a new name.
- Reintroduction guard requirements: guard tests must fail on reintroduced old carrier names in prompt-visible payloads.
- Must include: exact old carrier scans, no compatibility prompt carrier, no fallback prompt carrier, before/after provider examples, no hidden residual work.
- Validation hints: scans for `chart_json`, `natal_data`, fallback prompt carriers, provider examples and gateway tests.
- Blockers: stop if CS-366 has not produced stable provider builder evidence.
- Expected file/surface classification changes: removed legacy surfaces become closed `delete-candidate` or deleted with before/after negative usage evidence; retained references require explicit classification and rationale.

## SC-006 CS-368 closure audit

- Source finding: F-004
- Suggested story title: CS-368 Audit Cloture Bascule Theme Astral Prompt Contract
- Suggested archetype: closure-audit-guard-hardening
- Primary domain: theme-astral-prompt-contract
- Required contracts: Baseline Snapshot, Persistent Evidence, Reintroduction Guard, No Legacy
- Draft objective: Audit the completed migration and prove each text source classification changed only as expected.
- Closure intent: full-closure for F-004.
- Exact files or selection rule: new timestamped audit folder under `_condamad/audits/theme-astral-prompt-contract/` plus story evidence; inspect every CS-361 source family and every runtime/provider surface changed by CS-363 through CS-367.
- Before evidence required: CS-361 audit folder, CS-363 through CS-367 implementation evidence, pre-closure source reachability matrix and provider examples.
- After evidence required: closure matrix for source existence, projection reach, LLM input reach and provider reach; validation outputs; negative legacy scans; file/surface classification deltas.
- Ownership routing decisions expected: classify residual issues as in-domain, non-domain, blocked, or closed; do not leave hidden implementation work outside findings/candidates.
- Mandatory no-wildcard allowlist and No Legacy checks: rerun no-wildcard, no legacy carrier, no fallback and no audit-field prompt-visible scans.
- Reintroduction guard requirements: permanent guards must distinguish source existence from provider visibility and fail on unclassified prompt-visible material.
- Must include: complete source list from CS-361, before/after source reachability matrix, tests/guards proving provider reach, deleted/legacy surface scans, file/surface classification changes.
- Validation hints: rerun CS-361 source scans, inspect new artifacts, execute targeted unit/architecture tests, compare free/basic/premium provider payloads.
- Blockers: stop if CS-363 through CS-367 are incomplete.
- Expected file/surface classification changes: every CS-361 surface must retain or change classification with direct evidence; any `unknown` must become closed, blocked, or `needs-user-decision`.

## Exhaustive Files To Modify

For F-001: none in CS-361. Candidate implementation files are selected by CS-363 and CS-365 after architecture approval.

For F-002: none in CS-361. Candidate implementation files are selected by CS-366 and CS-367 after target contract approval.

For F-003: none in CS-361. Candidate implementation files are selected by CS-364 after persistence ownership decision.

For F-004: none in CS-361. Candidate implementation files are selected by CS-368 after migration completion.

## Deferred Non-Domain Context

Frontend, auth, real provider calls, DB migration execution and UI behavior are deferred non-domain concerns for this audit and must not keep CS-361 open.
