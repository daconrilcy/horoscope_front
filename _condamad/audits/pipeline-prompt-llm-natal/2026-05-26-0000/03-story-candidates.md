# Story Candidates - Pipeline Prompt LLM Natal

## SC-001 - Converge natal LLM prompt input owner

- Source finding: F-001
- Suggested story title: Converger l'entree prompt LLM natale vers un owner canonique
- Suggested archetype: service-boundary-refactor
- Primary domain: backend natal LLM input
- Required contracts: Runtime Source of Truth; Ownership Routing; No Legacy; DRY; Reintroduction Guard
- Draft objective: choose the canonical factual/narrative owner for natal prompt input and route the audited pipeline through it without exposing raw runtime internals.
- Closure intent: full-closure
- Must include: exact owner decision among existing interpretation contracts or a documented user decision; before/after field matrix for `chart_json`, `natal_data`, `astro_context`, `evidence_catalog`; no duplicate active projection; no prompt rewrite unless explicitly authorized.
- Validation hints: targeted service tests for `NatalExecutionInput`, gateway message composition tests, negative scan for raw runtime classes in provider/prompt layers, positive scan for the chosen owner in natal input assembly.
- Blockers: needs-user-decision if the canonical owner is not already accepted as `AINarrativeInput` or another existing interpretation contract.

### Exhaustive Files To Modify

- Application files: exact selection rule: `backend/app/services/llm_generation/natal/interpretation_service.py`, selected existing owner under `backend/app/domain/astrology/interpretation/**`, and runtime contracts only if field shape changes.
- Governance/test files: `backend/tests/llm_orchestration/**` and targeted natal service tests.
- Before evidence required: current audit `02-input-field-matrix.md`, `rg` negative scan E-019.
- After evidence required: one canonical owner visible in the service path, no raw `ChartObjectRuntimeData` in prompt/provider code, all existing LLM orchestration tests green.
- Ownership routing decisions: astrology facts stay under domain astrology/interpretation; LLM request mapping stays under service/runtime.
- Mandatory no-wildcard allowlist and No Legacy checks: no broad allowlist; no `*_legacy` field; no fallback prompt path for supported natal features.
- Reintroduction guard requirements: exact scans for chosen owner and forbidden raw runtime classes.
- Stop condition: finding closes when the pipeline has one chosen owner or a documented user decision intentionally preserves public `chart_json`.
- Expected classification changes: selected canonical owner moves from not-used/out-of-domain context to used; no file becomes delete-candidate without separate evidence.

## SC-002 - Guard prompt-visible versus runtime-only fields

- Source finding: F-002
- Suggested story title: Garder la separation champs prompt-visible et runtime-only du pipeline natal
- Suggested archetype: runtime-contract-preservation
- Primary domain: backend LLM runtime contract
- Required contracts: Contract Shape; Reintroduction Guard; No Legacy
- Draft objective: add deterministic tests or guardrails proving only intended fields enter the user message and runtime-only fields remain non-visible unless placeholders explicitly allow them.
- Closure intent: full-closure
- Must include: explicit cases for `chart_json` with and without `{{chart_json}}`, and negative assertions for `natal_data`, `astro_context`, `plan`, `level`, `module`, `variant_code` in `build_user_payload`.
- Validation hints: focused gateway tests around `_build_messages` and `build_user_payload`; prompt renderer/assembly tests proving placeholder rendering does not make runtime-only fields visible by accident; scan audit matrix terms `prompt-visible`, `runtime-only`, `validation-only`.
- Blockers: none unless product decides `astro_context` or `evidence_catalog` must become prompt-visible.

### Exhaustive Files To Modify

- Application files: none expected unless behavior changes are explicitly authorized.
- Governance/test files: likely `backend/tests/llm_orchestration/test_llm_gateway_compose.py`, `backend/tests/llm_orchestration/test_prompt_renderer.py`, `backend/tests/llm_orchestration/test_assembly_resolution.py` or a new focused runtime test.
- Before evidence required: E-010 and E-011 source behavior.
- After evidence required: tests fail if runtime-only fields appear in user data block unexpectedly.
- Ownership routing decisions: gateway owns message visibility; contracts own transport fields.
- Mandatory no-wildcard allowlist and No Legacy checks: no broad placeholder allowlist and no silent fallback.
- Reintroduction guard requirements: exact assertions on message content and placeholder-rendering behavior.
- Stop condition: all audited fields have prompt-visible/runtime-only/validation-only tests or documented intentional gaps.
- Expected classification changes: tests become test-only; no application file classification changes expected.

