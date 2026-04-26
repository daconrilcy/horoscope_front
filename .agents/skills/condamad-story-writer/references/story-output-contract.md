# Story Output Contract

<!-- Contrat de structure obligatoire pour une story CONDAMAD. -->

## Required Status

Use:

```text
Status: ready-for-dev
```

Only use `ready-for-dev` when the story passes `condamad_story_validate.py`.

## Required Sections

The story must include these sections:

1. Objective
2. Trigger / Source
3. Domain Boundary
4. Current State Evidence
5. Target State
6. Acceptance Criteria
7. Implementation Tasks
8. Mandatory Reuse / DRY Constraints
9. No Legacy / Forbidden Paths
10. Files to Inspect First
11. Expected Files to Modify
12. Dependency Policy
13. Validation Plan
14. Regression Risks
15. Dev Agent Instructions
16. References

Numbering is recommended. The validator accepts equivalent markdown headings
with the same titles.

## Language Contract

Contract headings and required markers must remain in English:

- `Objective`
- `Domain Boundary`
- `Current State Evidence`
- `Acceptance Criteria`
- `Validation evidence required`
- `Dependency Policy`

Business content may be written in French when useful, but the structural
contract remains English-only for deterministic validation.

## Required Boundary Fields

The Domain Boundary section must include:

- exactly one `Domain:`;
- `In scope:`;
- `Out of scope:`;
- `Explicit non-goals:`.

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
