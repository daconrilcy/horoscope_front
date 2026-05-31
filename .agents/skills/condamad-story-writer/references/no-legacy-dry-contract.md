# No Legacy / DRY Contract

<!-- Regles DRY et No Legacy partagees par les skills CONDAMAD. -->

## DRY

Prefer one canonical implementation per responsibility.

Before allowing a new abstraction, the story must identify:

- the duplicated responsibility it removes;
- the concrete consumers that will reuse it;
- why an existing module cannot serve the same role.

Do not create speculative shared utilities.

## No Legacy

Forbidden unless explicitly approved by the story:

- compatibility wrappers;
- transitional aliases;
- legacy imports;
- duplicate active implementations;
- silent fallback behavior;
- root-level service when a canonical namespace exists;
- preserving old path through re-export;
- tests that encode legacy behavior as nominal behavior.

## Required Story Content

The story must include:

- mandatory reuse targets, when known;
- specific forbidden symbols or paths, when known;
- negative searches or architecture guards when legacy risk exists;
- an explicit statement when no new dependency is allowed.

