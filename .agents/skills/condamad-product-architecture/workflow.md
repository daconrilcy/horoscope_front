# Product Architecture Synthesis Workflow

## 1. Establish the synthesis boundary

- Identify the audit set and the intended capstone scope.
- Name the product domain and bounded contexts.
- Record excluded domains and why they are out of scope.
- Preserve source audit IDs in all findings and decisions.

## 2. Build the audit source map

For each source audit, extract:

- Audit ID and title.
- Scope.
- Closure status and any closure caveats.
- Key findings.
- Affected capabilities.
- Affected surfaces.
- Current-state evidence.
- Recommended actions.
- Blockers or unresolved decisions.
- Story candidate labels and remapping caveats.
- Deferred non-domain context.

Classify each finding as:

- `architecture-input`: should shape the capstone architecture.
- `implementation-detail`: relevant to roadmap but not an architecture decision.
- `duplicate`: covered by another finding.
- `contradiction`: conflicts with another source.
- `stale-or-unproven`: lacks current evidence.

When audits provide evidence IDs, preserve those IDs in the source map and downstream decisions. Do not collapse `E-*`, `F-*`, `SC-*`, `RG-*`, or story labels into prose-only citations.

## 3. Create the capability matrix

Use the domain language from the audits. For a domain with families, modules, workflows, graph types, document types, calculation modes, plans, or feature classes, use those as rows.

Columns:

- `capability_or_family`
- `required_inputs`
- `required_domain_objects`
- `required_canonical_contracts`
- `required_surfaces`
- `current_status`
- `blockers`
- `source_audits`

Use status values:

- `implemented`
- `partial`
- `implicit`
- `missing`
- `conflicting`
- `blocked`
- `unknown`

## 4. Create the surface matrix

Default surfaces:

- `internal`
- `public_api`
- `admin_debug`
- `automation_or_llm`
- `frontend`
- `data_storage`
- `observability`

Adapt names only when the source product has clearer surface terms.

Columns:

- `surface`
- `current_contract`
- `expected_contract`
- `exposed_capabilities`
- `consumers`
- `risks`
- `blockers`
- `required_changes`
- `source_audits`

## 5. Decide canonical registries

Create registries for concepts that need stable names, versioned contracts, replay, or cross-surface consistency.

Typical registries:

- Capability registry.
- Contract/schema registry.
- Graph/model registry.
- Domain object/entity registry.
- Event/job registry.
- Policy/entitlement registry.
- Prompt/interpretation registry.

For each registry entry, decide:

- Canonical ID.
- Version suffix.
- Owner.
- Inputs.
- Output contract.
- Compatibility rule.
- Deprecation rule.
- Trace fields.

## 6. Decide domain objects and entities

Normalize repeated audit vocabulary into a canonical object/entity taxonomy.

For each object:

- Canonical name.
- Kind: `core_entity`, `value_object`, `derived_object`, `external_reference`, `presentation_model`, `debug_artifact`.
- Lifecycle owner.
- Persistence rule.
- Serialization rule.
- Versioning rule.
- Required surfaces.
- Forbidden shortcuts or legacy aliases.

## 7. Define operational rules

Cover:

- Versioning.
- Traceability.
- Cache keys.
- Replay.
- Invalidation.
- Migration.
- Observability.
- Backward compatibility.

Each rule must state:

- What is versioned or traced.
- Who owns it.
- Which inputs participate.
- Which changes invalidate outputs.
- Which audit finding requires the rule.

## 8. Produce ordered stories

Derive stories from architecture dependencies:

1. Source-of-truth registries and contracts.
2. Domain object normalization.
3. Internal implementation boundaries.
4. Public/API/admin/debug surfaces.
5. Automation, interpretation, or LLM surfaces.
6. Frontend and user-facing workflows.
7. Observability, replay, cache, invalidation hardening.
8. Migration and cleanup.

Each story must include:

- Story ID suggestion.
- Source label if the audit already proposed one.
- Title.
- Goal.
- Source audit findings.
- Scope.
- Out of scope.
- Acceptance criteria.
- Validation evidence.
- Dependencies.
- Blockers or required decisions.

If source audits contain story labels that conflict with an existing tracker, keep the source label as provenance and assign the implementation story to `next-available-id` or `needs-tracker-remap`.

## 9. Final consistency pass

Before final output:

- Ensure every blocker maps to at least one roadmap story or explicit owner decision.
- Ensure every canonical registry decision has a versioning rule.
- Ensure every surface has an owner and expected contract.
- Ensure every major story has source audit evidence.
- Ensure unresolved contradictions are not hidden.
- Ensure deferred non-domain context is not accidentally converted into implementation scope.
- Ensure source-label caveats are preserved and no existing story ID is overwritten by implication.
