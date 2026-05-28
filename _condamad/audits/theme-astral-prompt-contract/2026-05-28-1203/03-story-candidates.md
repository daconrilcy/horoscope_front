# Story Candidates

## SC-001 CS-363 commercial plan replacement

- Source finding: F-001
- Suggested story title: CS-363 Define Theme Astral LLM Input V1 Architecture
- Suggested archetype: contract-shape-audit / architecture-contract
- Primary domain: theme-astral-prompt-contract
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard, No Legacy
- Draft objective: Replace prompt-visible commercial `plan` labels with backend-owned delivery and feature profile fields in the target contract.
- Closure intent: full-closure.
- Must include: `delivery_profile`, `feature_context`, no prompt-visible commercial `plan`, explicit distinction between backend commercial entitlement and LLM delivery requirements.
- Validation hints: targeted scans for `plan commercial`, `delivery_profile`, `feature_context`, `astrologer_voice`, `output_contract`, `free`, `basic`, `premium`, `backend-only`.
- Blockers: stop if product wants commercial plan labels prompt-visible; that requires explicit decision.

## SC-002 CS-366 single provider data carrier

- Source finding: F-002
- Suggested story title: CS-366 Implement Stable Theme Astral Provider Payload Builder
- Suggested archetype: provider-payload-builder-convergence
- Primary domain: backend/app/domain/llm/runtime and natal LLM generation
- Required contracts: Contract Shape, Runtime Source of Truth, No Legacy, Reintroduction Guard
- Draft objective: Build provider payloads with one canonical prompt-visible data carrier and no duplicate full chart material in both developer and user messages.
- Closure intent: full-closure.
- Must include: before/after `free/basic/premium` provider payload examples, no duplicate full data in developer/user, and targeted scans proving the chosen carrier owns chart facts.
- Validation hints: parse regenerated payloads, compare key shapes, scan prompt-visible user message for forbidden commercial/runtime/audit fields, scan basic developer prompt for premium-only labels.
- Blockers: stop if CS-363 architecture report is absent.

## SC-003 CS-363 stable shape and variability map

- Source finding: F-003
- Suggested story title: CS-363 Define Theme Astral LLM Input V1 Architecture
- Suggested archetype: contract-shape-audit
- Primary domain: theme-astral-prompt-contract
- Required contracts: Runtime Source of Truth, Contract Shape, Persistent Evidence
- Draft objective: Preserve plan-variable quantities while formalizing which keys and message roles must be stable.
- Closure intent: full-closure.
- Must include: stable key-shape table, role/message policy, allowed plan-specific cardinality differences, stop condition proving no hidden shape drift remains.
- Validation hints: parse `free/basic/premium` examples and compare top-level keys, message roles, nested keys and array counts.
- Blockers: stop if any payload cannot be parsed mechanically.

## SC-004 CS-366 backend-only metadata split

- Source finding: F-004
- Suggested story title: CS-366 Implement Stable Theme Astral Provider Payload Builder
- Suggested archetype: provider-payload-builder-convergence / boundary-hardening
- Primary domain: backend/app/domain/llm/runtime and natal LLM generation
- Required contracts: Runtime Source of Truth, Ownership Routing, Reintroduction Guard, No Legacy
- Draft objective: Remove exclusion registry and calculation metadata from provider payload shape while preserving LLM-needed birth context.
- Closure intent: full-closure.
- Must include: before/after split of `source_metadata`, no `audit_excluded_from_prompt` in final provider payload, no hashes/provenance/provider response/chart_json/natal_data prompt-visible.
- Validation hints: targeted scans for `projection_hash`, `llm_input_hash`, `provider_response`, `provenance`, `observability`, `replay_snapshot`, `chart_json`, `natal_data`, `debug`, `trace`.
- Blockers: stop if CS-363 does not decide which birth context fields are LLM-needed.

## SC-005 CS-366 basic-not-premium prompt guard

- Source finding: F-005
- Suggested story title: CS-366 Implement Stable Theme Astral Provider Payload Builder
- Suggested archetype: prompt-contract-guard-hardening
- Primary domain: backend/app/domain/llm/runtime and prompt assembly
- Required contracts: Contract Shape, Reintroduction Guard, No Legacy
- Draft objective: Ensure the basic provider prompt cannot contain premium-only wording or density obligations.
- Closure intent: full-closure.
- Must include: targeted test or scan over rendered `basic` provider payload proving absence of premium-only labels, while premium payload still carries high-depth delivery requirements through non-commercial vocabulary.
- Validation hints: parse basic payload and scan developer messages for premium-only strings; scan premium payload for allowed delivery-depth terms.
- Blockers: stop if prompt configuration owner is unresolved.

## Exhaustive Files To Modify

For F-001: none in CS-362. Candidate files are selected by CS-363/CS-366 after architecture approval.

For F-002: none in CS-362. Candidate files are selected by CS-363/CS-366; exact affected surface must include provider payload construction and tests.

For F-003: none in CS-362. Candidate artifact is the CS-363 architecture report and any validation evidence it owns.

For F-004: none in CS-362. Candidate files are selected by CS-363/CS-366; exact affected surface must include backend-only filtering and example payload checks.

For F-005: none in CS-362. Candidate files are selected by CS-363/CS-366; exact affected surface must include prompt assembly/seed/config owner and a targeted guard.

## Deferred Non-Domain Context

Frontend, auth, DB migrations, real provider calls, prompt seed rewrites, and UI behavior are deferred non-domain concerns for this audit and must not keep CS-362 open.
