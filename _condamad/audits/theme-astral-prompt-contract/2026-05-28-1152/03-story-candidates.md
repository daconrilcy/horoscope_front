# Story Candidates

## SC-001 CS-363 target contract architecture

- Source finding: F-001
- Suggested story title: CS-363 Define Theme Astral LLM Input V1 Architecture
- Suggested archetype: contract-shape-audit / architecture-contract
- Primary domain: theme-astral-prompt-contract
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard
- Draft objective: Define the backend-only `theme_astral_llm_input_v1` target with explicit `interpretation_material`, source ownership, allowed provider-visible blocks and excluded runtime/audit fields.
- Closure intent: full-closure for F-001 contract ambiguity, prerequisite for F-002 and F-003.
- Must include: exact source families from CS-361, current builders, provider examples, no `chart_json`/`natal_data` prompt-visible promotion, no wildcard allowlist, No Legacy checks.
- Validation hints: scan report for `birth_context`, `astrological_facts`, `interpretation_material`, `selected_themes`, `limits`, `output_contract`, and verify CS-361 sources are cited.
- Blockers: stop if CS-361 or CS-362 audit artifacts are missing or contradict the target scope.

## SC-002 CS-364 versioned persistence contract

- Source finding: F-003
- Suggested story title: CS-364 Define Versioned Theme Astral Prompt Contract Persistence
- Suggested archetype: data-contract-persistence
- Primary domain: theme-astral-prompt-contract
- Required contracts: Persistence Versioning, Ownership Routing, No Legacy, Runtime Source of Truth
- Draft objective: Decide where prompt contract versions, material-source references and output contract metadata live without editing seed/reference rows opportunistically.
- Closure intent: full-closure for F-003 persistence/ownership ambiguity.
- Must include: exact table/model owners, migration decision points, before/after evidence for DB schema if implemented later, no duplicated source registry.
- Validation hints: targeted scans for `llm_assembly_configs`, `llm_prompt_versions`, `llm_output_schemas`, `llm_personas`, source owner IDs and version fields.
- Blockers: stop if persistence owner is a product decision rather than repository-evidenced.

## SC-003 CS-365 interpretation material builder

- Source finding: F-001
- Suggested story title: CS-365 Implement Interpretation Material Builder For Theme Astral
- Suggested archetype: service-boundary-refactor
- Primary domain: backend/app/domain/astrology/interpretation
- Required contracts: Runtime Source of Truth, Ownership Routing, No Legacy, DRY, Reintroduction Guard
- Draft objective: Build one canonical material builder that selects table-derived sign, planet, house, aspect, dignity, dominance, rulership and condition material for the target contract.
- Closure intent: full-closure for rich-source material construction after CS-363/CS-364.
- Must include: exact selection rule for DB/reference/static catalog sources, source-to-output evidence, no fallback material, no prompt text hidden in services.
- Validation hints: unit tests proving selected material comes from declared source owners and negative scans for duplicate builders or inline prompt prose.
- Blockers: stop if CS-363 has not defined `interpretation_material` shape.

## SC-004 CS-366 stable provider payload builder

- Source finding: F-002
- Suggested story title: CS-366 Implement Stable Theme Astral Provider Payload Builder
- Suggested archetype: provider-payload-builder-convergence
- Primary domain: backend/app/domain/llm/runtime and natal LLM generation
- Required contracts: Contract Shape, Runtime Source of Truth, No Legacy, Reintroduction Guard
- Draft objective: Compose provider payloads from the new backend-only contract without leaking audit/runtime fields and without reintroducing old prompt carriers.
- Closure intent: full-closure for F-002 after CS-365 supplies material.
- Must include: free/basic/premium payload rules, filtered prompt-visible blocks, no wildcard allowlist, tests for excluded `chart_json`, `natal_data`, hashes and provider metadata.
- Validation hints: provider payload examples for free/basic/premium, tests around `_prompt_visible_llm_astrology_input`, scans for `chart_json.*prompt-visible`.
- Blockers: stop if material builder or target contract is absent.

## SC-005 CS-367 bigbang legacy removal

- Source finding: F-002
- Suggested story title: CS-367 Bigbang Theme Astral Prompt Contract
- Suggested archetype: legacy-surface-removal
- Primary domain: theme-astral-prompt-contract runtime integration
- Required contracts: No Legacy, DRY, Runtime Source of Truth, Reintroduction Guard
- Draft objective: Replace old provider prompt contract surfaces with the stable theme astral contract in one nominal path.
- Closure intent: full-closure for residual legacy carrier risk after CS-366.
- Must include: exact old carrier scans, no compatibility prompt carrier, no fallback prompt carrier, before/after provider examples, no hidden residual work.
- Validation hints: scans for `chart_json`, `natal_data`, fallback prompt carriers, provider examples and gateway tests.
- Blockers: stop if CS-366 has not produced stable provider builder evidence.

## SC-006 CS-368 closure audit

- Source finding: F-004
- Suggested story title: CS-368 Audit Cloture Bascule Theme Astral Prompt Contract
- Suggested archetype: closure-audit-guard-hardening
- Primary domain: theme-astral-prompt-contract
- Required contracts: Baseline Snapshot, Persistent Evidence, Reintroduction Guard, No Legacy
- Draft objective: Audit the completed migration and prove each text source classification changed only as expected.
- Closure intent: full-closure for F-004.
- Must include: complete source list from CS-361, before/after source reachability matrix, tests/guards proving provider reach, deleted/legacy surface scans, file/surface classification changes.
- Validation hints: rerun CS-361 source scans, inspect new artifacts, execute targeted unit/architecture tests, compare free/basic/premium provider payloads.
- Blockers: stop if CS-363 through CS-367 are incomplete.

## Exhaustive Files To Modify

For F-001: none in CS-361. Candidate implementation files are selected by CS-363 and CS-365 after architecture approval.

For F-002: none in CS-361. Candidate implementation files are selected by CS-366 and CS-367 after target contract approval.

For F-003: none in CS-361. Candidate implementation files are selected by CS-364 after persistence ownership decision.

For F-004: none in CS-361. Candidate implementation files are selected by CS-368 after migration completion.

## Deferred Non-Domain Context

Frontend, auth, real provider calls, DB migration execution and UI behavior are deferred non-domain concerns for this audit and must not keep CS-361 open.
