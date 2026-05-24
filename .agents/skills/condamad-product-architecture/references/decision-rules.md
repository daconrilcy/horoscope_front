# Decision Rules

## Canonical registry rules

Create a canonical registry when at least one condition is true:

- Multiple audits refer to the same concept with different names.
- A concept crosses internal, API, admin/debug, automation, frontend, or storage surfaces.
- A concept requires versioned compatibility.
- A concept participates in cache keys, replay, traceability, or invalidation.
- A concept is consumed by generated output, interpretation, automation, or external clients.

Do not create a registry when:

- The concept is local implementation detail with no cross-surface contract.
- The concept is temporary migration scaffolding.
- The source audits do not provide enough evidence to define stable entries.

## Versioning rules

Use explicit version suffixes for contracts that may need compatibility windows, for example `<name>_v1`.

Version when changes affect:

- Required inputs.
- Output shape.
- Semantics of a field.
- Ordering or determinism.
- Cache key identity.
- Replay compatibility.
- Public or persisted contracts.

Do not version for:

- Internal refactors that preserve behavior.
- Documentation-only changes.
- Non-contractual debug wording.

## Object/entity rules

Classify objects by lifecycle, not by display name.

- Use `core_entity` for durable business identity.
- Use `value_object` for immutable structured values without independent identity.
- Use `derived_object` for reproducible outputs from canonical inputs.
- Use `external_reference` for third-party IDs or imported source objects.
- Use `presentation_model` for UI-only projections.
- Use `debug_artifact` for trace, inspection, or admin-only data.

Any object exposed to public API, storage, replay, or automation must have serialization and versioning rules.

## Surface rules

Every surface needs:

- Owner.
- Contract.
- Consumer list.
- Compatibility expectation.
- Validation evidence.

Public and persisted surfaces need stronger backward compatibility than internal surfaces.

Admin/debug surfaces may expose richer trace data, but must not become the only source of truth.

Automation or LLM surfaces must identify which inputs are canonical and which outputs are interpretive, generated, or non-authoritative.

## Blocker rules

Mark a blocker when implementation cannot proceed without:

- Product decision.
- Architecture owner decision.
- Security/privacy decision.
- Data ownership decision.
- Missing source-of-truth.
- Contradictory audit findings.
- Unknown compatibility requirement.

Do not mark ordinary implementation effort as a blocker.
