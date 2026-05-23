# Story CS-### <story-key>: <title>

Status: ready-to-dev

<!-- Keep contract headings and markers in English. Story content may be written in French. -->

## 1. Objective

One clear paragraph explaining the implementation outcome.

## 2. Trigger / Source

- Source type: brief | audit | code-review | architecture-decision | bug | refactor
- Source reference: <path, pasted brief, issue, review, or audit>
- Reason for change: <why this story exists>

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: <backend/app/services/... or equivalent>
- In scope:
  - ...
- Out of scope:
  - ...
- Explicit non-goals:
  - ...

## 4. Operation Contract

- Operation type: create | update | move | remove | split | converge | guard | migrate
- Primary archetype: <one archetype from the allowed list below>
- Allowed primary archetypes:
  - api-route-removal | api-contract-change | api-error-contract-centralization
  - route-architecture-convergence | api-adapter-boundary-convergence
  - legacy-facade-removal | field-contract-removal | namespace-convergence
  - ownership-routing-refactor | module-move | large-file-split
  - dead-code-removal | frontend-route-removal | runtime-contract-preservation
  - batch-migration | architecture-guard-hardening | registry-catalog-refactor
  - test-guard-hardening | service-boundary-refactor | custom
- Archetype reason: <why this archetype applies>
- Behavior change allowed: no | constrained | yes
- Behavior change constraints:
  - <what may change>
  - <what must not change>
- Deletion allowed: yes | no
- Replacement allowed: yes | no
- User decision required if: <condition>

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | <why runtime truth is required, or no with reason> |
| Baseline Snapshot | yes | <why before/after comparison is required, or no with reason> |
| Ownership Routing | yes | <why ownership classification is required, or no with reason> |
| Allowlist Exception | no | <why an allowlist register is required, or why no allowlist register is required> |
| Contract Shape | yes | <why exact API/DTO/error shape is required, or no with reason> |
| Batch Migration | no | <why batch migration is required, or no with reason> |
| Reintroduction Guard | yes | <why anti-regression guard is required, or no with reason> |
| Persistent Evidence | yes | <why persisted audit/snapshot evidence is required, or no with reason> |

## 4b. Runtime Source of Truth

Use active form when runtime behavior, route registration, config, generated
contracts, persistence, or architecture rules are affected:

- Primary source of truth:
  - `<app.openapi(), app.routes, AST guard, loaded config, DB schema, manifest>`
- Secondary evidence:
  - `<test, rg scan, snapshot, or static inspection>`
- Static scans alone are not sufficient for this story because:
  - `<why runtime/source-loaded evidence is required>`

Use N/A form only when no runtime source is affected:

- Runtime source of truth: not applicable
- Reason: <why no runtime route, config, generated contract, persistence, or
  architecture rule is affected>

## 4c. Baseline / Before-After Rule

Use active form when required:

- Baseline artifact before implementation:
  - `<path or command>`
- Comparison after implementation:
  - `<path or command>`
- Expected invariant:
  - `<allowed delta or preserved behavior>`

Use N/A form only when no baseline-triggering operation applies:

- Baseline / before-after rule: not applicable
- Reason: <why this story does not move, split, converge, migrate, or require
  baseline evidence>

## 4d. Ownership Routing Rule

Use active form when required:

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `<responsibility>` | `<canonical module/path>` | `<non-canonical path>` |

Use N/A form only when ownership is not required:

- Ownership routing: not applicable
- Reason: <why no responsibility moves or boundary rules are affected>

## 4e. Allowlist / Exception Register

Choose exactly one snippet:

- `templates/snippets/allowlist-exception-active.md`
- `templates/snippets/allowlist-exception-not-applicable.md`

## 4f. Contract Shape

Use active form when API, HTTP error, payload, DTO, OpenAPI, export, generated
client, or frontend type shape is affected:

- Contract type:
  - `<API route, payload, DTO, OpenAPI path, error envelope, export, type>`
- Fields:
  - `<field>`: `<type/value rule>`
- Required fields:
  - `<field>`
- Optional fields:
  - `<field or none>`
- Status codes:
  - `<status and condition>`
- Serialization names:
  - `<wire name rule>`
- Frontend type impact:
  - `<impact or none>`
- Generated contract impact:
  - `<OpenAPI/generated client/schema impact or none>`

Use N/A form only when no shape is affected:

- Contract shape: not applicable
- Reason: <why no API, error, payload, export, DTO, OpenAPI contract,
  generated client, or frontend type is affected>

## 4g. Batch Migration Plan

Choose exactly one snippet:

- `templates/snippets/batch-migration-active.md`
- `templates/snippets/batch-migration-not-applicable.md`

## 4h. Persistent Evidence Artifacts

Use active form when audit, snapshot, baseline, OpenAPI diff, route inventory,
mapping, allowlist, or exception-register evidence is required:

| Artifact | Path | Purpose |
|---|---|---|
| `<artifact name>` | `<path>` | `<why it must persist>` |

Use N/A form only when no persistent evidence is required:

- Persistent evidence artifacts: not applicable
- Reason: <why no audit, snapshot, baseline, OpenAPI diff, route inventory,
  migration mapping, allowlist register, or exception register is required>

## 4i. Reintroduction Guard

Choose exactly one snippet:

- `templates/snippets/reintroduction-guard-active.md`
- `templates/snippets/reintroduction-guard-not-applicable.md`

## 4j. Source Finding Closure

Use for every story.

For audit-sourced stories:

- Closure status: full-closure | phased-with-map | blocked | non-domain
- Source finding: `<audit path>#<finding-id>`
- Closure proof required: <before/after artifact, guard, test, scan>
- Known residual in-domain work: none | <explicit list>
- Deferred non-domain concerns: none | <explicit list>

For non-audit stories:

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `<relative/path.py>` - <what exists today>
- Evidence 2: `<relative/path.py>` - <what must change>
- Evidence N: `_condamad/stories/regression-guardrails.md` - shared regression
  invariants consulted before story scope was finalized.

If repository evidence was not available, state:

- Repository evidence: not available
- Assumption risk: <risk>

## 6. Target State

After implementation:

- ...
- ...
- ...

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Scope vector:
  - Operation: <operation type>
  - Domain: <domain>
  - Touched surfaces: <paths, routes, contracts>
  - Out-of-scope surfaces: <frontend, database, auth, i18n, etc.>
- Selection rule:
  - Applied only guardrails matching exact path, file surface, operation,
    contract, domain, or universal local guardrails.
- Applicable invariants:
  - `RG-XXX` - <why this invariant applies>
- Needs-investigation invariants:
  - none | `RG-YYY` - <exact overlap that must be checked before editing>
  - Registry gap: <missing exact invariant; do not update the registry unless
    this story is explicit registry-enrichment work>
- Non-applicable examples:
  - `RG-ZZZ` - <why this likely-confusing surface is out of scope>
- Required regression evidence:
  - <test, scan, snapshot, diff, audit, or runtime inventory>
- Allowed differences:
  - <explicit allowed differences, or "none">

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | ... | Evidence profile: `<validator-known-profile>`; `pytest -q <test path>` or `python -c "<assertion>"` |
| AC2 | ... | Evidence profile: `<validator-known-profile>`; `rg -n "<exact token>" <bounded paths>` or `Manual check: <scope> verifies <expected result>` |

AC evidence must include a validator-recognized token: `pytest`, `python`,
`ruff`, `rg`, `npm`, `pnpm`, `vitest`, `eslint`, `tsc`, an explicit test path,
or `Manual check:`. Do not use `Test-Path`, `Get-Content`, an artifact path
alone, or `Evidence profile: persistent_evidence` as AC evidence.

## 8. Implementation Tasks

- [ ] Task 1 - <action> (AC: AC1)
  - [ ] Subtask 1.1 - <specific step>
  - [ ] Subtask 1.2 - <specific step>

- [ ] Task 2 - <action> (AC: AC2)
  - [ ] Subtask 2.1 - <specific step>

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `<existing module/class/function>` for <purpose>
- Do not recreate:
  - ...
- Shared abstraction allowed only if:
  - ...

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `<path or import>`
- `<symbol>`

## 11. Removal Classification Rules

Use this section only when `Operation type: remove` or the archetype is a
removal archetype. Otherwise write:

- Removal classification: not applicable

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Use this section only when `Operation type: remove` or the archetype is a
removal archetype. Otherwise write:

- Removal audit: not applicable

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/<story-key>/route-consumption-audit.md`

## 13. Canonical Ownership

Use this section when the story mentions canonical routes, canonical endpoints,
canonical namespaces, or removal. Otherwise write:

- Canonical ownership: not applicable

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| ... | ... | ... |

## 14. Delete-Only Rule

Use this section only when deletion is allowed. Otherwise write:

- Delete-only rule: not applicable

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

Use this section only when deletion is allowed. Otherwise write:

- External usage blocker: not applicable

If an item is classified as `external-active`, it must not be deleted. The dev
agent must stop or record an explicit user decision with external evidence and
deletion risk.

## 17. Generated Contract Check

Use this section when generated contracts exist or the archetype affects API
surfaces. Otherwise write:

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

Required generated-contract evidence:

- OpenAPI path absence
- generated client/schema absence
- route manifest absence

## 18. Files to Inspect First

Codex must inspect before editing:

- `<relative/path>`
- `<relative/path>`

## 19. Expected Files to Modify

Likely files:

- `<relative/path>` - <expected change>

Likely tests:

- `<relative/test_path>` - <expected coverage>

Files not expected to change:

- `<relative/path>` - <reason>
- If unknown until repo inspection: `unknown until repo inspection` - assumption risk: <why unchanged files cannot be named yet>

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```bash
<targeted tests>
<architecture guard tests>
<lint/type checks>
<negative rg scans>
```

## 22. Regression Risks

- Risk: ...
  - Guardrail: ...
- Risk: ...
  - Guardrail: ...

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- `<source>` - <why relevant>