## SC-003 - Decide evidence catalog generation role

- Source finding: F-003
- Suggested story title: Clarifier le role du catalogue d'evidence LLM natal
- Suggested archetype: api-contract-change
- Primary domain: backend LLM evidence validation
- Required contracts: Runtime Source of Truth; Ownership Routing; DRY; No Legacy
- Draft objective: decide and encode whether `evidence_catalog` is validation-only or a future prompt input, then align tests and documentation around that stage.
- Closure intent: blocked
- Must include: user/architecture decision; validation-stage tests; no prompt injection of evidence labels unless the decision explicitly authorizes it.
- Validation hints: `validate_output` tests with `evidence_catalog`, gateway message tests proving no unintended prompt injection, scans for `evidence_catalog` in prompt templates.
- Blockers: user decision required if evidence labels should constrain generation before output validation.

### Exhaustive Files To Modify

- Application files: none until decision; after decision exact selection likely `backend/app/domain/llm/runtime/output_validator.py`, `backend/app/domain/llm/runtime/gateway.py`, and `backend/app/services/llm_generation/natal/interpretation_service.py` only if role changes.
- Governance/test files: LLM orchestration output-validator and gateway tests.
- Before evidence required: E-017 validation path and E-010/E-011 message path.
- After evidence required: tests prove selected role.
- Ownership routing decisions: evidence validation cannot be owned by prompt prose.
- Mandatory no-wildcard allowlist and No Legacy checks: no fallback to public `chart_json` evidence without explicit compatibility test.
- Reintroduction guard requirements: scan for unexpected `evidence_catalog` prompt/template injection.
- Stop condition: role is documented and guarded, or blocked decision remains explicit.
- Expected classification changes: none until decision.

## SC-004 - Classify natal compatibility branches before refactor

- Source finding: F-004
- Suggested story title: Classer les compatibilites natales `/users`, `free_short`, fallback et schemas
- Suggested archetype: legacy-facade-removal
- Primary domain: backend natal compatibility surfaces
- Required contracts: No Legacy; Ownership Routing; Reintroduction Guard
- Draft objective: turn `/users`, `free_short`, schema v1/v2/v3 and prompt fallback compatibility into an explicit keep/remove decision register before changing runtime behavior.
- Closure intent: full-closure
- Must include: exact branch list, owner per branch, canonical replacement or keep rationale, tests/guards preventing unclassified compatibility growth.
- Validation hints: branch tests around `interpret_chart`, `_generate_free_short`, schema deserialization, assembly resolution and prompt fallback guard tests RG-018/RG-021.
- Blockers: needs-user-decision for any compatibility surface that is externally contracted.

### Exhaustive Files To Modify

- Application files: none for classification-only story; implementation story may later target `backend/app/services/llm_generation/natal/interpretation_service.py`.
- Governance/test files: compatibility register under `_condamad/stories/**` and targeted tests/guards, including assembly resolution and prompt fallback guard tests.
- Before evidence required: E-003, E-005, E-006, E-020.
- After evidence required: every compatibility branch has status `intentional`, `delete-candidate`, or `needs-user-decision`.
- Ownership routing decisions: API `/users` compatibility remains separate from LLM prompt input ownership.
- Mandatory no-wildcard allowlist and No Legacy checks: no broad compatibility allowlist.
- Reintroduction guard requirements: exact branch/key scans.
- Stop condition: all branches listed in `04-legacy-vs-canonical.md` have a decision.
- Expected classification changes: unresolved compatibility surfaces move from `needs-user-decision` to `used` or `delete-candidate` only with direct evidence.

## Deferred Non-Domain Candidates

- None emitted for frontend, DB, auth, CI, provider cost, prompt copy or output schemas.
