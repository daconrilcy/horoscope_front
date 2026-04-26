# Story <story-key>: <title>

Status: ready-for-dev

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
- Primary archetype: api-route-removal | legacy-facade-removal | field-contract-removal | namespace-convergence | module-move | large-file-split | dead-code-removal | frontend-route-removal | test-guard-hardening | service-boundary-refactor | custom
- Archetype reason: <why this archetype applies>
- Behavior change allowed: yes | no
- Deletion allowed: yes | no
- Replacement allowed: yes | no
- User decision required if: <condition>

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `<relative/path.py>` - <what exists today>
- Evidence 2: `<relative/path.py>` - <what must change>

If repository evidence was not available, state:

- Repository evidence: not available
- Assumption risk: <risk>

## 6. Target State

After implementation:

- ...
- ...
- ...

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | ... | Evidence profile: `<profile>`; command / test / guard |
| AC2 | ... | Evidence profile: `<profile>`; command / test / guard |

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

## 16. Reintroduction Guard

Use this section for No Legacy removal stories. Otherwise write:

- Reintroduction guard: not applicable

The implementation must add or update an architecture guard that fails if the
removed surface is reintroduced.

The guard must check at least one deterministic source:

- registered router prefixes
- importable Python modules
- frontend route table
- generated OpenAPI paths
- forbidden symbols or states

Required forbidden examples:

- `<removed route prefix>`
- `<removed import path>`
- `<removed frontend route>`
- `<removed legacy field>`

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

## 24. References

- `<source>` - <why relevant>
