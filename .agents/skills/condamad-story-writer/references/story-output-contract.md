# Story Output Contract

<!-- Contrat de structure obligatoire pour une story CONDAMAD. -->

## Required Story Number

Each story must have a stable sequential story number:

```text
# Story CS-### <story-key>: <title>
```

The number comes from `_condamad/stories/story-status.md`. New numbers are
allocated by incrementing the highest existing `CS-###` row. Existing numbers
must never be reused or changed.

## Required Status

Use:

```text
Status: ready-to-dev
```

Allowed statuses are:

- `ready-to-dev`
- `ready-to-review`
- `done`

Only use `ready-to-dev` when the story passes `condamad_story_validate.py`.
Only use `ready-to-review` when implementation evidence exists. Only use
`done` when review evidence exists.

## Required Tracking Document

Every story creation or status transition must update:

```text
_condamad/stories/story-status.md
```

Required table columns:

| Story ID | Story key | Title | Status | Path | Source | Last update |
|---|---|---|---|---|---|---|

`Status` must be one of `ready-to-dev`, `ready-to-review`, or `done`.
`Last update` must use ISO date format `YYYY-MM-DD`.

## Required Base Sections

Every story must include these sections:

1. Objective
2. Trigger / Source
3. Domain Boundary
4. Operation Contract
4a. Required Contracts
5. Current State Evidence
6. Target State
7. Acceptance Criteria
8. Implementation Tasks
9. Mandatory Reuse / DRY Constraints
10. No Legacy / Forbidden Paths
11. Files to Inspect First
12. Expected Files to Modify
13. Dependency Policy
14. Validation Plan
15. Regression Risks
16. Dev Agent Instructions
17. References

## Conditional Transverse Sections

Stories must include the section when the selected archetype or story scope
activates the matching contract:

- Runtime Source of Truth
- Baseline / Before-After Rule
- Ownership Routing Rule
- Allowlist / Exception Register
- Contract Shape
- Batch Migration Plan
- Reintroduction Guard
- Persistent Evidence Artifacts

When a conditional section is not active, the story may mark it `not applicable`
with a concrete reason.

The template keeps conditional sections as headings. The final story must inline
exactly one matching active or not-applicable snippet from `templates/snippets/`
for each conditional transverse section.

`Reintroduction Guard` is a transverse contract. It is required for removal
stories when the selected archetype activates it, but it is not removal-only.

## Conditional Removal Sections

Removal stories must also include:

1. Removal Classification Rules
2. Removal Audit Format
3. Canonical Ownership
4. Delete-Only Rule
5. External Usage Blocker
6. Generated Contract Check

Numbering is recommended. The validator accepts equivalent markdown headings
with the same titles.

## Language Contract

Contract headings and required markers must remain in English:

- `Objective`
- `Domain Boundary`
- `Current State Evidence`
- `Acceptance Criteria`
- `Validation evidence required`
- `Operation Contract`
- `Dependency Policy`

Business content may be written in French when useful, but the structural
contract remains English-only for deterministic validation.

## Required Boundary Fields

The Domain Boundary section must include:

- exactly one `Domain:`;
- `In scope:`;
- `Out of scope:`;
- `Explicit non-goals:`.

## Operation Contract

The Operation Contract section must include:

- `Operation type: create | update | move | remove | split | converge | guard | migrate`
- `Primary archetype: <supported archetype>`
- `Archetype reason: <why this archetype applies>`
- `Behavior change allowed: no | constrained | yes`
- `Behavior change constraints:` when behavior change is `constrained` or `yes`
- `Deletion allowed: yes | no`
- `Replacement allowed: yes | no`
- `User decision required if: <condition>`

The primary archetype must come from `references/story-archetypes.md` unless it
is `custom`, in which case the story must explain why no supported archetype
fits and add explicit validation rules.

## Required Contracts

The Required Contracts section must include this table:

| Contract | Required | Reason |
|---|---:|---|

`Required` must be `yes` or `no`. Contracts required by
`references/story-archetypes.md` must be listed as `yes` unless the archetype is
`custom`, in which case the story must explain its selected contracts.

The table must list every known contract exactly once:

- Runtime Source of Truth
- Baseline Snapshot
- Ownership Routing
- Allowlist Exception
- Contract Shape
- Batch Migration
- Reintroduction Guard
- Persistent Evidence

Unknown contract names and duplicate rows are invalid.

When a contract is marked `yes`, the matching section must be active. When a
contract is marked `no`, the matching section must be `not applicable` and must
include a `Reason`.

## Contract Shape

When active, the Contract Shape section must include:

- `Contract type:`
- `Fields:`
- `Required fields:`
- `Optional fields:`
- `Status codes:`
- `Serialization names:`
- `Frontend type impact:`
- `Generated contract impact:`

## Batch Migration Plan

When active, the Batch Migration Plan section must include:

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|

## Expected File Fields

The story must distinguish:

- files Codex must inspect before editing;
- likely files to modify;
- likely tests;
- files not expected to change.

If a file cannot be known from evidence, mark it as an assumption instead of
inventing certainty.

Each `Expected Files to Modify` block must contain at least one concrete path in
backticks, or the phrase `unknown until repo inspection` plus an `assumption
risk`.

A concrete path must contain `/` or `\`, or end with a known file extension such
as `.py`, `.ts`, `.tsx`, `.md`, `.yaml`, `.sql`, `.css`, `.scss`, `.json`, or
`.toml`.

## Dependency Policy

The story must include:

```md
## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
```

If new dependencies are allowed, they must be listed with a concrete
justification:

```md
- New dependencies: package-name
- Justification: explain why no existing project dependency or standard library path is sufficient.
```

## Anti-Drift Guardrails

The Dev Agent Instructions section must explicitly forbid:

- broadening the story to adjacent domains;
- unrelated cleanup;
- new dependencies unless explicitly listed;
- task completion without validation evidence;
- preserving legacy behavior for convenience;
- continuing silently when an AC cannot be satisfied.
