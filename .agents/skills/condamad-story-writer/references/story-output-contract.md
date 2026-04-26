# Story Output Contract

<!-- Contrat de structure obligatoire pour une story CONDAMAD. -->

## Required Status

Use:

```text
Status: ready-for-dev
```

Only use `ready-for-dev` when the story passes `condamad_story_validate.py`.

## Required Base Sections

Every story must include these sections:

1. Objective
2. Trigger / Source
3. Domain Boundary
4. Operation Contract
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

## Conditional Removal Sections

Removal stories must also include:

1. Removal Classification Rules
2. Removal Audit Format
3. Canonical Ownership
4. Delete-Only Rule
5. External Usage Blocker
6. Reintroduction Guard
7. Generated Contract Check

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
- `Behavior change allowed: yes | no`
- `Deletion allowed: yes | no`
- `Replacement allowed: yes | no`
- `User decision required if: <condition>`

The primary archetype must come from `references/story-archetypes.md` unless it
is `custom`, in which case the story must explain why no supported archetype
fits and add explicit validation rules.

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
