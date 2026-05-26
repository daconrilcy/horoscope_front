# Story Candidates - Configuration Prompts Placeholders Input Schema

## SC-001 Declare Canonical LLM Astrology Input Schema

- Source finding: F-001
- Suggested story title: Declarer le contrat `llm_astrology_input` pour les use cases natals
- Suggested archetype: architecture-transition-calculs-interpretations-injection-llm
- Primary domain: backend-domain/llm-configuration
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard, Persistent Evidence
- Draft objective: Define one canonical structured astrology input schema that can carry facts, signals, limits and proofs without relying on `chart_json`.
- Closure intent: blocked full-closure candidate pending the schema ownership decision
- Must include: exact owner decision for schema declaration; mapping for `natal_interpretation`, `natal_interpretation_short`, `natal_long_free`, and thematic natal modules; no prompt text rewrite unless explicitly scoped; no wildcard allowlist.
- Validation hints: rerun scans for `llm_astrology_input`, `required_prompt_placeholders`, `input_schema`, `chart_json`; add or update focused orchestration guards only in the implementation story.
- Blockers: user/architecture decision is required on whether the canonical payload is `AINarrativeInputContract`, a wrapper around it, or a smaller schema derived from it.

### Exhaustive Files To Modify

- Application files: `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, likely bootstrap owners under `backend/app/ops/llm/bootstrap/**`, and possibly `backend/app/domain/llm/runtime/contracts.py` depending on the selected contract.
- Governance/test files: focused orchestration tests under `backend/tests/llm_orchestration/**`.
- Audit files: none after this audit.
- Stop condition: every active natal use case has a declared modern input schema or an explicit user-approved exception; scans prove no new legacy carrier or wildcard placeholder allowlist.

## SC-002 Converge Runtime Validation Payload Ownership

- Source finding: F-002
- Suggested story title: Aligner la validation runtime sur le contrat d'entree astrologique canonique
- Suggested archetype: runtime-contract-preservation
- Primary domain: backend-domain/llm-runtime
- Required contracts: Runtime Source of Truth, Contract Shape, Reintroduction Guard
- Draft objective: Make gateway input validation consume the canonical structured astrology payload once SC-001 has selected and declared it.
- Closure intent: blocked
- Must include: before/after evidence for `_build_validation_payload`; explicit decision for `chart_json` compatibility; no silent fallback from `natal_data` to `chart_json` unless documented as temporary and guarded.
- Validation hints: targeted tests around `LLMGateway._build_validation_payload`, `validate_input`, and natal orchestration paths.
- Blockers: blocked by SC-001 target schema decision.

### Exhaustive Files To Modify

- Application files: `backend/app/domain/llm/runtime/gateway.py`, possibly `backend/app/domain/llm/runtime/contracts.py`.
- Governance/test files: `backend/tests/llm_orchestration/test_gateway_pipeline.py`, `test_resolved_execution_plan.py`, or a new focused test if no existing owner fits.
- Stop condition: validation payload has one canonical owner for modern astrology input; `chart_json` substitution is either removed or explicitly bounded by a guard.

## SC-003 Govern Structured Prompt Blocks

- Source finding: F-003
- Suggested story title: Gouverner les blocs prompt facts/signals/limits/proofs
- Suggested archetype: prompt-placeholder-contract-convergence
- Primary domain: backend-domain/llm-prompting
- Required contracts: Ownership Routing, Contract Shape, Reintroduction Guard
- Draft objective: Bind facts, signals, limits and proofs to declared schema fields or a single structured placeholder instead of ad hoc flat placeholders.
- Closure intent: blocked
- Must include: placeholder allowlist update with no wildcard; renderer tests for required structured input; assembly preview variables aligned with runtime payload; explicit no-prompt-copy-change unless scoped.
- Validation hints: `rg` scans for `facts|signals|limits|proofs`, renderer tests, placeholder governance tests.
- Blockers: blocked by SC-001 schema owner decision.

### Exhaustive Files To Modify

- Application files: `backend/app/domain/llm/prompting/prompt_renderer.py` only if rendering behavior changes; otherwise governance/registry owners and assembly preview variables under `backend/app/domain/llm/configuration/assembly_resolver.py`.
- Governance/test files: `backend/tests/llm_orchestration/test_prompt_renderer.py`, `test_placeholder_validation.py`, `test_prompt_governance_registry.py`.
- Stop condition: each structured block is either a field of the canonical input or explicitly absent by design; no separate follow-up is needed for placeholder ownership.

## Deferred Non-Domain Context

- Prompt copy edits are deferred.
- Provider changes are deferred.
- Frontend, DB, auth, migrations and release governance are deferred.
